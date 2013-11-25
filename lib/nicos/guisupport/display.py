#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""
NICOS value display widget.
"""

import ast
from cgi import escape
from time import time as currenttime

import sip
from PyQt4.QtCore import Qt, QSize, QTimer, SIGNAL
from PyQt4.QtGui import QLabel, QFrame, QColor, QWidget, QVBoxLayout, \
     QHBoxLayout, QFontMetrics

from nicos.core.status import OK, BUSY, PAUSED, ERROR, NOTREACHED, UNKNOWN, \
     statuses
from nicos.clients.gui.utils import setBackgroundColor, setForegroundColor
from nicos.guisupport.widget import NicosWidget, PropDef


_black = QColor('black')
_red   = QColor('red')
_gray  = QColor('gray')

statusColor = {
    OK:         QColor('#00ff00'),
    BUSY:       QColor('yellow'),
    PAUSED:     QColor('yellow'),
    ERROR:      QColor('red'),
    NOTREACHED: QColor('red'),
    UNKNOWN:    QColor('white'),
}


class SensitiveSMLabel(QLabel):
    """A label that calls back when entered/left by the mouse."""
    def __init__(self, text, parent, enter, leave):
        QLabel.__init__(self, text, parent)
        self._enter = enter
        self._leave = leave
    def enterEvent(self, event):
        self._enter(self, event)
    def leaveEvent(self, event):
        self._leave(self, event)


def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class ValueDisplay(NicosWidget, QWidget):
    """Default value display widget with two labels."""

    designer_description = 'A widget with name/value labels'
    designer_icon = ':/table'

    def __init__(self, parent, designMode=False, **kwds):
        # keys being watched
        self._mainkeyid = None
        self._statuskeyid = None

        # eval()ed min and max values
        self._minvalue = None
        self._maxvalue = None

        # other current values
        self._isfixed = ''
        # XXX could be taken from devinfo
        self._lastvalue = designMode and '1.4' or None
        self._laststatus = (OK, '')
        self._lastchange = 0
        self._mouseover = False
        self._mousetimer = None
        self._statuscolor = statusColor[UNKNOWN]

        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)

    properties = {
        'dev':        PropDef(str, ''),
        'key':        PropDef(str, ''),
        'statuskey':  PropDef(str, ''),
        'name':       PropDef(str, ''),
        'unit':       PropDef(str, ''),
        'item':       PropDef(int, -1),
        'format':     PropDef(str, ''),
        'maxlen':     PropDef(int, -1),
        'width':      PropDef(int, 8),
        'min':        PropDef(str, ''),
        'max':        PropDef(str, ''),
        'istext':     PropDef(bool, False),
        'showName':   PropDef(bool, True),
        'showStatus': PropDef(bool, True),
        'showExpiration': PropDef(bool, True),
        'horizontal': PropDef(bool, False),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
                self.statuskey = value + '.status'
        elif pname == 'min':
            if not value:
                self._minvalue = None
            else:
                self._minvalue = ast.literal_eval(value)
            self._applywarncolor(self._lastvalue)
        elif pname == 'max':
            if not value:
                self._maxvalue = None
            else:
                self._maxvalue = ast.literal_eval(value)
            self._applywarncolor(self._lastvalue)
        elif pname == 'width':
            onechar = QFontMetrics(self.valueFont).width('0')
            self.valuelabel.setMinimumSize(QSize(onechar * (value + .5), 0))
        elif pname == 'istext':
            self.valuelabel.setFont(value and self.font() or self.valueFont)
            self.width = self.width
        elif pname == 'valueFont':
            self.valuelabel.setFont(self.valueFont)
            self.width = self.width  # update char width calculation
        elif pname == 'showName':
            self.namelabel.setVisible(value)
        elif pname == 'showStatus':
            if not value:
                setForegroundColor(self.valuelabel, statusColor[UNKNOWN])
        elif pname == 'showExpiration':
            if not value:
                setBackgroundColor(self.valuelabel, statusColor[UNKNOWN])
        elif pname == 'horizontal':
            self.reinitLayout()
        if pname in ('dev', 'name', 'unit'):
            self.update_namelabel()
        NicosWidget.propertyUpdated(self, pname, value)

    def initUi(self):
        self.namelabel = QLabel(' ', self, textFormat=Qt.RichText)
        self.update_namelabel()

        valuelabel = SensitiveSMLabel('----', self, self._label_entered,
                                      self._label_left)
        valuelabel.setFrameShape(QFrame.Panel)
        valuelabel.setAlignment(Qt.AlignHCenter)
        valuelabel.setFrameShadow(QFrame.Sunken)
        valuelabel.setAutoFillBackground(True)
        setBackgroundColor(valuelabel, _black)
        setForegroundColor(valuelabel, statusColor[UNKNOWN])
        valuelabel.setLineWidth(2)
        self.valuelabel = valuelabel
        self.width = 8

        self.reinitLayout()

    def reinitLayout(self):
        # reinitialize UI after switching horizontal/vertical layout
        if self.props['horizontal']:
            new_layout = QHBoxLayout()
            new_layout.addWidget(self.namelabel)
            new_layout.addStretch()
            new_layout.addWidget(self.valuelabel)
            self.namelabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        else:
            new_layout = QVBoxLayout()
            new_layout.addWidget(self.namelabel)
            tmplayout = QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(self.valuelabel)
            tmplayout.addStretch()
            new_layout.addLayout(tmplayout)
            self.namelabel.setAlignment(Qt.AlignHCenter)
        if self.layout():
            sip.delete(self.layout())
        new_layout.setContentsMargins(1, 1, 1, 1)  # save space
        self.setLayout(new_layout)

    def registerKeys(self):
        if self.props['dev']:
            self.registerDevice(self.props['dev'], self.props['item'],
                                self.props['unit'], self.props['format'])
        else:
            self.registerKey(self.props['key'], self.props['statuskey'],
                             self.props['item'], self.props['unit'],
                             self.props['format'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        # check expired values
        if expired and self.props['showExpiration']:
            setBackgroundColor(self.valuelabel, _gray)
        else:
            setBackgroundColor(self.valuelabel, _black)
        self._applywarncolor(value)
        if self.props['maxlen'] > -1:
            self.valuelabel.setText(strvalue[:self.props['maxlen']])
        else:
            self.valuelabel.setText(strvalue)
        self._lastvalue = value
        self._lastchange = currenttime()
        setForegroundColor(self.valuelabel, statusColor[BUSY])
        QTimer.singleShot(1000, self._applystatuscolor)

    def _applystatuscolor(self):
        setForegroundColor(self.valuelabel, self._statuscolor)

    def _applywarncolor(self, value):
        # check min/max values
        if (self._minvalue is not None and value < self._minvalue) or \
            (self._maxvalue is not None and value > self._maxvalue):
            self.namelabel.setAutoFillBackground(True)
            setBackgroundColor(self.namelabel, _red)
        else:
            self.namelabel.setAutoFillBackground(False)

    def on_devStatusChange(self, dev, code, status, expired):
        if self.props['showStatus']:
            self._statuscolor = statusColor[code]
            self._laststatus = code, status
            self._applystatuscolor()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed, minval, maxval):
        self._isfixed = fixed and ' (F)'
        self.format = fmtstr
        self.unit = unit
        self.min = repr(minval)
        self.max = repr(maxval)

    def update_namelabel(self):
        name = self.props['name'] or self.props['dev'] or self.props['key']
        self.namelabel.setText(escape(unicode(name)) +
            ' <font color="#888888">%s</font><font color="#0000ff">%s</font> ' %
            (escape(self.props['unit'].strip()), self._isfixed))

    def _label_entered(self, widget, event, from_mouse=True):
        infotext = '%s = %s' % (self.props['name'] or self.props['dev']
                                or self.props['key'], self.valuelabel.text())
        if self.props['unit'].strip():
            infotext += ' %s' % self.props['unit']
        if self.props['statuskey']:
            try:
                const, msg = self._laststatus
            except ValueError:
                const, msg = self._laststatus, ''
            infotext += ', status is %s: %s' % (statuses.get(const, '?'), msg)
        infotext += ', changed %s ago' % (
            nicedelta(currenttime() - self._lastchange))
        self.emit(SIGNAL('widgetInfo'), infotext)
        if from_mouse:
            self._mousetimer = QTimer(self, timeout=
                lambda: self._label_entered(widget, event, False))
            self._mousetimer.start(1000)

    def _label_left(self, widget, event):
        if self._mousetimer:
            self._mousetimer.stop()
            self._mousetimer = None
            self.emit(SIGNAL('widgetInfo'), '')
