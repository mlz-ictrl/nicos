#  -*- coding: utf-8 -*-

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED

from nicos.guisupport.widget import DisplayWidget

_magenta = QBrush(QColor('#A12F86'))
_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_black = QBrush(QColor('black'))
_blue = QBrush(QColor('blue'))
_red = QBrush(QColor('red'))

statusbrush = {
    BUSY: _yellow,
    ERROR: _red,
    NOTREACHED: _red,
    OK: _white,
}

class Tube(DisplayWidget, QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        DisplayWidget.__init__(self)

        self.curval = 0
        self.curstr = ''
        self.curstatus = OK

    def sizeHint(self):
        return QSize(self.width + 10, self.height + self.titleheight + 40)

    def setConfig(self, config, labelfont, valuefont, scale):
        self.device = config['dev']
        self.title = config.get('name', '')
        self.labelfont = labelfont
        self.valuefont = valuefont
        self.height = scale * config.get('height', 10)
        self.width = scale * config.get('width', 30)
        self.scale = (self.width - 120.) / (config.get('max', 100))
        self.titleheight = self.title and scale * 2.5 or 0

    def registerKeys(self):
        self.registerDevice(self.device)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.curval = value
        self.curstr = unitvalue
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self.curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.title:
            painter.setFont(self.labelfont)
            painter.drawText(5, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.title)
            yoff = self.titleheight
        else:
            yoff = 0
        painter.setPen(_magenta.color())
        painter.drawEllipse(5, 5 + yoff, 50, self.height)
        painter.drawRect(30, 5 + yoff, self.width - 50, self.height)
        painter.setPen(QColor('black'))
        painter.drawArc(5, 5 + yoff, 50, self.height, 1440, 2880)
        painter.drawLine(30, 5 + yoff, self.width - 25, 5 + yoff)
        painter.drawLine(30, 5 + yoff + self.height, self.width - 25,
                                               5 + yoff + self.height)
        painter.drawEllipse(self.width - 45, 5 + yoff, 50, self.height)

        if self.curval is not None:
            painter.setBrush(statusbrush[self.curstatus])
            painter.drawRect(60 + self.curval*self.scale, 15 + yoff,
                             10, self.height - 20)
            painter.setFont(self.valuefont)
            painter.drawText(60 + self.curval*self.scale + 5 - 100,
                             self.height + 10 + yoff, 200, 30, Qt.AlignCenter,
                             self.curstr)

class Tube2(DisplayWidget, QWidget):
    ''' Sans1Tube with two detectors.... '''

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        DisplayWidget.__init__(self)

        self.curval = []
        self.curstr = []
        self.curstatus = []

    def sizeHint(self):
        return QSize(self.width + 10, self.height + self.titleheight + 40)

    def setConfig(self, config, labelfont, valuefont, scale):
        self.devices = config['dev']
        self.curval = [0] * len(self.devices)
        self.curstr = [''] * len(self.devices)
        self.curstatus = [OK] * len(self.devices)
        self.title = config.get('name', '')
        self.labelfont = labelfont
        self.valuefont = valuefont
        self.fontscale = scale
        self.height = scale * config.get('height', 10)
        self.width = scale * config.get('width', 30)
        self.scale = (self.width - 120.) / (config.get('max', 100))
        self.titleheight = self.title and scale * 2.5 or 0

    def registerKeys(self):
        for dev in self.devices:
            self.registerDevice(dev)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        try:
            idx = self.devices.index(dev)
        except:
            return
        self.curval[idx] = value
        self.curstr[idx] = unitvalue
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        try:
            idx = self.devices.index(dev)
        except:
            return
        self.curstatus[idx] = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.title:
            painter.setFont(self.labelfont)
            painter.drawText(5, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.title)
            yoff = self.titleheight
        else:
            yoff = 0
        painter.setPen(_magenta.color())
        painter.drawEllipse(5, 5 + yoff, 50, self.height)
        painter.drawRect(30, 5 + yoff, self.width - 50, self.height)
        painter.setPen(QColor('black'))
        painter.drawArc(5, 5 + yoff, 50, self.height, 1440, 2880)
        painter.drawLine(30, 5 + yoff, self.width - 25, 5 + yoff)
        painter.drawLine(30, 5 + yoff + self.height, self.width - 25,
                                               5 + yoff + self.height)
        painter.drawEllipse(self.width - 45, 5 + yoff, 50, self.height)

        # draw Detector 1
        minx = 0
        pos_val = self.curval[0]
        if pos_val is not None:
            pos_status = self.curstatus[0]
            pos_str = self.curstr[0]
            shift_val = self.curval[1]
            shift_status = self.curstatus[1]
            shift_str = self.curstr[1]
            # Not used at the moment, prepared for later use
            # tilt_val = self.curval[2]
            tilt_status = self.curstatus[2]
            tilt_str = self.curstr[2]
            if tilt_str.endswith('deg'):
                tilt_str = tilt_str[:-3]+u'°'

            stat = max(pos_status, shift_status, tilt_status)
            painter.setBrush(statusbrush[stat])
            painter.drawRect(60 + pos_val * self.scale, 15 + yoff + shift_val * self.scale,
                             self.fontscale, self.height - 20 - 4*self.scale) #XXX tilt ???
            painter.setFont(self.valuefont)
            painter.drawText(60 + pos_val * self.scale - 10.5 * self.fontscale,
                             -5 + yoff + (shift_val - 4) * self.scale + self.height - self.fontscale,
                             10 * self.fontscale, 2 * self.fontscale, Qt.AlignRight, tilt_str)
            painter.drawText(60 + pos_val * self.scale + 1.5 * self.fontscale,
                             -5 + yoff + (shift_val - 4) * self.scale + self.height - self.fontscale,
                             10 * self.fontscale, 2 * self.fontscale, Qt.AlignLeft, shift_str)
            minx = max(minx, 60 + pos_val * self.scale + 5 - 4 * self.fontscale)
            painter.drawText(minx,
                             self.height + 10 + yoff, 8 * self.fontscale, 30, Qt.AlignCenter,
                             pos_str)
            minx = minx + 8 * self.fontscale

        # draw Detector 2
        pos_val = self.curval[3]
        if pos_val is not None:
            pos_status = self.curstatus[3]
            pos_str = self.curstr[3]

            painter.setBrush(statusbrush[pos_status])
            painter.drawRect(60 + pos_val * self.scale, 15 + yoff,
                             self.fontscale, self.height - 20 - 5 * self.scale)
            painter.setFont(self.valuefont)
            minx = max(minx, 65 + pos_val * self.scale - 4 * self.fontscale)
            painter.drawText(minx, self.height + 10 + yoff,
                             8 * self.fontscale, 30, Qt.AlignCenter, pos_str)
            minx = minx + 8 * self.fontscale

class BeamOption(DisplayWidget, QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        DisplayWidget.__init__(self)

        self.curstr = ''
        self.curstatus = OK

    def setConfig(self, config, labelfont, valuefont, scale):
        self.device = config['dev']
        self.title = config.get('name', '')
        self.labelfont = labelfont
        self.valuefont = valuefont
        self.height = scale * config.get('height', 4)
        self.width = scale * config.get('width', 10)
        self.titleheight = config.get('name') and scale * 2.5 or 0

    def registerKeys(self):
        self.registerDevice(self.device)

    def sizeHint(self):
        return QSize(self.width, self.height + self.titleheight)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.curstr = unitvalue
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self.curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.title:
            painter.setFont(self.labelfont)
            painter.drawText(0, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.title)
            yoff = self.titleheight
        else:
            yoff = 0
        painter.setBrush(statusbrush[self.curstatus])
        painter.drawRect(2, 2 + yoff, self.width - 4, self.height - 4)
        painter.setFont(self.valuefont)
        painter.drawText(2, 2 + yoff, self.width - 4, self.height - 4,
                         Qt.AlignCenter, self.curstr)

class CollimatorTable(DisplayWidget, QWidget):

    scale = 1
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        DisplayWidget.__init__(self)

        self.curstr = ''
        self.curstatus = OK

    def setConfig(self, config, labelfont, valuefont, scale):
        self.device = config['dev']
        self.options = config['options']        # list of possible positions
        self.title = config.get('name', '')
        self.labelfont = labelfont
        self.valuefont = valuefont
        self.scale = scale
        self.height = scale * 2.5 * config.get('height', 3)
        self.width = scale * config.get('width', 10)
        self.titleheight = config.get('name') and scale * 2.5 or 0

    def registerKeys(self):
        self.registerDevice(self.device)

    def sizeHint(self):
        return QSize(self.width, self.height + self.titleheight)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.curstr = unitvalue
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self.curstatus = code
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.title:
            painter.setFont(self.labelfont)
            if self.curstatus != OK:
                painter.fillRect(0, 0, self.width, self.titleheight, statusbrush[self.curstatus])
            painter.drawText(0, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.title)
            yoff = self.titleheight
        else:
            yoff = 0

        painter.setBrush(_blue)
        y = self.height * 0.5 + yoff
        painter.drawLine(0, y, self.width, y)
        painter.drawLine(0, y+1, self.width, y+1)
        painter.drawLine(0, y+2, self.width, y+2)

        painter.setBrush(statusbrush[self.curstatus])
        try:
            p = self.options.index( self.curstr )
        except:
            p = 0

        painter.setFont(self.valuefont)

        h = max( 2.5*self.scale, 2*self.scale + 4 )
        painter.setClipRect(0, yoff, self.width, self.height )
        for i,t in enumerate( self.options ):
            y = self.height * 0.5 + yoff + h * (p - i - 0.45)
            painter.drawRect(5, y + 2, self.width - 10, h - 4 )
            painter.drawText(5, y + 2, self.width - 10, h - 4,
                             Qt.AlignCenter, t)
