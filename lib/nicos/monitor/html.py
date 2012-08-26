#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

from cgi import escape
from time import sleep

from nicos.core import Param
from nicos.monitor import Monitor as BaseMonitor


HEAD = '''\
<html>
<head>
<meta http-equiv="refresh" content="%(intv)s">
<style type="text/css">
body { background-color: #cccccc; font-family: '%(ff)s', sans-serif; font-size: %(fs)spx; }
table { font-family: inherit; font-size: 100%%; }
.time { text-align: center; font-size: %(fst)s; }
.timelabel { margin: 0.1em; padding: 0.2em; }
.blockhead { font-size: %(fsb)spx; text-align: center; font-weight: bold; }
.block { border: 2px outset #cccccc; padding: .5em; margin: .3em; }
.blocktable { width: 100%%; }
.blocktable > tr { width: 100%%; }
.field { display: inline-block; }
.field td  { text-align: center; }
.value { font-family: '%(ffm)s', monospace;
         padding: .15em; border: 2px inset #cccccc; }
.istext { font-family: '%(ff)s', sans-serif !important; font-weight: normal; }
.unit   { color: #888888; }
.warnings { margin-top: 1em; background-color: red; font-size: 120%%; }
</style>
</head>
<body>
'''

class Block(object):
    def __init__(self):
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


class Monitor(BaseMonitor):
    """HTML specific implementation of instrument monitor."""

    parameters = {
        'filename': Param('Filename for HTML output', type=str, mandatory=True),
        'interval': Param('Interval for writing file', default=1),
    }

    def mainLoop(self):
        while not self._stoprequest:
            sleep(self.interval)
            open(self.filename, 'w').write(''.join(map(str, self._content)))
            self.log.debug('wrote status to %r' % self.filename)

    def closeGui(self):
        pass

    def initColors(self):
        self._bgcolor = 'inherit'
        self._black = 'black'
        self._yellow = 'yellow'
        self._green = '#00ff00'
        self._red = 'red'
        self._gray = 'gray'
        self._white = 'white'

    def initGui(self):
        self._content = []

        add = self._content.append

        style = dict(
            fs = self._fontsize,
            fst = self._fontsize + self._fontsizebig,
            fsb = self._fontsizebig,
            ff = self.font,
            ffm = self.valuefont or self.font,
            intv = self.interval,
        )
        add(HEAD % style)

        add('<div class="time">')
        self._timelabel = Label('timelabel')
        add(self._timelabel)
        add('</div>\n<table class="layout">')

        for superrow in self._layout:
            add('<tr>')
            for column in superrow:
                add('<td>\n  <table class="column"><tr><td>')
                for block in column:
                    blk = Block()
                    blk.add('<div class="block">')
                    blk.add('<div class="blockhead">%s</div>' %
                            escape(block[0]['name']))
                    blk.add('\n    <table class="blocktable">')
                    for row in block[1]:
                        if row is None:
                            blk.add('<tr></tr>')
                        else:
                            blk.add('<tr><td style="text-align: center">')
                            for field in row:
                                blk.add('\n      <table class="field"><tr><td>')
                                flabel = Label('name', field['width'],
                                               escape(field['name']))
                                field['namelabel'] = flabel
                                blk.add(flabel)
                                blk.add('</td></tr><tr><td>')

                                cls = 'value'
                                if field['istext']: cls += ' istext'
                                field['valuelabel'] = Label(cls)
                                blk.add(field['valuelabel'])
                                blk.add('</td></tr></table> ')
                                self.updateKeymap(field)
                            blk.add('\n    </td></tr>')
                    blk.add('</table>\n  </div>')
                    add(blk)
                    if block[0]['only']:
                        self._onlymap.setdefault(block[0]['only'],
                                                 []).append(blk)
                add('</td></tr></table>\n</td>')
            add('</tr>')
        add('</table>\n')
        self._warnlabel = Label('warnings')
        add(self._warnlabel)
        add('</body></html>\n')

    def setLabelText(self, label, text):
        label.text = escape(text) or '&nbsp;'

    def setLabelUnitText(self, label, text, unit):
        label.text = escape(text) + ' <span class="unit">%s</span> ' % escape(unit)

    def setForeColor(self, label, fore):
        label.fore = fore

    def setBackColor(self, label, back):
        label.back = back

    def setBothColors(self, label, fore, back):
        label.fore = fore
        label.back = back

    def switchWarnPanel(self, off=False):
        pass

    def reconfigureBoxes(self):
        for setup, boxes in self._onlymap.iteritems():
            for block in boxes:
                if setup.startswith('!'):
                    block.enabled = setup[1:] not in self._setups
                else:
                    block.enabled = setup in self._setups
