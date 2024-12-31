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
#
# *****************************************************************************

from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QBrush, QColor, QLineF, QPainter, QPen, \
    QRectF, QSize, Qt, QTextOption, QWidget
from nicos.guisupport.utils import scaledFont
from nicos.guisupport.widget import NicosWidget, PropDef

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
    DISABLED: _white,
    OK: _white,
    UNKNOWN: _olive,
}


class Tube(NicosWidget, QWidget):

    designer_description = 'KWS tube'

    devices = PropDef('devices', 'QStringList', [])
    height = PropDef('height', int, 10, 'Widget height in characters')
    width = PropDef('width', int, 30, 'Widget width in characters')
    name = PropDef('name', str, '')
    posscale = PropDef('posscale', float, 20)
    color = PropDef('color', 'QColor', _grey.color())
    beamstop = PropDef('beamstop', bool, False,
                       'Beamstop instead of detector Y/Z')
    smalldet = PropDef('smalldet', float, 0, 'Positioning of small detector, '
                       'or zero for no small detector')

    def __init__(self, parent, designMode=False):
        # z, x, y, small_x, small_y
        self._curval = [0, 0, 0, 0, 0]
        self._curstr = ['', '', '', '', '']
        self._curstatus = [OK, OK, OK, OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    def sizeHint(self):
        return QSize(round(self.props['width'] * self._scale) + 10,
                     round(self.props['height'] * self._scale) +
                     round(self.props['smalldet'] and 50 or 0) +
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
        posscale = (w - 100) / self.props['posscale']

        # Draw name above tube
        if self.props['name']:
            painter.setFont(self.font())
            painter.drawText(QRectF(5, 0, w, fontscale * 2.5),
                             self.props['name'],
                             QTextOption(Qt.AlignmentFlag.AlignCenter))
            yoff = fontscale * 2.5
        elif self.props['smalldet']:
            yoff = 50
        else:
            yoff = 0

        # Draw tube
        painter.setPen(self.color)
        painter.drawEllipse(QRectF(5, 5 + yoff, 50, h))
        painter.drawRect(QRectF(30, 5 + yoff, w - 50, h))
        painter.setPen(QColor('black'))
        painter.drawArc(QRectF(5, 5 + yoff, 50, h), 1440, 2880)
        painter.drawLine(QLineF(30, 5 + yoff, w - 25, 5 + yoff))
        painter.drawLine(QLineF(30, 5 + yoff + h, w - 25, 5 + yoff + h))
        painter.drawEllipse(QRectF(w - 45, 5 + yoff, 50, h))

        if self.props['smalldet']:
            sw = 20
            sx = 30 + self.props['smalldet'] * posscale
            painter.setPen(self.color)
            painter.drawRect(QRectF(sx - sw, 2, 2*sw, yoff + 10))
            painter.setPen(QColor('black'))
            painter.drawLine(QLineF(sx - sw, 5 + yoff, sx - sw, 2))
            painter.drawLine(QLineF(sx - sw, 2, sx + sw, 2))
            painter.drawLine(QLineF(sx + sw, 2, sx + sw, 5 + yoff))

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
            xp = 30 + pos_val * posscale
            painter.translate(xp + fontscale / 2., 15 + yoff + (h - 20) / 2.)
            painter.drawRect(QRectF(-fontscale / 2., - (h - 20) / 2., fontscale,
                                    h - 20))
            painter.resetTransform()
            # Put X/Y values left or right of detector depending on position
            if pos_val < 14:
                xoff = 2 * fontscale
            else:
                xoff = - 8.5 * fontscale
            # X translation
            painter.drawText(QRectF(xp + xoff, yoff + 2 * fontscale,
                                    7 * fontscale, 2 * fontscale), x_str,
                             QTextOption(Qt.AlignmentFlag.AlignRight))
            # Y translation
            painter.drawText(QRectF(xp + xoff, yoff + 3.5 * fontscale,
                                    7 * fontscale, 2 * fontscale), y_str,
                             QTextOption(Qt.AlignmentFlag.AlignRight))
            # Z position
            minx = max(0, xp + 5 - 4 * fontscale)
            painter.drawText(QRectF(minx, h + 10 + yoff, 8 * fontscale, 30),
                             pos_str, QTextOption(Qt.AlignmentFlag.AlignCenter))

            # draw beamstop
            if self.props['beamstop']:
                painter.setPen(QPen(_blue.color()))
                painter.drawRect(
                    QRectF(xp - 8, yoff + 15 + posscale / 350 * (1100 - y_val),
                           2, 10))

        # draw small detector
        if self.props['smalldet'] and self._curval[4] is not None:
            x_status = self._curstatus[3]
            x_str = '%4.1f x' % self._curval[3]
            y_status = self._curstatus[4]
            y_val = self._curval[4]
            y_str = '%4.0f y' % y_val
            stat = max(x_status, y_status)

            painter.setBrush(statusbrush[stat])
            painter.setPen(QPen(_black.color()))
            painter.setFont(self.valueFont)
            sy = 10 + y_val * posscale / 250
            painter.drawRect(QRectF(sx - fontscale / 2., sy, fontscale, 30))

            painter.drawText(QRectF(sx - 10.5 * fontscale, sy,
                                    8 * fontscale, 2 * fontscale), x_str,
                             QTextOption(Qt.AlignmentFlag.AlignRight))
            painter.drawText(QRectF(sx - 10.5 * fontscale, sy + 1.5 * fontscale,
                                    8 * fontscale, 2 * fontscale), y_str,
                             QTextOption(Qt.AlignmentFlag.AlignRight))


collstatusbrush = {
    BUSY: _yellow,
    WARN: _orange,
    ERROR: _red,
    NOTREACHED: _red,
    DISABLED: _white,
    OK: _green,
    UNKNOWN: _olive,
}


class Collimation(NicosWidget, QWidget):

    designer_description = 'KWS collimation'

    devices = PropDef('devices', 'QStringList', [])
    height = PropDef('height', int, 4)
    width = PropDef('width', int, 10)
    polarizer = PropDef('polarizer', int, 0, 'Number of bits for the polarizer')

    def __init__(self, parent, designMode=False):
        # coll_in, coll_out, ap_20, ap_14, ap_8, ap_4, ap_2, pol_in, pol_out
        self._curval = [0, 0, (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), 0, 0]
        self._curstr = ['', '', '', '', '', '', '', '', '']
        self._curstatus = [OK, OK, OK, OK, OK, OK, OK, OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    def registerKeys(self):
        for dev in self.props['devices']:
            self.registerDevice(str(dev))

    def sizeHint(self):
        return QSize(round(self._scale * self.props['width']),
                     round(self._scale * self.props['height'] * 1.2))

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = painter.pen()

        fontscale = float(self._scale)
        painter.setFont(scaledFont(self.valueFont, 0.9))
        h = self.props['height'] * fontscale
        w = self.props['width'] * fontscale
        elwidth = w / 20.
        elheight = h / 3

        pol_bits = self.props['polarizer']
        is_in = int(self._curval[0] << pol_bits | self._curval[7])
        is_out = int(self._curval[1] << pol_bits | self._curval[8])
        x = elwidth
        y = 2.5 * fontscale
        for i in range(18):
            painter.setPen(QPen(_black.color()))
            painter.setBrush(_grey)
            painter.drawRect(QRectF(x, y, elwidth - 2, elheight))
            painter.setBrush(_blue)
            if is_in & (1 << (17 - i)):
                ely = 3
            elif is_out & (1 << (17 - i)):
                ely = 2 + elheight / 2
            else:
                ely = 2 + elheight / 4
            painter.drawRect(QRectF(x + 3, y + ely, elwidth - 8, elheight / 3))
            if i >= 18-pol_bits:
                painter.setPen(QPen(_white.color()))
                painter.drawText(QRectF(x + 3, y + ely - 2,
                                        elwidth - 8, elheight / 3 + 2), 'POL',
                                 QTextOption(Qt.AlignmentFlag.AlignHCenter))
                painter.setPen(QPen(_black.color()))
            painter.drawText(QRectF(x, 3, elwidth, 2 * fontscale),
                             str(19 - i),
                             QTextOption(Qt.AlignmentFlag.AlignRight |
                                         Qt.AlignmentFlag.AlignTop))
            x += elwidth
        painter.fillRect(QRectF(0, y + elheight / 3 - 5, w, 3), _yellow)
        painter.setPen(pen)

        x = elwidth + 1
        y += elheight + 4

        slhw = 1.6 * elwidth
        for i, slitpos in enumerate([20, 14, 8, 4, 2]):
            slitw, slith = self._curval[2 + i]
            xmiddle = x + ((20 - slitpos) * elwidth)
            painter.drawLine(QLineF(xmiddle, y, xmiddle, y + 15))
            painter.setBrush(_white)
            painter.drawRect(QRectF(xmiddle - 0.5 * slhw, y + 15, slhw, slhw))
            painter.setBrush(collstatusbrush[self._curstatus[2 + i]])
            w = (50 - slitw) * slhw / 100
            h = (50 - slith) * slhw / 100
            painter.drawRect(QRectF(xmiddle - 0.5 * slhw + w, y + 15 + h,
                                    slhw - 2 * w, slhw - 2 * h))
            painter.drawText(QRectF(xmiddle - 0.8 * elwidth, y + 15, slhw, slhw),
                             '%.1f\n%.1f' % (slitw, slith),
                             QTextOption(Qt.AlignmentFlag.AlignCenter))


class Lenses(NicosWidget, QWidget):

    designer_description = 'KWS lenses'

    def __init__(self, parent, designMode=False):
        # lens_in, lens_out
        self._curval = [0, 0]
        self._curstr = ['', '']
        self._curstatus = [OK, OK]

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    devices = PropDef('devices', 'QStringList', [])
    height = PropDef('height', int, 4)
    width = PropDef('width', int, 10)

    def registerKeys(self):
        for dev in self.props['devices']:
            self.registerDevice(str(dev))

    def sizeHint(self):
        return QSize(round(self._scale * self.props['width']),
                     round(self._scale * self.props['height']))

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(_black.color()))
        painter.setBrush(_grey)

        fontscale = float(self._scale)
        h = self.props['height'] * fontscale
        w = self.props['width'] * fontscale
        painter.drawRect(QRectF(2, 10, w - 4, h / 2))

        is_in = int(self._curval[0])
        is_out = int(self._curval[1])
        lensheight = h / 2 - 25
        lensw = w / 32
        for (i, n, x) in [(0, 4, 0), (1, 6, 6), (2, 16, 14)]:
            if is_in & (1 << i):
                lensy = 22
            elif is_out & (1 << i):
                lensy = h / 2 + 20
            else:
                lensy = h / 4 + 22
            for j in range(n):
                painter.drawRect(QRectF((1 + x + j) * lensw, lensy,
                                        lensw + 1, lensheight))


class SampleSlit(NicosWidget, QWidget):

    designer_description = 'KWS sample slit'

    def __init__(self, parent, designMode=False):
        self._curval = [0, 0, 0, 0]
        self._curstatus = OK
        self._opmode = 'offcentered'

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    device = PropDef('device', str, '')
    maxh = PropDef('maxh', float, 30)
    maxw = PropDef('maxw', float, 30)
    height = PropDef('height', int, 4)
    width = PropDef('width', int, 10)

    def registerKeys(self):
        self.registerDevice(str(self.props['device']))
        self.registerKey('%s/opmode' % self.props['device'])

    def sizeHint(self):
        return QSize(round(self._scale * self.props['width']),
                     round(self._scale * self.props['height']))

    def on_keyChange(self, key, value, time, expired):
        if key.endswith('/opmode'):
            self._opmode = value
            return
        NicosWidget.on_keyChange(self, key, value, time, expired)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self._curval = value
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self._curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        fontscale = float(self._scale)
        ww = self.props['width'] * fontscale - 4
        wh = self.props['height'] * fontscale - 4
        sx, sy = self.props['maxw'], self.props['maxh']

        if self._opmode == 'offcentered':
            dx, dy, w, h = self._curval
            x0, x1, y0, y1 = dx - w/2., dx + w/2., dy - h/2., dy + h/2.
            l1, l2, l3, l4 = '(%.1f, %.1f)' % (dx, dy), '%.1f x %.1f' % (w, h), '', ''
        elif self._opmode == 'centered':
            w, h = self._curval
            x0, x1, y0, y1 = -w/2., w/2., -h/2., h/2.
            l1, l2, l3, l4 = '', '%.1f x %.1f' % (w, h), '', ''
        elif self._opmode.startswith('4blades'):
            x0, x1, y0, y1 = self._curval
            l1, l2, l3, l4 = '%.1f' % y1, '%.1f' % y0, '%.1f' % x0, '%.1f' % x1
            if self._opmode.endswith('opposite'):
                x0 *= -1
                y0 *= -1

        x0 = (x0 + sx/2) / sx * ww
        x1 = (x1 + sx/2) / sx * ww
        y0 = wh - (y0 + sy/2) / sy * wh
        y1 = wh - (y1 + sy/2) / sy * wh

        painter.setPen(QPen(_black.color()))
        painter.setBrush(_white)
        painter.drawRect(QRectF(2, 2, ww, wh))
        painter.setBrush(collstatusbrush[self._curstatus])
        painter.drawRect(QRectF(2 + x0, 2 + y1, x1 - x0, y0 - y1))

        painter.setFont(scaledFont(self.valueFont, 0.8))
        painter.drawText(QRectF(2, 2, ww, wh), l1,
                         QTextOption(Qt.AlignmentFlag.AlignTop |
                                     Qt.AlignmentFlag.AlignHCenter))
        painter.drawText(QRectF(2, 2, ww, wh), l2,
                         QTextOption(Qt.AlignmentFlag.AlignBottom |
                                     Qt.AlignmentFlag.AlignHCenter))
        painter.drawText(QRectF(2, 2, ww, wh), l3,
                         QTextOption(Qt.AlignmentFlag.AlignVCenter |
                                     Qt.AlignmentFlag.AlignLeft))
        painter.drawText(QRectF(2, 2, ww, wh), l4,
                         QTextOption(Qt.AlignmentFlag.AlignVCenter |
                                     Qt.AlignmentFlag.AlignRight))
