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

"""
NICOS value display widget.
"""

__version__ = "$Revision$"

import ast
from cgi import escape
from time import time as currenttime

import sip
from PyQt4.QtCore import Qt, pyqtProperty, QSize, QTimer, SIGNAL
from PyQt4.QtGui import QLabel, QFrame, QColor, QWidget, QVBoxLayout, \
     QHBoxLayout, QFontMetrics

from nicos.core.status import OK, BUSY, PAUSED, ERROR, NOTREACHED, UNKNOWN, \
     statuses
from nicos.clients.gui.utils import setBackgroundColor, setForegroundColor
from nicos.guisupport.widget import DisplayWidget


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


class ValueDisplay(QWidget, DisplayWidget):
    """Default value display widget with two labels."""

    designer_description = 'A widget with name/value labels'
    designer_icon = ':/table'

    def __init__(self, parent, designMode=False, **kwds):
        # keys being watched
        self._mainkeyid = None
        self._statuskeyid = None

        # default values for Qt properties
        self._device = ''
        self._key = ''
        self._statuskey = ''
        self._showstatus = True
        self._showexpiration = True
        self._showname = True
        self._valuename = ''
        self._valueunit = ''
        self._valueindex = -1
        self._formatstring = ''
        self._textcutoff = -1
        self._charwidth = 8
        self._minvalue = None
        self._maxvalue = None
        self._horizontal = False

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
        DisplayWidget.__init__(self)

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
        self.charWidth = 8

        self.reinitLayout()

    def reinitLayout(self):
        # reinitialize UI after switching horizontal/vertical layout
        if self._horizontal:
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
        self.setLayout(new_layout)

    def setConfig(self, config, labelfont, valuefont, scale):
        self.pyqtConfigure(
            device       = config.get('dev', self._device),
            key          = config.get('key', self._key),
            statuskey    = config.get('statuskey', self._statuskey),
            valueIndex   = config.get('item', self._valueindex),
            valueName    = config.get('name', self._valuename),
            valueUnit    = config.get('unit', self._valueunit),
            formatString = config.get('format', self._formatstring),
            textCutoff   = config.get('maxlen', self._textcutoff),
            font         = labelfont,
            valueFont    = labelfont if config.get('istext', False)
                           else valuefont,
            charWidth    = config.get('width', 8),
        )
        if 'min' in config:
            self.minValue = repr(config['min'])
        if 'max' in config:
            self.maxValue = repr(config['max'])

    def registerKeys(self):
        if self._device:
            self.registerDevice(self._device, self._valueindex, self._valueunit,
                                self._formatstring)
        else:
            self.registerKey(self._key, self._statuskey, self._valueindex,
                             self._valueunit, self._formatstring)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        # check expired values
        if expired and self._showexpiration:
            setBackgroundColor(self.valuelabel, _gray)
        else:
            setBackgroundColor(self.valuelabel, _black)
        self._applywarncolor(value)
        if self._textcutoff > -1:
            self.valuelabel.setText(strvalue[:self._textcutoff])
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
        if self._showstatus:
            self._statuscolor = statusColor[code]
            self._laststatus = code, status
            self._applystatuscolor()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed, minval, maxval):
        self._isfixed = fixed and ' (F)'
        self.formatString = fmtstr
        self.valueUnit = unit
        self.minValue = str(minval)
        self.maxValue = str(maxval)

    def update_namelabel(self):
        name = self._valuename or self._device or self._key
        self.namelabel.setText(escape(unicode(name)) + ' <font color="#888888">%s</font>'
            '<font color="#0000ff">%s</font> ' % (escape(self._valueunit.strip()),
                                                  self._isfixed))

    def _label_entered(self, widget, event, from_mouse=True):
        infotext = '%s = %s' % (self._valuename or self._device or self._key,
                                self.valuelabel.text())
        if self._valueunit.strip():
            infotext += ' %s' % self._valueunit
        if self._statuskey:
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

    def get_device(self):
        return self._device
    def set_device(self, value):
        self._device = str(value)
        if value:
            self._key = str(value + '.value')
            self._statuskey = str(value + '.status')
        self.update_namelabel()
    def reset_device(self):
        self._device = ''
    device = pyqtProperty(str, get_device, set_device, reset_device)

    def get_key(self):
        return self._key
    def set_key(self, value):
        self._key = str(value)
    def reset_key(self):
        self._key = ''
    key = pyqtProperty(str, get_key, set_key, reset_key)

    def get_statuskey(self):
        return self._statuskey
    def set_statuskey(self, value):
        self._statuskey = str(value)
    def reset_statuskey(self):
        self._statuskey = ''
    statuskey = pyqtProperty(str, get_statuskey, set_statuskey, reset_statuskey)

    def get_showName(self):
        return self._showname
    def set_showName(self, value):
        self.namelabel.setVisible(value)
        self._showname = value
    def reset_showName(self):
        self.showName = True
    showName = pyqtProperty('bool', get_showName, set_showName, reset_showName)

    def get_showStatus(self):
        return self._showstatus
    def set_showStatus(self, value):
        self._showstatus = value
        if not value:
            setForegroundColor(self.valuelabel, statusColor[UNKNOWN])
    def reset_showStatus(self):
        self.showStatus = True
    showStatus = pyqtProperty('bool', get_showStatus, set_showStatus,
                              reset_showStatus)

    def get_showExpiration(self):
        return self._showexpiration
    def set_showExpiration(self, value):
        self._showexpiration = value
        if not value:
            setBackgroundColor(self.valuelabel, statusColor[UNKNOWN])
    def reset_showExpiration(self):
        self.showExpiration = True
    showExpiration = pyqtProperty('bool', get_showExpiration,
                                  set_showExpiration, reset_showExpiration)

    def get_valueName(self):
        return self._valuename
    def set_valueName(self, value):
        self._valuename = value
        self.update_namelabel()
    def reset_valueName(self):
        self.valueName = ''
    valueName = pyqtProperty(str, get_valueName, set_valueName, reset_valueName)

    def get_valueUnit(self):
        return self._valueunit
    def set_valueUnit(self, value):
        self._valueunit = str(value)
        self.update_namelabel()
    def reset_valueUnit(self):
        self.valueUnit = ''
    valueUnit = pyqtProperty(str, get_valueUnit, set_valueUnit, reset_valueUnit)

    def get_valueIndex(self):
        return self._valueindex
    def set_valueIndex(self, value):
        self._valueindex = value
    def reset_valueIndex(self):
        self.valueIndex = -1
    valueIndex = pyqtProperty(int, get_valueIndex, set_valueIndex,
                              reset_valueIndex)

    def get_formatString(self):
        return self._formatstring
    def set_formatString(self, value):
        self._formatstring = str(value)
    def reset_formatString(self):
        self.formatString = '%s'
    formatString = pyqtProperty(str, get_formatString, set_formatString,
                                reset_formatString)

    def get_textCutoff(self):
        return self._textcutoff
    def set_textCutoff(self, value):
        self._textcutoff = value
    def reset_textCutoff(self):
        self.textCutoff = -1
    textCutoff = pyqtProperty(int, get_textCutoff, set_textCutoff,
                              reset_textCutoff)

    def get_minValue(self):
        return repr(self._minvalue) if self._minvalue is not None else ''
    def set_minValue(self, value):
        if value in ('', 'None'):
            self._minvalue = None
        else:
            self._minvalue = ast.literal_eval(str(value))
        self._applywarncolor(self._lastvalue)
    def reset_minValue(self):
        self._minvalue = None
    minValue = pyqtProperty(str, get_minValue, set_minValue, reset_minValue)

    def get_maxValue(self):
        return repr(self._maxvalue) if self._maxvalue is not None else ''
    def set_maxValue(self, value):
        if value in ('', 'None'):
            self._maxvalue = None
        else:
            self._maxvalue = ast.literal_eval(str(value))
        self._applywarncolor(self._lastvalue)
    def reset_maxValue(self):
        self._maxvalue = None
    maxValue = pyqtProperty(str, get_maxValue, set_maxValue, reset_maxValue)

    def get_charWidth(self):
        return self._charwidth
    def set_charWidth(self, value):
        self._charwidth = value
        onechar = QFontMetrics(self.valueFont).width('0')
        self.valuelabel.setMinimumSize(QSize(onechar * (value + .5), 0))
    def reset_charWidth(self):
        self.charWidth = 8
    charWidth = pyqtProperty(int, get_charWidth, set_charWidth, reset_charWidth)

    def get_valueFont(self):
        return self.valuelabel.font()
    def set_valueFont(self, value):
        self.valuelabel.setFont(value)
        self.charWidth = self.charWidth  # update minimum size
    def reset_valueFont(self):
        self.valueFont = self.font()
    valueFont = pyqtProperty('QFont', get_valueFont, set_valueFont,
                             reset_valueFont)

    def get_horizontal(self):
        return self._horizontal
    def set_horizontal(self, value):
        self._horizontal = value
        self.reinitLayout()
    def reset_horizontal(self):
        self.horizontal = False
    horizontal = pyqtProperty(bool, get_horizontal, set_horizontal,
                              reset_horizontal)
