#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Instrument monitor that generates an HTML page."""

from cgi import escape
from time import sleep, time as currenttime
from binascii import b2a_base64
from datetime import datetime
from threading import RLock

try:
    import matplotlib
    matplotlib.use('agg')
    matplotlib.rc('font', family='Helvetica')
    import matplotlib.pyplot as mpl
    import matplotlib.dates as mpldate
except ImportError:
    matplotlib = None

from nicos.core import Param
from nicos.core.status import OK, WARN, BUSY, ERROR, NOTREACHED
from nicos.services.monitor import Monitor as BaseMonitor
from nicos.pycompat import BytesIO, iteritems, from_utf8, string_types
from nicos.services.monitor.icon import nicos_icon
from nicos.guisupport.utils import checkSetupSpec


HEAD = '''\
<html>
<head>
<meta http-equiv="refresh" content="%(intv)s">
<link rel="shortcut icon" type="image/png" href="data:image/png;base64,%(icon)s">
<style type="text/css">
body { background-color: #e0e0e0;
       font-family: '%(ff)s', sans-serif; font-size: %(fs)spx; }
table { font-family: inherit; font-size: 100%%; }
.center { text-align: center; }
.time { text-align: center; font-size: %(fst)s; }
.timelabel { margin: 0.1em; padding: 0.2em; }
.column { display: inline-block; vertical-align: middle; }
.blockhead { font-size: %(fsb)spx; text-align: center; font-weight: bold; }
.block { border: 2px outset #e0e0e0; padding: .5em; margin: .3em; }
.blocktable { width: 100%%; }
.blocktable > tr { width: 100%%; }
.field { display: inline-block; }
.field td  { text-align: center; }
.value { font-family: '%(ffm)s', monospace;
         padding: .15em; border: 2px inset #e0e0e0; }
.istext { font-family: '%(ff)s', sans-serif !important; }
.unit   { color: #888888; }
.fixed  { color: #0000ff; }
.warnings { font-size: 120%%; }
</style>
<title>%(title)s</title>
</head>
<body>
'''


class Field(object):
    # what to display
    key = ''         # main key (displayed value)
    item = -1        # item to display of value, -1 means whole value
    name = ''        # name of value
    statuskey = ''   # key for value status
    unitkey = ''     # key for value unit
    formatkey = ''   # key for value format string
    fixedkey = ''    # key for value fixed-ness

    # how to display it
    width = 8        # width of the widget (in characters, usually)
    height = 8       # height of the widget
    istext = False   # true if not a number but plain text
    min = None       # minimum value
    max = None       # maximum value; if out of range display in red

    # current values
    value = ''       # current value
    fixed = ''       # current fixed status
    unit = ''        # unit for display
    format = '%s'    # format string for display

    # for plots
    plot = None           # which plot to plot this value in
    plotwindow = 3600     # time span of plot

    # for pictures
    picture = None   # file name

    def __init__(self, prefix, desc):
        if isinstance(desc, string_types):
            desc = {'dev': desc}
        if 'dev' in desc:
            dev = desc.pop('dev')
            if 'name' not in desc:
                desc['name'] = dev
            desc['key'] =       dev + '/value'
            desc['statuskey'] = dev + '/status'
            desc['fixedkey'] =  dev + '/fixed'
            if 'unit' not in desc:
                desc['unitkey'] = dev + '/unit'
            if 'format' not in desc:
                desc['formatkey'] = dev + '/fmtstr'
        for kn in ('key', 'statuskey', 'fixedkey', 'unitkey', 'formatkey'):
            if kn in desc:
                desc[kn] = (prefix + desc[kn]).replace('.', '/').lower()
        if 'name' not in desc and 'key' in desc:
            desc['name'] = desc['key']
        self.__dict__.update(desc)

    def updateKeymap(self, keymap):
        # store reference from key to field for updates
        for kn in ('key', 'statuskey', 'fixedkey', 'unitkey', 'formatkey'):
            key = getattr(self, kn)
            if key:
                keymap.setdefault(key, []).append(self)


class Block(object):
    def __init__(self, config=None):
        config = config or {}
        self.enabled = True
        self.content = []

    def add(self, p):
        self.content.append(p)

    def __str__(self):
        if self.enabled:
            return ''.join(map(str, self.content))
        return ''


class Label(object):
    def __init__(self, cls='label', width=0, text='&nbsp;',
                 fore='inherit', back='inherit'):
        self.cls = cls
        self.width = width
        self.text = text
        self.fore = fore
        self.back = back

    def __str__(self):
        return ('<div class="%s" style="color: %s; min-width: %sex; '
                'background-color: %s">%s</div>' %
                (self.cls, self.fore, self.width, self.back, self.text))


class Plot(object):
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.data = []
        self.lock = RLock()
        self.figure = mpl.figure(figsize=(width/11., height/11.))
        ax = self.figure.gca()
        ax.grid()
        ax.xaxis.set_major_locator(mpldate.AutoDateLocator())
        fmt = '%m-%d %H:%M:%S'
        if window < 24*3600:
            fmt = fmt[6:]
        if window > 300:
            fmt = fmt[:-3]
        ax.xaxis.set_major_formatter(mpldate.DateFormatter(fmt))
        self.curves = []

    def addcurve(self, name):
        self.curves.append(self.figure.gca().plot([], [], lw=2, label=name)[0])
        self.data.append([[], [], []])
        self.figure.gca().legend(loc=2, prop={'size': 'small'}).draw_frame(0)
        return len(self.curves) - 1

    def updatevalues(self, curve, x, y):
        # we have to guard modifications to self.data, since otherwise the
        # __str__ method below may see inconsistent X and Y lists, which will
        # cause matplotlib to raise exceptions
        with self.lock:
            ts, dt, yy = self.data[curve]
            ts.append(x)
            dt.append(datetime.fromtimestamp(x))
            yy.append(y)
            i = 0
            ll = len(ts)
            limit = currenttime() - self.window
            while i < ll and ts[i] < limit:
                i += 1
            self.data[curve][:] = [ts[i:], dt[i:], yy[i:]]

    def __str__(self):
        with self.lock:
            for i, (d, c) in enumerate(zip(self.data, self.curves)):
                # add a point "current value" at "right now" to avoid curves
                # not updating if the value doesn't change
                try:
                    self.updatevalues(i, currenttime(), d[2][-1])
                    c.set_data(d[1], d[2])
                except IndexError:
                    # no data (yet)
                    pass
        ax = self.figure.gca()
        try:
            ax.relim()
            ax.autoscale_view()
        except Exception:
            # print('error while determining limits')
            return ''
        try:
            mpl.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        except Exception:
            # no data yet in plot
            return ''
        self.figure.tight_layout()
        io = BytesIO()
        self.figure.savefig(io, format='svg', facecolor=(0,0,0,0))
        return ('<img src="data:image/svg+xml;base64,%s" '
                'style="width: %sex; height: %sex">' % (
                    from_utf8(b2a_base64(io.getvalue())),
                    self.width, self.height))


class Picture(object):

    def __init__(self, filepath, width, height, name):
        self.filepath = filepath
        self.width = width
        self.height = height
        self.name = name

    def __str__(self):
        s = ''
        if self.name:
            s += '<div class="label">%s</div><br>' % self.name
        s += '<img src="%s" style="width: %sex; height: %sex">' % (
            self.filepath, self.width, self.height)
        return s


class Monitor(BaseMonitor):
    """HTML specific implementation of instrument monitor."""

    parameters = {
        'filename': Param('Filename for HTML output', type=str, mandatory=True),
        'interval': Param('Interval for writing file', default=5),
    }

    def mainLoop(self):
        while not self._stoprequest:
            sleep(self.interval)
            try:
                content = ''.join(map(str, self._content))
                open(self.filename, 'w').write(content)
            except Exception:
                self.log.error('could not write status to %r'
                               % self.filename, exc=1)
            else:
                self.log.debug('wrote status to %r' % self.filename)

    def closeGui(self):
        pass

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

        add = self._content.append

        headprops = dict(
            fs = self._fontsize,
            fst = self._fontsize + self._fontsizebig,
            fsb = self._fontsizebig,
            ff = self.font,
            ffm = self.valuefont or self.font,
            intv = self.interval,
            title = escape(self.title),
            icon = nicos_icon,
        )
        add(HEAD % headprops)

        add('<table class="layout">'
            '<tr><td><div class="time">')
        self._timelabel = Label('timelabel')
        add(self._timelabel)
        add('</div><div>')
        self._warnlabel = Label('warnings', back='red', text='')
        add(self._warnlabel)
        add('</div></td></tr>\n')

        self._plots = {}

        def _create_field(blk, config):
            if 'widget' in config or 'gui' in config:
                self.log.warning('ignoring "widget" or "gui" element in HTML '
                                 'monitor configuration')
                return
            field = Field(self._prefix, config)
            field.updateKeymap(self._keymap)
            if field.plot and matplotlib:
                p = self._plots.get(field.plot)
                if not p:
                    p = Plot(field.plotwindow, field.width, field.height)
                    self._plots[field.plot] = p
                    blk.add(p)
                field._plotcurve = p.addcurve(field.name)
            elif field.picture:
                pic = Picture(field.picture, field.width, field.height,
                              escape(field.name))
                blk.add(pic)
            else:
                # deactivate plots
                field.plot = None
                # create name label
                flabel = field._namelabel = Label('name', field.width,
                                                  escape(field.name))
                blk.add(flabel)
                blk.add('</td></tr><tr><td>')
                # create value label
                cls = 'value'
                if field.istext:
                    cls += ' istext'
                vlabel = field._valuelabel = Label(cls, fore='white')
                blk.add(vlabel)

        for superrow in self.layout:
            add('<tr><td class="center">\n')
            for column in superrow:
                add('  <table class="column"><tr><td>')
                for block in column:
                    blockconfig = block[1] if len(block) > 1 else None
                    block = block[0]
                    blk = Block(blockconfig)
                    blk.add('<div class="block">')
                    blk.add('<div class="blockhead">%s</div>' % escape(block[0]))
                    blk.add('\n    <table class="blocktable">')
                    for row in block[1]:
                        if row is None:
                            blk.add('<tr></tr>')
                        else:
                            blk.add('<tr><td class="center">')
                            for field in row:
                                blk.add('\n      <table class="field"><tr><td>')
                                _create_field(blk, field)
                                blk.add('</td></tr></table> ')
                            blk.add('\n    </td></tr>')
                    blk.add('</table>\n  </div>')
                    add(blk)
                    if blockconfig:
                        setups = blockconfig.get('setups', [])
                        setupnames = [setups] if isinstance(setups, string_types) \
                                     else setups
                        for setupname in setupnames:
                            self._onlymap.setdefault(setupname, []).append(blk)
                add('</td></tr></table>\n')
            add('</td></tr>')
        add('</table>\n')
        add('</body></html>\n')

    def updateTitle(self, text):
        self._timelabel.text = text

    # pylint: disable=W0221
    def signal(self, field, signal, key, value, time, expired):
        if field.plot:
            if key == field.key and value is not None:
                self._plots[field.plot].updatevalues(field._plotcurve,
                                                     time, value)
            return
        if key == field.key:
            # apply item selection
            field.value = value
            if field.item >= 0 and value is not None:
                try:
                    fvalue = value[field.item]
                except Exception:
                    fvalue = value
            else:
                fvalue = value
            if field.min is not None and fvalue < field.min:
                field._namelabel.back = self._red
            elif field.max is not None and fvalue > field.max:
                field._namelabel.back = self._red
            else:
                field._namelabel.back = self._bgcolor
            if expired:
                field._valuelabel.back = self._gray
            else:
                field._valuelabel.back = self._black
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
                if status == OK:
                    field._valuelabel.fore = self._green
                elif status == WARN:
                    field._valuelabel.fore = self._orange
                elif status == BUSY:
                    field._valuelabel.fore = self._yellow
                elif status in (ERROR, NOTREACHED):
                    field._valuelabel.fore = self._red
                else:
                    field._valuelabel.fore = self._white
        elif key == field.unitkey:
            if value is not None:
                field.unit = value
                field._namelabel.text = self._labelunittext(field.name, field.unit,
                                                            field.fixed)
        elif key == field.fixedkey:
            field.fixed = value and ' (F)' or ''
            field._namelabel.text = self._labelunittext(field.name, field.unit,
                                                        field.fixed)
        elif key == field.formatkey:
            if value is not None:
                field.format = value
                self.signal(field, 'keyChange', field.key, field.value, 0, False)

    def _labelunittext(self, text, unit, fixed):
        return escape(text) + ' <span class="unit">%s</span><span ' \
            'class="fixed">%s</span> ' % (escape(unit), fixed)

    def switchWarnPanel(self, on):
        if on:
            self._warnlabel.text = escape(self._currwarnings)
        else:
            self._warnlabel.text = ''

    def reconfigureBoxes(self):
        for setup, boxes in iteritems(self._onlymap):
            for block in boxes:
                block.enabled = checkSetupSpec(setup, self._setups,
                                               compat='and', log=self.log)
