from PyQt4.QtCore import QSize, Qt
from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED

from nicos.guisupport.widget import DisplayWidget

_magenta = QBrush(QColor('#A12F86'))
_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
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
