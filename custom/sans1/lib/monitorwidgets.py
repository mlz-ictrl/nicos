from PyQt4.QtCore import SIGNAL, QSize, Qt
from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED

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


class Tube(QWidget):

    def __init__(self, parent, main, field):
        QWidget.__init__(self, parent)
        self.field = field
        self.labelfont = main._labelfont
        self.valuefont = main._valuefont
        self.height = main._onechar * field.height
        self.width = main._onechar * field.width
        self.scale = (self.width - 120.) / (field.max or 100)
        self.titleheight = self.field.name and main._onechar * 2.5 or 0

        self.curval = 0
        self.curstr = ''
        self.curstatus = OK
        self.connect(self, SIGNAL('newValue'), self.on_newValue)
        self.connect(self, SIGNAL('statusChanged'), self.on_statusChanged)

    def sizeHint(self):
        return QSize(self.width + 10, self.height + self.titleheight + 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.field.name:
            painter.setFont(self.labelfont)
            painter.drawText(5, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.field.name)
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

        painter.setBrush(statusbrush[self.curstatus])
        painter.drawRect(60 + self.curval*self.scale, 15 + yoff,
                         10, self.height - 20)
        painter.setFont(self.valuefont)
        painter.drawText(60 + self.curval*self.scale + 5 - 100,
                         self.height + 10 + yoff, 200, 30, Qt.AlignCenter,
                         self.curstr + ' ' + self.field.unit)

    def on_newValue(self, time, value, strvalue):
        self.curval = value
        self.curstr = strvalue
        self.update()

    def on_statusChanged(self, status):
        self.curstatus = status
        self.update()


class BeamOption(QWidget):

    def __init__(self, parent, main, field):
        QWidget.__init__(self, parent)
        self.field = field
        self.labelfont = main._labelfont
        self.valuefont = main._valuefont
        self.height = main._onechar * field.height
        self.width = main._onechar * field.width
        self.titleheight = self.field.name and main._onechar * 2.5 or 0

        self.curstr = ''
        self.curstatus = OK
        self.connect(self, SIGNAL('newValue'), self.on_newValue)
        self.connect(self, SIGNAL('statusChanged'), self.on_statusChanged)
        self.connect(self, SIGNAL('expireChanged'), self.on_expireChanged)

    def sizeHint(self):
        return QSize(self.width, self.height + self.titleheight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(_magenta)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.field.name:
            painter.setFont(self.labelfont)
            painter.drawText(0, 0, self.width, self.titleheight, Qt.AlignCenter,
                             self.field.name)
            yoff = self.titleheight
        else:
            yoff = 0
        painter.setBrush(statusbrush[self.curstatus])
        painter.drawRect(2, 2 + yoff, self.width - 4, self.height - 4)
        painter.setFont(self.valuefont)
        painter.drawText(2, 2 + yoff, self.width - 4, self.height - 4,
                         Qt.AlignCenter, self.curstr)

    def on_newValue(self, time, value, strvalue):
        self.curstr = strvalue
        self.update()

    def on_statusChanged(self, status):
        self.curstatus = status
        self.update()

    def on_expireChanged(self, expired):
        if expired:
            self.curstr = ''
        self.update()
