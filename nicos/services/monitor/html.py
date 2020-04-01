#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import functools
import operator
import os
import tempfile
import time
from binascii import b2a_base64
from threading import RLock
from time import sleep, time as currenttime

import numpy
from lttb import lttb

from nicos.core import Param
from nicos.core.constants import NOT_AVAILABLE
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, WARN
from nicos.pycompat import escape_html, from_utf8, string_types, text_type, \
    to_utf8
from nicos.services.monitor import Monitor as BaseMonitor
from nicos.services.monitor.icon import nicos_icon
from nicos.utils import checkSetupSpec, extractKeyAndIndex, safeWriteFile

try:
    from gr import pygr
    import gr

    # required for import order on Py3
    import nicos.clients.gui.widgets.plotting  # pylint: disable=unused-import
    from nicos.guisupport.plots import NicosTimePlotAxes
except ImportError:
    pygr = None


HEAD = u'''\
<html>
<head>
<meta charset="utf-8"/>
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

    # conditional hiding
    setups = None    # setupspec for which should be shown (None = always)
    enabled = True   # if the field is currently shown

    def __init__(self, prefix, desc):
        if isinstance(desc, string_types):
            desc = {'dev': desc}
        else:
            desc = desc._options
        if 'dev' in desc:
            dev = desc.pop('dev')
            if 'name' not in desc:
                desc['name'] = dev
            dev, indices, _scale, _offset = extractKeyAndIndex(
                dev, False, normalize=lambda s: s.lower())
            if indices:
                desc['item'] = indices
            desc['key'] = prefix + dev + '/value'
            desc['statuskey'] = prefix + dev + '/status'
            desc['fixedkey'] = prefix + dev + '/fixed'
            if 'unit' not in desc:
                desc['unitkey'] = prefix + dev + '/unit'
            if 'format' not in desc:
                desc['formatkey'] = prefix + dev + '/fmtstr'
        elif 'key' in desc:
            key, indices, _scale, _offset = extractKeyAndIndex(desc['key'], False)
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


class Static(text_type):

    def getHTML(self):
        return self


class Block(object):
    def __init__(self, config):
        self.enabled = True
        self._content = []
        self.setups = config.get('setups')
        self._onlyfields = []

    def __iadd__(self, content):
        """Easily adds content to the block using ``+=``."""
        if isinstance(content, string_types):
            self._content.append(Static(content))
        else:
            self._content.append(content)
        return self

    def getHTML(self):
        if self.enabled and self._content:
            return u''.join(c.getHTML() for c in self._content)
        return u''


class Label(object):
    def __init__(self, cls='label', width=0, text='&nbsp;',
                 fore='inherit', back='inherit'):
        self.cls = cls
        self.width = width
        self.text = text
        self.fore = fore
        self.back = back
        self.enabled = True

    def getHTML(self):
        if not self.enabled:
            return u''
        return (u'<div class="%s" style="color: %s; min-width: %sex; '
                'background-color: %s">%s</div>' %
                (self.cls, self.fore, self.width, self.back, self.text))


DATEFMT = '%Y-%m-%d'
TIMEFMT = '%H:%M:%S'


class Plot(object):

    # if the field should be displayed
    enabled = True

    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.data = []
        self.lock = RLock()
        self.plot = pygr.Plot(viewport=(.1, .95, .25, .95))
        self.axes = NicosTimePlotAxes(self.plot._viewport)
        self.plot.addAxes(self.axes)
        self.plot.setLegend(True)
        self.plot.setLegendWidth(0.07)
        self.plot.offsetXLabel = -.2
        self.axes.setXtickCallback(self.xtickCallBack)
        self.curves = []
        os.environ['GKS_WSTYPE'] = 'svg'
        (fd, self.tempfile) = tempfile.mkstemp('.svg')
        os.close(fd)

    def xtickCallBack(self, x, y, _svalue, value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        dx = .02
        timeVal = time.localtime(value)
        gr.text(x + dx, y - 0.01, time.strftime(DATEFMT, timeVal))
        gr.text(x - dx, y - 0.01, time.strftime(TIMEFMT, timeVal))
        gr.setcharup(0., 1.)

    def addcurve(self, name):
        self.curves.append(pygr.PlotCurve([currenttime()], [0], legend=name,
                                          linewidth=4))
        self.axes.addCurves(self.curves[-1])
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
        if not self.enabled:
            return ''
        if not self.data or not self.curves:
            return u'<span>No data or curves found</span>'
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
        c = self.axes.getCurves()
        self.axes.setWindow(c.xmin, c.xmax, c.ymin, c.ymax)
        if os.path.isfile(self.tempfile):
            os.unlink(self.tempfile)
        gr.beginprint(self.tempfile)
        gr.setwsviewport(0, self.width * 0.0022, 0, self.height * 0.0022)
        try:
            self.plot.drawGR()
        finally:
            gr.endprint()
            gr.clearws()
        with open(self.tempfile, 'rb') as fp:
            imgbytes = fp.read()
        return (u'<img src="data:image/svg+xml;base64,%s" '
                'style="width: %sex; height: %sex">' % (
                    from_utf8(b2a_base64(imgbytes)),
                    self.width, self.height))


class Picture(object):

    # if the field should be displayed
    enabled = True

    def __init__(self, filepath, width, height, name):
        self.filepath = filepath
        self.width = width
        self.height = height
        self.name = name

    def getHTML(self):
        s = u''
        if not self.enabled:
            return s
        if self.name:
            s += u'<div class="label">%s</div><br>' % self.name
        s += u'<img src="%s" style="width: %sex; height: %sex">' % (
            self.filepath, self.width, self.height)
        return s


class Monitor(BaseMonitor):
    """HTML specific implementation of instrument monitor."""

    parameters = {
        'filename': Param('Filename for HTML output', type=str, mandatory=True),
        'interval': Param('Interval for writing file', default=5),
        'noexpired': Param('If true, show expired values as "n/a"', type=bool)
    }

    def mainLoop(self):
        while not self._stoprequest:
            try:
                if self._content:
                    content = u''.join(ct.getHTML() for ct in self._content)
                    safeWriteFile(self.filename, to_utf8(content), mode='wb',
                                  maxbackups=0)
            except Exception:
                self.log.error('could not write status to %r', self.filename,
                               exc=1)
            else:
                self.log.debug('wrote status to %r', self.filename)
            sleep(self.interval)

    def closeGui(self):
        pass

    def __iadd__(self, content):
        if isinstance(content, string_types):
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
            fs = self._fontsize,
            fst = self._timefontsize,
            fsb = self._fontsizebig,
            ff = self.font,
            ffm = self.valuefont or self.font,
            intv = self.interval,
            title = escape_html(self.title),
            icon = nicos_icon,
        )

        self += HEAD % headprops

        self += u'<table class="layout"><tr><td><div class="time">'
        self._timelabel = Label('timelabel')
        self += self._timelabel
        self += u'</div><div>'
        self._warnlabel = Label('warnings', back='red', text='')
        self += self._warnlabel
        self += u'</div></td></tr>\n'

        self._plots = {}

        def _create_field(blk, config):
            if 'widget' in config or 'gui' in config:
                self.log.warning('ignoring "widget" or "gui" element in HTML '
                                 'monitor configuration')
                return None
            field = Field(self._prefix, config)
            field.updateKeymap(self._keymap)

            if field.plot and pygr:
                p = self._plots.get(field.plot)
                if not p:
                    p = Plot(field.plotwindow, field.width, field.height)
                    self._plots[field.plot] = p
                    blk += p
                field._plotcurve = p.addcurve(field.name)
            elif field.picture:
                pic = Picture(field.picture, field.width, field.height,
                              escape_html(field.name))
                blk += pic
            else:
                # deactivate plots
                field.plot = None
                # create name label
                flabel = field._namelabel = Label('name', field.width,
                                                  escape_html(field.name))
                blk += flabel
                blk += u'</td></tr><tr><td>'
                # create value label
                cls = 'value'
                if field.istext:
                    cls += ' istext'
                vlabel = field._valuelabel = Label(cls, fore='white')
                blk += vlabel
            return field

        for superrow in self.layout:
            self += u'<tr><td class="center">\n'
            for column in superrow:
                self += u'  <table class="column"><tr><td>'
                for block in column:
                    block = self._resolve_block(block)
                    blk = Block(block._options)
                    blk += u'<div class="block">'
                    blk += (u'<div class="blockhead">%s</div>' %
                            escape_html(block._title))
                    blk += u'\n    <table class="blocktable">'
                    for row in block:
                        if row is None:
                            blk += u'<tr></tr>'
                        else:
                            blk += u'<tr><td class="center">'
                            for field in row:
                                blk += u'\n      <table class="field"><tr><td>'
                                f = _create_field(blk, field)
                                if f and f.setups:
                                    if blk.setups:
                                        blk._onlyfields.append(f)
                                    else:
                                        self._onlyfields.append(f)
                                blk += u'</td></tr></table> '
                            blk += u'\n    </td></tr>'
                    blk += u'</table>\n  </div>'
                    self += blk
                    if blk.setups:
                        self._onlyblocks.append(blk)
                self += u'</td></tr></table>\n'
            self += u'</td></tr>'
        self += u'</table>\n'
        self += u'</body></html>\n'

    def updateTitle(self, text):
        self._timelabel.text = text

    def signalKeyChange(self, field, key, value, time, expired):
        if field.plot:
            if key == field.key and value is not None:
                self._plots[field.plot].updatevalues(field._plotcurve,
                                                     time, value)
            return
        if key == field.key:
            # apply item selection
            field.value = value
            if value is not None:
                if isinstance(field.item, tuple):
                    try:
                        fvalue = functools.reduce(operator.getitem,
                                                  field.item, value)
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
            if field.min is not None and fvalue < field.min:
                field._namelabel.back = self._red
            elif field.max is not None and fvalue > field.max:
                field._namelabel.back = self._red
            else:
                field._namelabel.back = self._bgcolor
            if expired:
                field._valuelabel.back = self._gray
                if self.noexpired:
                    fvalue = 'n/a'
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
                elif status == DISABLED:
                    field._valuelabel.fore = self._white
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
                self.signalKeyChange(field, field.key, field.value, 0, False)

    def _labelunittext(self, text, unit, fixed):
        return escape_html(text) + u' <span class="unit">%s</span><span ' \
            'class="fixed">%s</span> ' % (escape_html(unit), fixed)

    def switchWarnPanel(self, on):
        if on:
            self._warnlabel.text = escape_html(self._currwarnings)
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
