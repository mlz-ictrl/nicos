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

"""
NICOS value display widget.
"""

from cgi import escape
from time import time as currenttime

import sip
from PyQt4.QtCore import Qt, QSize, QTimer, SIGNAL
from PyQt4.QtGui import QLabel, QFrame, QColor, QWidget, QVBoxLayout, \
    QHBoxLayout, QFontMetrics

from nicos.core.status import OK, WARN, BUSY, ERROR, NOTREACHED, UNKNOWN, \
    statuses
from nicos.guisupport.utils import setBackgroundColor, setForegroundColor, \
    setBothColors
from nicos.guisupport.squeezedlbl import SqueezedLabel
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.pycompat import text_type, from_maybe_utf8


defaultColorScheme = {
    'fore': {
        OK:         QColor('#00ff00'),
        WARN:       QColor('#ffa500'),
        BUSY:       QColor('yellow'),
        ERROR:      QColor('red'),
        NOTREACHED: QColor('red'),
        UNKNOWN:    QColor('white'),
    },
    'back': {
        OK:         QColor('black'),
        WARN:       QColor('black'),
        BUSY:       QColor('black'),
        ERROR:      QColor('black'),
        NOTREACHED: QColor('black'),
        UNKNOWN:    QColor('black'),
    },
    'label': {
        OK:         None,
        WARN:       QColor('red'),
        BUSY:       None,
        ERROR:      QColor('red'),
        NOTREACHED: QColor('red'),
        UNKNOWN:    None,
    },
    'expired':      QColor('gray'),
}

lightColorScheme = {
    'fore': {
        OK:         QColor('#00cc00'),
        WARN:       QColor('black'),
        BUSY:       QColor('black'),
        ERROR:      QColor('black'),
        NOTREACHED: QColor('black'),
        UNKNOWN:    QColor('black'),
    },
    'back': {
        OK:         QColor('white'),
        WARN:       QColor('#ffa500'),
        BUSY:       QColor('yellow'),
        ERROR:      QColor('#ff4444'),
        NOTREACHED: QColor('#ff4444'),
        UNKNOWN:    QColor('white'),
    },
    'label': {
        OK:         None,
        WARN:       QColor('red'),
        BUSY:       None,
        ERROR:      QColor('red'),
        NOTREACHED: QColor('red'),
        UNKNOWN:    None,
    },
    'expired':      QColor('#cccccc'),
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


class ValueLabel(NicosWidget, SqueezedLabel):
    """Label that just displays a single value."""

    designer_description = 'A label that just displays a single value'
    # designer_icon = ':/'     # XXX add appropriate icons

    def __init__(self, parent, designMode=False, **kwds):
        self._designMode = designMode
        SqueezedLabel.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        if designMode:
            self.setText('(value display)')
        self._callback = lambda value, strvalue: from_maybe_utf8(strvalue)

    def setFormatCallback(self, callback):
        self._callback = callback

    properties = {
        'key': PropDef(str, '', 'Cache key to display'),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'key' and self._designMode:
            self.setText('(%s)' % value)
        NicosWidget.propertyUpdated(self, pname, value)

    def registerKeys(self):
        self.registerKey(self.props['key'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        if not expired:
            self.setText(self._callback(value, strvalue))


class ValueDisplay(NicosWidget, QWidget):
    """Value display widget with two labels."""

    designer_description = 'A widget with name/value labels'
    designer_icon = ':/table'

    def __init__(self, parent, designMode=False, colorScheme=None, **kwds):
        # keys being watched
        self._mainkeyid = None
        self._statuskeyid = None

        # other current values
        self._isfixed = ''
        # XXX could be taken from devinfo
        self._lastvalue = designMode and '1.4' or None
        self._laststatus = (OK, '')
        self._lastchange = 0
        self._mouseover = False
        self._mousetimer = None
        self._expired = True

        self._colorscheme = colorScheme or defaultColorScheme

        QWidget.__init__(self, parent, **kwds)
        NicosWidget.__init__(self)
        self._statuscolors = self._colorscheme['fore'][UNKNOWN], \
            self._colorscheme['back'][UNKNOWN]
        self._labelcolor = None

    properties = {
        'dev':        PropDef(str, '', 'NICOS device name, if set, display '
                              'value of this device'),
        'key':        PropDef(str, '', 'Cache key to display (without "nicos/" '
                              'prefix), set either "dev" or this'),
        'statuskey':  PropDef(str, '', 'Cache key to extract status information'
                              ' for coloring value, if "dev" is given this is '
                              'set automatically'),
        'name':       PropDef(str, '', 'Name of the value to display above/'
                              'left of the value; if "dev" is given this '
                              'defaults to the device name'),
        'unit':       PropDef(str, '', 'Unit of the value to display next to '
                              'the name; if "dev" is given this defaults to '
                              'the unit set in NICOS'),
        'item':       PropDef(int, -1, 'Item to extract from a value that is '
                              'a sequence of items'),
        'format':     PropDef(str, '', 'Python format string to use for the '
                              'value; if "dev" is given this defaults to the '
                              '"fmtstr" set in NICOS'),
        'maxlen':     PropDef(int, -1, 'Maximum length of the value string to '
                              'allow; defaults to no limit'),
        'width':      PropDef(int, 8, 'Width of the widget in units of the '
                              'width of one character'),
        'min':        PropDef(str, '', 'If given, and the value is below the '
                              'minimum, the name will be displayed with a red '
                              'background'),
        'max':        PropDef(str, '', 'If given, and the value is above the '
                              'maximum, the name will be displayed with a red '
                              'background'),
        'istext':     PropDef(bool, False, 'If given, a "text" font will be '
                              'used for the value instead of the monospaced '
                              'font used for numeric values'),
        'showName':   PropDef(bool, True, 'If false, do not display the '
                              'label for the value name'),
        'showStatus': PropDef(bool, True, 'If false, do not display the '
                              'device status as a color of the value text'),
        'showExpiration': PropDef(bool, True, 'If false, do not display the '
                                  'expiration of the cache key as a color'),
        'horizontal': PropDef(bool, False, 'If true, display name label '
                              'left of the value instead of above it'),
    }

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
                self.statuskey = value + '.status'
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
                setBothColors(self.valuelabel,
                              (self._colorscheme['fore'][UNKNOWN],
                               self._colorscheme['back'][UNKNOWN]))
        elif pname == 'showExpiration':
            if not value:
                setBackgroundColor(self.valuelabel, self._colorscheme['expired'])
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
        setBackgroundColor(valuelabel, self._colorscheme['fore'][UNKNOWN])
        setForegroundColor(valuelabel, self._colorscheme['back'][UNKNOWN])
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
        self._expired = expired
        if self._expired and self.props['showExpiration']:
            setBackgroundColor(self.valuelabel, self._colorscheme['expired'])
        else:
            setBackgroundColor(self.valuelabel, self._colorscheme['back'][BUSY])
        if self.props['maxlen'] > -1:
            self.valuelabel.setText(from_maybe_utf8(strvalue[:self.props['maxlen']]))
        else:
            self.valuelabel.setText(from_maybe_utf8(strvalue))
        self._lastvalue = value
        self._lastchange = currenttime()
        setForegroundColor(self.valuelabel, self._colorscheme['fore'][BUSY])
        QTimer.singleShot(1000, self._applystatuscolor)

    def _applystatuscolor(self):
        if self._expired and self.props['showExpiration']:
            setBackgroundColor(self.valuelabel, self._colorscheme['expired'])
        else:
            setBothColors(self.valuelabel, self._statuscolors)
            if self._labelcolor:
                self.namelabel.setAutoFillBackground(True)
                setBackgroundColor(self.namelabel, self._labelcolor)
            else:
                self.namelabel.setAutoFillBackground(False)

    def on_devStatusChange(self, dev, code, status, expired):
        if self.props['showStatus']:
            self._statuscolors = self._colorscheme['fore'][code], \
                self._colorscheme['back'][code]
            self._labelcolor = self._colorscheme['label'][code]
            self._laststatus = code, status
            self._applystatuscolor()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._isfixed = fixed and ' (F)'
        self.format = fmtstr
        self.unit = unit or ''

    def update_namelabel(self):
        name = self.props['name'] or self.props['dev'] or self.props['key']
        self.namelabel.setText(
            escape(text_type(name)) +
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
            self._mousetimer = QTimer(self, timeout=lambda:
                                      self._label_entered(widget, event, False))
            self._mousetimer.start(1000)

    def _label_left(self, widget, event):
        if self._mousetimer:
            self._mousetimer.stop()
            self._mousetimer = None
            self.emit(SIGNAL('widgetInfo'), '')
