# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Instrument monitor that generates an HTML page."""

import functools
import operator
import urllib.request
from cgitb import html
from threading import RLock
from time import sleep, time as currenttime

import numpy
from lttb import lttb

from nicos.core import Param
from nicos.core.constants import NOT_AVAILABLE
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, WARN
from nicos.services.monitor import Monitor as BaseMonitor
from nicos.services.monitor.icon import nicos_icon
from nicos.utils import checkSetupSpec, parseKeyExpression, number_types, \
    safeWriteFile

from .chartjs import DEFAULT_BLACK, DEFAULT_BLUE, DEFAULT_GREEN, DEFAULT_RED, \
    ScatterChart

HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="%(intv)s">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>%(title)s</title>

    <link href="vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">
    <link href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i" rel="stylesheet">
    <link href="css/sb-admin-2.min.css?new" rel="stylesheet">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,%(icon)s">
    <script src="https://cdn.jsdelivr.net/npm/chart.js/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
</head>
<body id="page-top">
    <div id="wrapper">
        <div id="content-wrapper" class="d-flex flex-column">
            <div id="content">
                <div class="container-fluid">
"""
FOOT = """\
                </div>
            </div>
            <footer class="sticky-footer bg-white">
                <div class="container my-auto">
                    <div class="copyright text-center my-auto">
                        <span>%(text)s</span>
                    </div>
                </div>
            </footer>
        </div>
    </div>
    <a class="scroll-to-top rounded" href="#page-top">
        <i class="fas fa-angle-up"></i>
    </a>

    <!-- Bootstrap core JavaScript-->
    <script src="vendor/jquery/jquery.min.js"></script>
    <script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
    <!-- Core plugin JavaScript-->
    <script src="vendor/jquery-easing/jquery.easing.min.js"></script>
    <!-- Custom scripts for all pages-->
    <script src="js/sb-admin-2.min.js"></script>
</body>
</html>
"""


class Field:
    # what to display
    key = ''         # main key (displayed value)
    item = -1        # item to display of value, -1 means whole value
    name = ''        # name of value
    statuskey = ''   # key for value status
    unitkey = ''     # key for value unit
    formatkey = ''   # key for value format string
    fixedkey = ''    # key for value fixed-ness
    offset = None    # for value scaling

    # how to display it
    width = 8        # width of the widget (in characters, usually)
    height = 8       # height of the widget
    istext = False   # true if not a number but plain text
    min = None       # minimum value
    max = None       # maximum value; if out of range display in red
    warnmin = None   # minimum value
    warnmax = None   # maximum value; if out of range display in orange

    # current values
    value = ''       # current value
    fixed = ''       # current fixed status
    unit = ''        # unit for display
    format = '%s'    # format string for display
    statustext = ''  # status info

    # for layout change
    big = False

    # for plots
    plot = None           # which plot to plot this value in
    plotwindow = 3600     # time span of plot
    secondaxes = False    # if to show on separate second axes

    # for pictures
    picture = None   # file name

    # for rolling external html
    roll = None

    # conditional hiding
    setups = None    # setupspec for which should be shown (None = always)
    enabled = True   # if the field is currently shown

    def __init__(self, prefix, desc):
        if isinstance(desc, str):
            desc = {'dev': desc}
        else:
            desc = desc._options
        if 'dev' in desc:
            dev = desc.pop('dev')
            if 'name' not in desc:
                desc['name'] = dev
            dev, indices, scale, offset = parseKeyExpression(
                dev, False, normalize=lambda s: s.lower()
            )
            if indices:
                desc['item'] = indices
            desc['key'] = prefix + dev + '/value'
            desc['statuskey'] = prefix + dev + '/status'
            desc['fixedkey'] = prefix + dev + '/fixed'
            if scale:
                desc['scale'] = scale
            if offset:
                desc['offset'] = offset
            if 'unit' not in desc:
                desc['unitkey'] = prefix + dev + '/unit'
            else:
                pass
            if 'format' not in desc:
                desc['formatkey'] = prefix + dev + '/fmtstr'
        elif 'key' in desc:
            key, indices, scale, offset = parseKeyExpression(desc['key'], False)
            if scale:
                desc['scale'] = scale
            if offset:
                desc['offset'] = offset
            if indices:
                desc['item'] = indices
            if 'name' not in desc:
                desc['name'] = desc['key']
            desc['key'] = prefix + key
            for kn in ('statuskey', 'fixedkey', 'unitkey', 'formatkey'):
                if kn in desc:
                    desc[kn] = (prefix + desc[kn]).lower().replace('.', '/')
        self.__dict__.update(desc)

    def updateKeymap(self, keymap):
        # store reference from key to field for updates
        for kn in ('key', 'statuskey', 'fixedkey', 'unitkey', 'formatkey'):
            key = getattr(self, kn)
            if key:
                keymap.setdefault(key, []).append(self)


class Static(str):
    def getHTML(self):
        return self


class Block:
    def __init__(self, config):
        self.enabled = True
        self._content = []
        self.setups = config.get('setups')
        self._onlyfields = []

    def __iadd__(self, content):
        """Easily adds content to the block using ``+=``."""
        if isinstance(content, str):
            self._content.append(Static(content))
        else:
            self._content.append(content)
        return self

    def getHTML(self):
        if self.enabled and self._content:
            return ''.join(c.getHTML() for c in self._content)
        return ''


class Label:
    def __init__(
        self,
        cls='label',
        width=0,
        text='&nbsp;',
        fore='inherit',
        back='inherit',
        style='',
    ):
        self.cls = cls
        self.width = width
        self.text = text
        self.fore = fore
        self.back = back
        self.style = style
        self.enabled = True

    def getHTML(self):
        if not self.enabled:
            return ''
        if self.cls == 'value':
            return f'<div class="valuebadge badge-{self.style}">{self.text}</div>'
        return (
            '<div class="%s" style="color: %s; min-width: %sex; '
            'background-color: %s">%s</div>'
            % (self.cls, self.fore, self.width, self.back, self.text)
        )


class Card:
    def __init__(self, text='', header='', style='primary'):
        self.text = text
        self.header = header
        self.style = style
        self.enabled = True

    def getHTML(self):
        if not self.enabled or not self.text:
            return ''
        text = ''
        if self.text:
            text = f'<div class="text-white-50 small">{self.text}</div>'
        html = (
            f'<div class="card bg-{self.style} text-white shadow">'
            f'<div class="card-body">{self.header}'
            f'{text}</div></div>'
        )
        return html


DATEFMT = '%Y-%m-%d'
TIMEFMT = '%H:%M:%S'


class PlotCurve:
    COUNT = 0

    def __init__(self, x, y, linetype=DEFAULT_BLUE, legend=None, secondaxis=False):
        self.secondaxis = secondaxis
        self._x, self._y = x, y
        self._linetype = (linetype,)
        self._legend = legend
        PlotCurve.COUNT += 1
        self._id = PlotCurve.COUNT
        if legend is None:
            self._legend = 'curve %d' % self._id

    @property
    def legend(self):
        """Get current text for a legend."""
        return self._legend

    @legend.setter
    def legend(self, s):
        self._legend = s

    @property
    def x(self):
        """Get the current list/ndarray of x values."""
        return self._x

    @x.setter
    def x(self, lst):
        self._x = lst

    @property
    def y(self):
        """Get the current list/ndarray of y values."""
        return self._y

    @y.setter
    def y(self, lst):
        self._y = lst

    @property
    def data(self):
        """Get xy data."""
        data = []
        for x, y in zip(self._x, self._y):
            data.append({'x': x * 1000, 'y': y})
        return data


class Plot:
    # if the field should be displayed
    enabled = True

    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.data = []
        self.lock = RLock()
        # self.plot = pygr.Plot(viewport=(.1, .95, .25, .95))
        # self.axes = NicosTimePlotAxes(self.plot._viewport)
        # self.plot.addAxes(self.axes)
        # self.plot.setLegend(True)
        # self.plot.setLegendWidth(0.07)
        # self.plot.offsetXLabel = -.2
        # self.axes.setXtickCallback(self.xtickCallBack)
        self.curves = []

    def addcurve(self, name, secondaxis=False):
        self.curves.append(
            PlotCurve([currenttime()], [0], legend=name, secondaxis=secondaxis)
        )
        # self.axes.addCurves(self.curves[-1])
        self.data.append([[], []])
        return len(self.curves) - 1

    def updatevalues(self, curve, x, y):
        # we have to guard modifications to self.data, since otherwise the
        # __str__ method below may see inconsistent X and Y lists
        with self.lock:
            ts, yy = self.data[curve]
            ts.append(x)
            yy.append(y)
            i = 0
            ll = len(ts)
            limit = currenttime() - self.window
            while i < ll and ts[i] < limit:
                i += 1
            self.data[curve][:] = [ts[i:], yy[i:]]

    def maybeDownsamplePlotdata(self, data):
        if len(data[0]) > self.width:
            temp = numpy.array(data).T
            down = lttb.downsample(temp[temp[:, 0].argsort()], n_out=self.width)
            data = down[:, 0], down[:, 1]
        return data

    def getHTML(self):
        from itertools import cycle

        if not self.enabled:
            return ''
        if not self.data or not self.curves:
            return '<span>No data or curves found</span>'
        with self.lock:
            for i, (d, c) in enumerate(zip(self.data, self.curves)):
                try:
                    # add a point "current value" at "right now" to avoid curves
                    # not updating if the value doesn't change
                    now = currenttime()
                    if d[0][-1] < now - 10:
                        self.updatevalues(i, now, d[1][-1])
                    c.x, c.y = self.maybeDownsamplePlotdata(d)
                except IndexError:
                    # no data (yet)
                    pass
        # c = self.axes.getCurves()
        # self.axes.setWindow(c.xmin, c.xmax, c.ymin, c.ymax)
        # render plot
        x = ScatterChart()
        cc = cycle([DEFAULT_GREEN, DEFAULT_RED, DEFAULT_BLUE, DEFAULT_BLACK])
        for c in self.curves:
            opt = next(cc).copy()
            if c.secondaxis:
                opt['yAxisID'] = 'y1'
                x.secondaxis = True
            x.add_line(c.legend, c.data, options=opt)

        return x.build_chart()

        return (
            '<img src="data:image/svg+xml;base64,%s" '
            'style="width: %sex; height: %sex">' % ('', self.width, self.height)
        )


class Roll:
    # if the field should be displayed
    enabled = True

    def __init__(self, url, name):
        self.url = url
        self.name = name

    def getHTML(self):
        s = ''
        if not self.enabled:
            return s
        content = urllib.request.urlopen(self.url).read().decode('utf-8')
        s = f"""
    <div>
      <div class="row marquee">
        <div class="col-12">
          <div class="block m-0 p-0 p-3">
            <div class="part m-0 p-0 pb-4" aria-hidden="true">{content}</div>
            <div class="part m-0 p-0 pb-4" aria-hidden="true">{content}</div>
            <div class="part m-0 p-0">{content}</div>
          </div>
        </div>
      </div>
    </div>
        """
        return s


class Picture:
    # if the field should be displayed
    enabled = True

    def __init__(self, filepath, width, height, name):
        self.filepath = filepath
        self.width = width
        self.height = height
        self.name = name

    def getHTML(self):
        s = ''
        if not self.enabled:
            return s
        if self.name:
            s += '<div class="label">%s</div><br>' % self.name
        s += '<img src="%s" style="width: %sex; height: %sex">' % (
            self.filepath,
            self.width,
            self.height,
        )
        return s


class BigField:
    # if the field should be displayed
    enabled = True

    def __init__(self, field):
        self.nlabel = field._namelabel
        self.vlabel = field._valuelabel
        self.f = field

    def getHTML(self):
        s = ''
        if not self.enabled:
            return s
        code = f"""
    <div class="card bg-{self.vlabel.style} text-white shadow">
        <div class="card-body">
            {self.nlabel.text}: {self.vlabel.text} {self.f.unit}
            <div class="text-white-50 small">{self.f.statustext}</div>
        </div>
    </div>"""
        return code


class Monitor(BaseMonitor):
    """HTML specific implementation of instrument monitor."""

    parameters = {
        'filename': Param('Filename for HTML output', type=str, mandatory=True),
        'interval': Param('Interval for writing file', default=5),
        'noexpired': Param('If true, show expired values as "n/a"', type=bool),
    }

    def mainLoop(self):
        while not self._stoprequest:
            try:
                if self._content:
                    content = ''.join(ct.getHTML() for ct in self._content)
                    safeWriteFile(self.filename, content, maxbackups=0)
            except Exception:
                self.log.error('could not write status to %r', self.filename, exc=1)
            else:
                self.log.debug('wrote status to %r', self.filename)
            sleep(self.interval)

    def closeGui(self):
        pass

    def __iadd__(self, content):
        if isinstance(content, str):
            self._content.append(Static(content))
        else:
            self._content.append(content)
        return self

    def initGui(self):
        self._content = []
        self._bgcolor = 'inherit'
        self._black = 'black'
        self._yellow = 'yellow'
        self._green = '#00ff00'
        self._red = 'red'
        self._gray = 'gray'
        self._white = 'white'
        self._orange = '#ffa500'

        headprops = dict(
            fs=self._fontsize,
            fst=self._timefontsize,
            fsb=self._fontsizebig,
            ff=self.font,
            ffm=self.valuefont or self.font,
            intv=self.interval,
            # pylint: disable=deprecated-method
            title=html.escape(self.title),
            icon=nicos_icon,
        )
        footprops = dict(
            text='Data provided by MGML',
        )

        self += HEAD % headprops

        # header
        self += '<div class="d-sm-flex align-items-center justify-content-between mb-2"><h1 class="h3 mb-0 text-gray-800">'
        self._timelabel = Label('timelabel')
        self += self._timelabel
        self += '</h1><img src="mgml-logo.png"></div><div>'
        self._warnlabel = Card(style='danger', text='', header='Warning')
        self += self._warnlabel
        self += '</div>\n'

        self._plots = {}

        def _create_field(blk, config):
            if 'widget' in config or 'gui' in config:
                self.log.warning(
                    'ignoring "widget" or "gui" element in HTML '
                    'monitor configuration'
                )
                return None
            field = Field(self._prefix, config)
            field.updateKeymap(self._keymap)

            if field.plot:
                p = self._plots.get(field.plot)
                if not p:
                    p = Plot(field.plotwindow, field.width, field.height)
                    self._plots[field.plot] = p
                    blk += p
                field._plotcurve = p.addcurve(field.name, field.secondaxes)
            elif field.picture:
                # pylint: disable=deprecated-method
                pic = Picture(
                    field.picture, field.width, field.height, html.escape(field.name)
                )
                blk += pic
            elif field.roll:
                # pylint: disable=deprecated-method
                rollcode = Roll(field.roll, html.escape(field.name))
                blk += rollcode
            elif field.big:
                # deactivate plots
                field.plot = None
                # create name label
                # pylint: disable=deprecated-method
                field._namelabel = Label('name', field.width, html.escape(field.name))
                field._valuelabel = Label('', fore='white')
                # blk += vlabel
                blk += BigField(field)
            else:
                # deactivate plots
                field.plot = None
                # create name label
                # pylint: disable=deprecated-method
                flabel = field._namelabel = Label(
                    'name', field.width, html.escape(field.name)
                )
                blk += flabel
                blk += '</td></tr><tr><td>'
                # create value label
                cls = 'value'
                if field.istext:
                    cls += ' istext'
                vlabel = field._valuelabel = Label(cls, fore='white')
                blk += vlabel
            return field

        # rows
        for superrow in self.layout:
            self += '<div class="row">\n'
            # determine width
            cols = len(superrow)
            if cols > 4:
                colstyle = 'col-xl-2 col-lg-3 col-md-4'
            elif cols == 4:
                colstyle = 'col-lg-3 col-md-6'
            elif cols == 3:
                colstyle = 'col-lg-4 col-md-6'
            elif cols == 2:
                colstyle = 'col-lg-6'
            else:
                colstyle = 'col-12'
            for column in superrow:
                self += f'  <div class="{colstyle} mb-2">'
                for block in column:
                    block = self._resolve_block(block)
                    blk = Block(block._options)
                    blk += '<div class="card shadow mb-3">'
                    # pylint: disable=deprecated-method
                    blk += (
                        f'<div class="card-header py-3">'
                        f'    <h6 class="m-0 font-weight-bold text-primary">{html.escape(block._title)}</h6>'
                        f'</div>'
                    )
                    for row in block:
                        if row is not None:
                            # normal row
                            blk += '<div class="row">\n'
                            for field in row:
                                blk += '<div class="col mx-3 my-1">'
                                f = _create_field(blk, field)
                                if f and f.setups:
                                    if blk.setups:
                                        blk._onlyfields.append(f)
                                    else:
                                        self._onlyfields.append(f)
                                blk += '</div>\n'
                            blk += '</div>\n'
                    blk += '</div>\n'
                    self += blk
                    if blk.setups:
                        self._onlyblocks.append(blk)
                self += '</div>\n'
            self += '</div>'

        self += FOOT % footprops

    def updateTitle(self, text):
        self._timelabel.text = text

    def signalKeyChange(self, field, key, value, time, expired):
        if field.plot:
            if key == field.key and value is not None:
                self._plots[field.plot].updatevalues(
                    field._plotcurve, time, value * field.scale
                )
            return
        if key == field.key:
            # apply item selection
            field.value = value
            if value is not None:
                if isinstance(field.item, tuple):
                    try:
                        fvalue = functools.reduce(operator.getitem, field.item, value)
                    except Exception:
                        fvalue = NOT_AVAILABLE
                elif field.item >= 0:
                    try:
                        fvalue = value[field.item]
                    except Exception:
                        fvalue = NOT_AVAILABLE
                else:
                    fvalue = value
            else:
                fvalue = value
            # default style
            field._namelabel.back = self._bgcolor
            field._valuelabel.style = 'dark'
            if isinstance(fvalue, number_types):
                if field.scale:
                    fvalue *= field.scale
                if field.offset:
                    fvalue += field.offset
                if field.min is not None and fvalue < field.min:
                    field._namelabel.back = self._red
                    field._valuelabel.style = 'danger'
                elif field.max is not None and fvalue > field.max:
                    field._namelabel.back = self._red
                    field._valuelabel.style = 'danger'
                elif field.warnmin is not None and fvalue < field.warnmin:
                    field._namelabel.back = self._red
                    field._valuelabel.style = 'warning'
                elif field.warnmax is not None and fvalue > field.warnmax:
                    field._namelabel.back = self._red
                    field._valuelabel.style = 'warning'
            if expired:
                field._valuelabel.back = self._gray
                # field._valuelabel.style = 'secondary'
                if self.noexpired:
                    fvalue = 'n/a'
            else:
                field._valuelabel.back = self._black
                # field._valuelabel.style = 'dark'
            if fvalue is None:
                strvalue = '----'
            else:
                if isinstance(fvalue, list):
                    fvalue = tuple(fvalue)
                try:
                    strvalue = field.format % fvalue
                except Exception:
                    strvalue = str(fvalue)
            field._valuelabel.text = strvalue or '&nbsp;'
        elif key == field.statuskey:
            if value is not None:
                status = value[0]
                field.statustext = value[1]
                if status == OK:
                    field._valuelabel.fore = self._green
                elif status == WARN:
                    field._valuelabel.fore = self._orange
                    field._valuelabel.style = 'warning'
                elif status == BUSY:
                    field._valuelabel.fore = self._yellow
                elif status in (ERROR, NOTREACHED):
                    field._valuelabel.fore = self._red
                elif status == DISABLED:
                    field._valuelabel.fore = self._white
                else:
                    field._valuelabel.fore = self._white
        elif key == field.unitkey:
            if value is not None:
                field.unit = value
                field._namelabel.text = self._labelunittext(
                    field.name, field.unit, field.fixed
                )
        elif key == field.fixedkey:
            field.fixed = value and ' (F)' or ''
            field._namelabel.text = self._labelunittext(
                field.name, field.unit, field.fixed
            )
        elif key == field.formatkey:
            if value is not None:
                field.format = value
                self.signalKeyChange(field, field.key, field.value, 0, False)

    def _labelunittext(self, text, unit, fixed):
        # pylint: disable=deprecated-method
        return (
            f'{html.escape(text)} <span class="unit">({html.escape(unit)})</span>'
            f'<span class="fixed">{fixed}</span> '
        )

    def switchWarnPanel(self, on):
        if on:
            # pylint: disable=deprecated-method
            self._warnlabel.text = html.escape(self._currwarnings)
        else:
            self._warnlabel.text = ''

    def reconfigureBoxes(self):
        fields = []
        for block in self._onlyblocks:
            block.enabled = checkSetupSpec(block.setups, self._setups,
                                           log=self.log)
            # check fields inside the block, if the block isn't invisible
            if block.enabled:
                fields.extend(block._onlyfields)
        # always check fields not in a setup controlled group
        fields.extend(self._onlyfields)
        for field in fields:
            field.enabled = checkSetupSpec(field.setups, self._setups,
                                           log=self.log)
            if hasattr(field, '_namelabel'):
                field._namelabel.enabled = field.enabled
            if hasattr(field, '_valuelabel'):
                field._valuelabel.enabled = field.enabled
