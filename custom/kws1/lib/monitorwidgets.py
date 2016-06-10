#  -*- coding: utf-8 -*-

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QBrush, QColor, QPainter, QWidget
from nicos.core.status import BUSY, ERROR, NOTREACHED, OK, UNKNOWN, WARN
from nicos.guisupport.widget import NicosWidget, PropDef


_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_grey = QBrush(QColor('lightgrey'))
_red = QBrush(QColor('red'))
_olive = QBrush(QColor('olive'))
_orange = QBrush(QColor('#ffa500'))

statusbrush = {
    BUSY: _yellow,
    WARN: _orange,
    ERROR: _red,
    NOTREACHED: _red,
    OK: _white,
    UNKNOWN: _olive,
}


class Tube(NicosWidget, QWidget):

    designer_description = 'KWS-1 tube'

    def __init__(self, parent, designMode=False):
        # z, x, y
        self._curval = [0, 0, 0]
        self._curstr = ['', '', '']
        self._curstatus = [OK, OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    properties = {
        'devices':   PropDef('QStringList', []),
        'height':    PropDef(int, 10),
        'width':     PropDef(int, 30),
        'name':      PropDef(str, ''),
        'posscale':  PropDef(float, 20),
        'color':     PropDef('QColor', _grey.color()),
    }

    def sizeHint(self):
        return QSize(self.props['width'] * self._scale + 10,
                     self.props['height'] * self._scale +
                     (self.props['name'] and self._scale * 2.5 or 0) + 40)

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
        painter.setRenderHint(QPainter.Antialiasing)

        fontscale = float(self._scale)
        h = self.props['height'] * fontscale
        w = self.props['width'] * fontscale
        posscale = (w - 100) / self.props['posscale']

        # Draw name above tube
        if self.props['name']:
            painter.setFont(self.font())
            painter.drawText(5, 0, w, fontscale * 2.5,
                             Qt.AlignCenter, self.props['name'])
            yoff = fontscale * 2.5
        else:
            yoff = 0

        # Draw tube
        painter.setPen(self.color)
        painter.drawEllipse(5, 5 + yoff, 50, h)
        painter.drawRect(30, 5 + yoff, w - 50, h)
        painter.setPen(QColor('black'))
        painter.drawArc(5, 5 + yoff, 50, h, 1440, 2880)
        painter.drawLine(30, 5 + yoff, w - 25, 5 + yoff)
        painter.drawLine(30, 5 + yoff + h, w - 25, 5 + yoff + h)
        painter.drawEllipse(w - 45, 5 + yoff, 50, h)

        # draw detector
        pos_val = self._curval[0]
        if pos_val is not None:
            pos_status = self._curstatus[0]
            pos_str = self._curstr[0]
            x_val = self._curval[1]
            x_status = self._curstatus[1]
            x_str = '%.1f x' % x_val
            y_val = self._curval[2]
            y_status = self._curstatus[2]
            y_str = '%.1f y' % y_val

            stat = max(pos_status, x_status, y_status)
            painter.setBrush(statusbrush[stat])
            painter.setFont(self.valueFont)
            painter.resetTransform()
            # Translate to detector position
            painter.translate(30 + pos_val * posscale + fontscale / 2.,
                              15 + yoff + (h - 20) / 2.)
            painter.drawRect(-fontscale / 2., - (h - 20) / 2., fontscale,
                             h - 20)
            painter.resetTransform()
            # Put X/Y values left or right of detector depending on position
            if pos_val < 14:
                xoff = 2 * fontscale
            else:
                xoff = - 8 * fontscale
            # X translation
            painter.drawText(30 + pos_val * posscale + xoff,
                             yoff + 2 * fontscale,
                             7 * fontscale, 2 * fontscale, Qt.AlignRight,
                             x_str)
            # Y translation
            painter.drawText(30 + pos_val * posscale + xoff,
                             yoff + 3.5 * fontscale,
                             7 * fontscale, 2 * fontscale, Qt.AlignRight,
                             y_str)
            # Z position
            minx = max(0, 30 + pos_val * posscale + 5 - 4 * fontscale)
            painter.drawText(minx,
                             h + 10 + yoff, 8 * fontscale, 30, Qt.AlignCenter,
                             pos_str)
