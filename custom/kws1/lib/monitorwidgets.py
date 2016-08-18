#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.widget import NicosWidget, PropDef

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QBrush, QColor, QPainter, QWidget, QPen, QFont
from nicos.core.status import BUSY, ERROR, NOTREACHED, OK, UNKNOWN, WARN


_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_grey = QBrush(QColor('lightgrey'))
_red = QBrush(QColor('red'))
_olive = QBrush(QColor('olive'))
_orange = QBrush(QColor('#ffa500'))
_black = QBrush(QColor('black'))
_blue = QBrush(QColor('blue'))
_green = QBrush(QColor('#00cc00'))

statusbrush = {
    BUSY: _yellow,
    WARN: _orange,
    ERROR: _red,
    NOTREACHED: _red,
    OK: _white,
    UNKNOWN: _olive,
}


class Tube(NicosWidget, QWidget):

    designer_description = 'KWS tube'

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


collstatusbrush = {
    BUSY: _yellow,
    WARN: _orange,
    ERROR: _red,
    NOTREACHED: _red,
    OK: _green,
    UNKNOWN: _olive,
}


class Collimation(NicosWidget, QWidget):

    designer_description = 'KWS collimation'

    def __init__(self, parent, designMode=False):
        # coll_in, coll_out, ap_20, ap_14, ap_8, ap_4, ap_2
        self._curval = [0, 0, (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        self._curstr = ['', '', '', '', '', '', '']
        self._curstatus = [OK, OK, OK, OK, OK, OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    properties = {
        'devices':   PropDef('QStringList', []),
        'height':    PropDef(int, 4),
        'width':     PropDef(int, 10),
    }

    def registerKeys(self):
        for dev in self.props['devices']:
            self.registerDevice(str(dev))

    def sizeHint(self):
        return QSize(self._scale * self.props['width'],
                     self._scale * self.props['height'] * 1.2)

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
        painter.setRenderHint(QPainter.Antialiasing)
        pen = painter.pen()

        fontscale = float(self._scale)
        smallerfont = QFont(self.valueFont)
        smallerfont.setPointSizeF(smallerfont.pointSizeF() * 0.9)
        painter.setFont(smallerfont)
        h = self.props['height'] * fontscale
        w = self.props['width'] * fontscale
        elwidth = w / 20.
        elheight = h / 3

        is_in = int(self._curval[0])
        is_out = int(self._curval[1])
        x = elwidth
        y = 2.5 * fontscale
        for i in range(18):
            painter.setPen(QPen(_black.color()))
            painter.setBrush(_grey)
            painter.drawRect(x, y, elwidth - 2, elheight)
            painter.setBrush(_blue)
            if is_in & (1 << (17 - i)):
                ely = 3
            elif is_out & (1 << (17 - i)):
                ely = 2 + elheight / 2
            else:
                ely = 2 + elheight / 4
            painter.drawRect(x + 3, y + ely, elwidth - 8, elheight / 3)
            painter.drawText(x, 3,
                             elwidth, 2 * fontscale,
                             Qt.AlignRight | Qt.AlignTop,
                             str(19 - i))
            x += elwidth
        painter.fillRect(0, y + elheight / 3 - 5, w, 3, _yellow)
        painter.setPen(pen)

        x = elwidth + 1
        y += elheight + 4

        slhw = 1.6 * elwidth
        for i, slitpos in enumerate([20, 14, 8, 4, 2]):
            slitw, slith = self._curval[2 + i]
            xmiddle = x + ((20 - slitpos) * elwidth)
            painter.drawLine(xmiddle, y, xmiddle, y + 15)
            painter.setBrush(_white)
            painter.drawRect(xmiddle - 0.5 * slhw, y + 15, slhw, slhw)
            painter.setBrush(collstatusbrush[self._curstatus[2 + i]])
            w = (50 - slitw) * slhw / 100
            h = (50 - slith) * slhw / 100
            painter.drawRect(xmiddle - 0.5 * slhw + w, y + 15 + h,
                             slhw - 2 * w, slhw - 2 * h)
            painter.drawText(xmiddle - 0.8 * elwidth, y + 15, slhw, slhw,
                             Qt.AlignCenter | Qt.AlignHCenter,
                             '%.1f\n%.1f' % (slitw, slith))
