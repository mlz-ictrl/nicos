# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special widgets for the SANS1 statusmonitor."""


from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QBrush, QColor, QLineF, QPainter, QPen, \
    QRectF, QSize, Qt, QTextOption, QWidget
from nicos.guisupport.widget import NicosWidget, PropDef

_magenta = QBrush(QColor('#A12F86'))
_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_grey = QBrush(QColor('lightgrey'))
_black = QBrush(QColor('black'))
_blue = QBrush(QColor('blue'))
_red = QBrush(QColor('red'))
_olive = QBrush(QColor('olive'))
_orange = QBrush(QColor('#ffa500'))

statusbrush = {
    BUSY: _yellow,
    WARN: _orange,
    ERROR: _red,
    NOTREACHED: _red,
    DISABLED: _white,
    OK: _white,
    UNKNOWN: _olive,
}


class Tube2(NicosWidget, QWidget):
    """SANS-1 tube with detector(s)."""

    designer_description = 'SANS-1 tube with two detectors'

    def __init__(self, parent, designMode=False):
        # det1pos, det1shift, det1tilt
        # Later: add det2pos
        self._curval = [0, 0, 0]
        self._curstr = ['', '', '']
        self._curstatus = [OK, OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    devices = PropDef('devices', 'QStringList', [], 'position, shift and '
                      'tilt of det1')
    height = PropDef('height', int, 10, 'Widget height in characters')
    width = PropDef('width', int, 30, 'Widget width in characters')
    name = PropDef('name', str, '', 'Display name')
    posscale = PropDef('posscale', float, 20000, 'Length of the tube')
    color = PropDef('color', 'QColor', _magenta.color(), 'Color of the tube')

    def sizeHint(self):
        return QSize(round(self.props['width'] * self._scale) + 10,
                     round(self.props['height'] * self._scale) +
                     round(self.props['name'] and self._scale * 2.5 or 0) + 40)

    def registerKeys(self):
        for dev in self.props['devices']:
            self.registerDevice(str(dev))

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        try:
            idx = self.props['devices'].index(dev)
        except ValueError:
            return
        self._curval[idx] = value
        self._curstr[idx] = unitvalue
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        try:
            idx = self.props['devices'].index(dev)
        except ValueError:
            return
        self._curstatus[idx] = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        fontscale = float(self._scale)
        h = self.props['height'] * fontscale
        w = self.props['width'] * fontscale
        posscale = (w - 120) / self.props['posscale']

        if self.props['name']:
            painter.setFont(self.font())
            painter.drawText(QRectF(5, 0, w, fontscale * 2.5),
                             self.props['name'],
                             QTextOption(Qt.AlignmentFlag.AlignCenter))
            yoff = fontscale * 2.5
        else:
            yoff = 0

        painter.setPen(self.color)
        painter.drawEllipse(QRectF(5, 5 + yoff, 50, h))
        painter.drawRect(QRectF(30, 5 + yoff, w - 50, h))
        painter.setPen(QColor('black'))
        painter.drawArc(QRectF(5, 5 + yoff, 50, h), 1440, 2880)
        painter.drawLine(QLineF(30, 5 + yoff, w - 25, 5 + yoff))
        painter.drawLine(QLineF(30, 5 + yoff + h, w - 25, 5 + yoff + h))
        painter.drawEllipse(QRectF(w - 45, 5 + yoff, 50, h))

        # draw Detector 1
        minx = 0
        pos_val = self._curval[0]
        if pos_val is not None:
            pos_status = self._curstatus[0]
            pos_str = self._curstr[0]
            shift_val = self._curval[1]
            shift_status = self._curstatus[1]
            shift_str = self._curstr[1]
            if shift_val > 0:
                shift_str += ' ↓'
            elif shift_val < 0:
                shift_str += ' ↑'
            # Not used at the moment, prepared for later use
            tilt_val = self._curval[2]
            tilt_status = self._curstatus[2]
            tilt_str = self._curstr[2]
            if tilt_str.endswith('deg'):
                tilt_str = tilt_str[:-3] + '°'

            stat = max(pos_status, shift_status, tilt_status)
            painter.setBrush(statusbrush[stat])
            # tf = QTransform()
            # tf.rotate(tilt_val)
            painter.resetTransform()
            painter.translate(60 + pos_val * posscale + fontscale / 2.,
                              15 + yoff + shift_val * posscale + (h - 20) / 2.)
            painter.rotate(-tilt_val)
            painter.drawRect(QRectF(-fontscale / 2., - (h - 20) / 2., fontscale,
                                    h - 20))  # XXX tilt ???
            painter.resetTransform()
            painter.setFont(self.valueFont)
            painter.drawText(QRectF(60 + pos_val * posscale - 10.5 * fontscale,
                                    -5 + yoff + h - fontscale,  # + (shift_val - 4) * posscale,
                                    9.5 * fontscale, 2 * fontscale),
                             tilt_str, QTextOption(Qt.AlignmentFlag.AlignRight))
            painter.drawText(QRectF(60 + pos_val * posscale - 6.5 * fontscale,
                                    yoff + fontscale,  # + (shift_val - 4) * posscale,
                                    9.5 * fontscale, 2 * fontscale),
                             shift_str, QTextOption(Qt.AlignmentFlag.AlignLeft))
            minx = max(minx, 60 + pos_val * posscale + 5 - 4 * fontscale)
            painter.drawText(QRectF(minx, h + 10 + yoff, 8 * fontscale, 30),
                             pos_str, QTextOption(Qt.AlignmentFlag.AlignCenter))
            minx = minx + 8 * fontscale

#        # draw Detector 2
#        pos_val = self._curval[3]
#        if pos_val is not None:
#            pos_status = self._curstatus[3]
#            pos_str = self._curstr[3]
#
#            painter.setBrush(statusbrush[pos_status])
#            painter.drawRect(60 + pos_val * posscale, 15 + yoff,
#                             fontscale, h - 20 - 5 * posscale)
#            painter.setFont(self.valueFont)
#            minx = max(minx, 65 + pos_val * posscale - 4 * fontscale)
#            painter.drawText(minx, h + 10 + yoff,
#                             8 * fontscale, 30, Qt.AlignmentFlag.AlignCenter, pos_str)
#            minx = minx + 8 * fontscale


class BeamOption(NicosWidget, QWidget):

    designer_description = 'SANS-1 beam option'

    def __init__(self, parent, designMode=False):
        self._curstr = ''
        self._curstatus = OK
        self._fixed = ''

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    dev = PropDef('dev', str, '', 'NICOS device name')
    height = PropDef('height', int, 4, 'Widget height in characters')
    width = PropDef('width', int, 10, 'Widget width in characters')
    name = PropDef('name', str, '', 'Display name')

    def sizeHint(self):
        return QSize(round(self.props['width'] * self._scale),
                     round(self.props['height'] * self._scale) +
                     round(self.props['name'] and self._scale * 2.5 or 0))

    def registerKeys(self):
        self.registerDevice(self.props['dev'])

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self._curstr = unitvalue
        self.update()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._fixed = fixed
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self._curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.props['width'] * self._scale
        h = self.props['height'] * self._scale

        if self.props['name']:
            painter.setFont(self.font())
            painter.drawText(QRectF(0, 0, w, self._scale * 2.5),
                             self.props['name'],
                             QTextOption(Qt.AlignmentFlag.AlignCenter))
            yoff = self._scale * 2.5
        else:
            yoff = 0
        painter.setBrush(statusbrush[self._curstatus])
        painter.drawRect(QRectF(2, 2 + yoff, w - 4, h - 4))
        painter.setFont(self.valueFont)
        painter.drawText(QRectF(2, 2 + yoff, w - 4, h - 4),
                         self._curstr, QTextOption(Qt.AlignmentFlag.AlignCenter))


class CollimatorTable(NicosWidget, QWidget):
    """Displays a list of 'beam options' as a vertical stack.

    Options are displayed as vertical stack of named elements drawn on top
    of a centered blue line ('the beam').
    If the device value is in 'options', the correspondig element is drawn
    on top of 'the beam' by moving the whole stack vertically.
    If the device value is in 'disabled_options', the whole
    stack of options is vertically shifted 'out of beam'.
    Other values are ignored as they are considered temporary
    (while moving an option).

    If the device state happens to be in error, the name label is
    displayed in red to indicate the error.
    """

    designer_description = 'SANS-1 collimator table'

    def __init__(self, parent, designMode=False):
        self._curstr = ''
        self._curstatus = OK
        self._fixed = ''
        self.shift = -1

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    dev = PropDef('dev', str, '', 'NICOS device name of a switcher')
    options = PropDef('options', 'QStringList', [], 'list of valid switcher-'
                      'values to display in top-down order (first element '
                      'will be displayed on top location)')
    disabled_options = PropDef('disabled_options', 'QStringList', [],
                               'list of valid switcher values for which '
                               'all options are display out-of-beam')
    height = PropDef('height', int, 4, 'Widget height in characters')
    width = PropDef('width', int, 10, 'Widget width in characters')
    name = PropDef('name', str, '', 'Display name')

    def registerKeys(self):
        self.registerDevice(self.props['dev'])

    def sizeHint(self):
        return QSize(round(self._scale * self.props['width']),
                     round(self._scale * 2.5 * self.props['height']) +
                     round(self.props['name'] and 2.5 * self._scale or 0))

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self._curstr = strvalue
        self.update()

    def on_devMetaChange(self, dev, fmtstr, unit, fixed):
        self._fixed = fixed
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self._curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        h = self._scale * 2.5 * self.props['height']
        w = self._scale * self.props['width']

        # cache pen
        pen = painter.pen()

        if self.props['name']:
            painter.setFont(self.font())
            if self._curstatus != OK:
                painter.fillRect(QRectF(0, 0, w, self._scale * 2.5),
                                 statusbrush[self._curstatus])
            if self._fixed:
                painter.setPen(QPen(_blue.color()))
            else:
                painter.setPen(QPen(_black.color()))
            painter.drawText(QRectF(0, 0, w, self._scale * 2.5),
                             self.props['name'],
                             QTextOption(Qt.AlignmentFlag.AlignCenter))
            painter.setPen(pen)
            yoff = self._scale * 2.5
        else:
            yoff = 0

        painter.setPen(QPen(_blue.color()))

        y = h * 0.5 + yoff
        painter.drawLine(QLineF(0, y, w, y))
        painter.drawLine(QLineF(0, y+1, w, y+1))
        painter.drawLine(QLineF(0, y+2, w, y+2))

        # reset pen
        painter.setPen(pen)

        painter.setBrush(statusbrush[self._curstatus])
        if self._curstr in self.props['options']:
            self.shift = self.props['options'].index(self._curstr)
        if self._curstr in self.props['disabled_options']:
            self.shift = len(self.props['options'])

        painter.setFont(self.valueFont)

        h0 = max(2 * self._scale, 2 * self._scale + 4)
        painter.setClipRect(QRectF(0, yoff, w, h))
        for i, t in enumerate(self.props['options']):
            y = h * 0.5 + yoff + h0 * (self.shift - i - 0.45)
            b = statusbrush[self._curstatus]
            if t == self._curstr:
                painter.setBrush(b)
            else:
                painter.setBrush(_grey if b == statusbrush[OK] else b)
            painter.drawRect(QRectF(5, y + 2, w - 10, h0 - 4))
            painter.drawText(QRectF(5, y + 2, w - 10, h0 - 4),
                             t, QTextOption(Qt.AlignmentFlag.AlignCenter))
