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

"""Qt version of instrument monitor."""

__version__ = "$Revision$"

import threading
from cgi import escape
from time import time as currenttime, sleep

from PyQt4.QtCore import QSize, QVariant, QTimer, Qt, SIGNAL
from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
     QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
     QCursor, QStackedWidget, QPen, QBrush, QWidget

try:
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtLegend, \
         QwtPlotZoomer
    from nicos.clients.gui.plothelpers import TimeScaleEngine, TimeScaleDraw
except (ImportError, RuntimeError):
    QwtPlot = QWidget

from nicos.services.monitor import Monitor as BaseMonitor
from nicos.core.status import statuses
from nicos.core.status import OK, BUSY, ERROR, PAUSED, NOTREACHED


class MonitorWindow(QMainWindow):
    def keyPressEvent(self, event):
        if event.text() == 'q':
            self.close()
        return QMainWindow.keyPressEvent(self, event)


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


def labelunittext(name, unit, fixed):
    return escape(name) + ' <font color="#888888">%s</font>' \
        '<font color="#0000ff">%s</font> ' % (escape(unit), fixed)


class SMDefaultDisplay(QWidget):
    """Default value display widget with two labels."""
    def __init__(self, parent, main, field):
        QWidget.__init__(self, parent)
        self.maxlen = field.maxlen
        self.field = field
        self.main = main

        layout = QVBoxLayout()
        namelabel = QLabel(' ' + escape(field.name) + ' ', self)
        if field.unit:
            namelabel.setText(labelunittext(field.name, field.unit, field.fixed))
        namelabel.setFont(main._labelfont)
        namelabel.setAlignment(Qt.AlignHCenter)
        namelabel.setAutoFillBackground(True)
        namelabel.setTextFormat(Qt.RichText)
        self.namelabel = namelabel

        valuelabel = SensitiveSMLabel('----', self, self._label_entered,
                                      self._label_left)
        if field.istext:
            valuelabel.setFont(main._labelfont)
        else:
            valuelabel.setFont(main._valuefont)
            valuelabel.setAlignment(Qt.AlignHCenter)
        valuelabel.setFrameShape(QFrame.Panel)
        valuelabel.setFrameShadow(QFrame.Sunken)
        valuelabel.setAutoFillBackground(True)
        valuelabel.setLineWidth(2)
        valuelabel.setMinimumSize(QSize(main._onechar * (field.width + .5), 0))
        valuelabel.setProperty('assignedField', QVariant(field))
        self.valuelabel = valuelabel

        layout.addWidget(namelabel)
        tmplayout = QHBoxLayout()
        tmplayout.addStretch()
        tmplayout.addWidget(valuelabel)
        tmplayout.addStretch()
        layout.addLayout(tmplayout)
        self.setLayout(layout)

        self.connect(self, SIGNAL('newValue'), self.on_newValue)
        self.connect(self, SIGNAL('metaChanged'), self.on_metaChanged)
        self.connect(self, SIGNAL('statusChanged'), self.on_statusChanged)
        self.connect(self, SIGNAL('expireChanged'), self.on_expireChanged)
        self.connect(self, SIGNAL('rangeChanged'), self.on_rangeChanged)

    def on_newValue(self, field, time, value, strvalue):
        self.valuelabel.setText(strvalue[:self.maxlen])

    def on_metaChanged(self, field):
        self.namelabel.setText(labelunittext(self.field.name, self.field.unit,
                                             self.field.fixed))

    def on_statusChanged(self, field, status):
        pal = self.valuelabel.palette()
        if status == OK:
            pal.setColor(QPalette.WindowText, self.main._green)
        elif status in (BUSY, PAUSED):
            pal.setColor(QPalette.WindowText, self.main._yellow)
        elif status in (ERROR, NOTREACHED):
            pal.setColor(QPalette.WindowText, self.main._red)
        else:
            pal.setColor(QPalette.WindowText, self.main._white)
        self.valuelabel.setPalette(pal)

    def on_expireChanged(self, field, expired):
        pal = self.valuelabel.palette()
        if expired:
            pal.setColor(QPalette.Window, self.main._gray)
        else:
            pal.setColor(QPalette.Window, self.main._black)
        self.valuelabel.setPalette(pal)

    def on_rangeChanged(self, field, inout):
        pal = self.namelabel.palette()
        if inout == 0:
            pal.setColor(QPalette.Window, self.main._bgcolor)
        else:
            pal.setColor(QPalette.Window, self.main._red)
        self.namelabel.setPalette(pal)

    def _label_entered(self, widget, event):
        field = self.field
        statustext = '%s = %s' % (field.name, self.valuelabel.text())
        if field.unit:
            statustext += ' %s' % field.unit
        if field.status:
            try:
                const, msg = field.status
            except ValueError:
                const, msg = field.status, ''
            statustext += ', status is %s: %s' % (statuses.get(const, '?'), msg)
        if field.changetime:
            statustext += ', changed %s ago' % (
                nicedelta(currenttime() - field.changetime))
        self.main._statuslabel.setText(statustext)
        self.main._statustimer = threading.Timer(1,
            lambda: self._label_entered(widget, event))
        self.main._statustimer.start()

    def _label_left(self, widget, event):
        self.main._statuslabel.setText('')
        if self.main._statustimer:
            self.main._statustimer.cancel()
            self.main._statustimer = None


class SMPlot(QwtPlot):
    colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.magenta, Qt.cyan, Qt.darkGray]

    def __init__(self, parent, interval, minv=None, maxv=None):
        QwtPlot.__init__(self, parent)
        self.ncurves = 0
        self.interval = interval
        self.minv = minv
        self.maxv = maxv
        self.ctimers = {}
        self.plotcurves = {}
        self.plotx = {}
        self.ploty = {}

        # appearance setup
        self.setCanvasBackground(Qt.white)

        # axes setup
        self.setAxisScaleEngine(QwtPlot.xBottom, TimeScaleEngine())
        showdate = interval > 24*3600
        showsecs = interval < 300
        self.setAxisScaleDraw(QwtPlot.xBottom,
            TimeScaleDraw(showdate=showdate, showsecs=showsecs))
        self.setAxisLabelAlignment(QwtPlot.xBottom,
                                   Qt.AlignBottom | Qt.AlignLeft)
        self.setAxisLabelRotation(QwtPlot.xBottom, -45)

        # subcomponents: grid, legend, zoomer
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.gray), 1, Qt.DotLine))
        grid.attach(self)
        self.legend = QwtLegend(self)
        self.legend.setMidLineWidth(100)
        self.insertLegend(self.legend, QwtPlot.TopLegend)
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())

        # additional curves setup
        self.mincurve = self.maxcurve = None
        if self.minv is not None:
            self.mincurve = QwtPlotCurve()
            self.mincurve.setItemAttribute(QwtPlotCurve.AutoScale, 0)
            self.mincurve.setItemAttribute(QwtPlotCurve.Legend, 0)
            self.mincurve.attach(self)
        if self.maxv is not None:
            self.maxcurve = QwtPlotCurve()
            self.maxcurve.setItemAttribute(QwtPlotCurve.AutoScale, 0)
            self.maxcurve.setItemAttribute(QwtPlotCurve.Legend, 0)
            self.maxcurve.attach(self)

        self.connect(self, SIGNAL('newValue'), self.on_newValue)
        self.connect(self, SIGNAL('updateplot'), self.updateplot)

    def setFont(self, font):
        QwtPlot.setFont(self, font)
        self.legend.setFont(font)
        self.setAxisFont(QwtPlot.yLeft, font)
        self.setAxisFont(QwtPlot.xBottom, font)

    def addcurve(self, field, title):
        curve = QwtPlotCurve(title)
        curve.setPen(QPen(self.colors[self.ncurves % 6], 2))
        self.ncurves += 1
        curve.attach(self)
        curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.legend.find(curve).setIdentifierWidth(30)
        self.ctimers[curve] = QTimer()
        self.ctimers[curve].setSingleShot(True)

        self.plotcurves[field] = curve
        self.plotx[field] = []
        self.ploty[field] = []

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            if self.plotx[field]:
                self.plotx[field].append(currenttime())
                self.ploty[field].append(self.ploty[field][-1])
                self.emit(SIGNAL('updateplot'), field, curve)
        self.connect(self.ctimers[curve], SIGNAL('timeout()'), update)

    def updateplot(self, field, curve):
        xx, yy = self.plotx[field], self.ploty[field]
        ll = len(xx)
        i = 0
        limit = currenttime() - self.interval
        while i < ll and xx[i] < limit:
            i += 1
        xx = self.plotx[field] = xx[i:]
        yy = self.ploty[field] = yy[i:]
        curve.setData(xx, yy)
        if self.mincurve:
            self.mincurve.setData([xx[0], xx[-1]], [self.minv, self.minv])
        if self.maxcurve:
            self.maxcurve.setData([xx[0], xx[-1]], [self.maxv, self.maxv])
        if self.zoomer.zoomRect() == self.zoomer.zoomBase():
            self.zoomer.setZoomBase(True)
        else:
            self.replot()
        self.ctimers[curve].start(5000)

    def on_newValue(self, field, time, value, strvalue):
        self.plotx[field].append(time)
        self.ploty[field].append(value)
        curve = self.plotcurves[field]
        self.updateplot(field, curve)


class BlockBox(QFrame):
    """Provide the equivalent of a Tk LabelFrame: a group box that has a
    definite frame around it.
    """
    def __init__(self, parent, text, font):
        QFrame.__init__(self, parent)
        self._label = QLabel(' ' + text + ' ', parent)
        self._label.setAutoFillBackground(True)
        self._label.setFont(font)
        self._label.resize(self._label.sizeHint())
        self._label.show()
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.connect(self, SIGNAL('enableDisplay'), self.enableDisplay)
    def moveEvent(self, event):
        self._repos()
        return QFrame.moveEvent(self, event)
    def resizeEvent(self, event):
        self._repos()
        return QFrame.resizeEvent(self, event)
    def _repos(self):
        mps = self.pos()
        msz = self.size()
        lsz = self._label.size()
        self._label.move(mps.x() + 0.5*(msz.width() - lsz.width()),
                         mps.y() - 0.5*lsz.height())
    def enableDisplay(self, layout, isvis):
        QFrame.setVisible(self, isvis)
        self._label.setVisible(isvis)
        if not isvis:
            layout.removeWidget(self)
        else:
            layout.insertWidget(1, self)

def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class Monitor(BaseMonitor):
    """Qt specific implementation of instrument monitor."""

    def mainLoop(self):
        self._qtapp.exec_()

    def closeGui(self):
        self._master.close()

    def _class_import(self, clsname):
        modname, member = clsname.rsplit('.', 1)
        mod = __import__(modname, None, None, [member])
        return getattr(mod, member)

    def initGui(self):
        self._qtapp = QApplication(['qtapp', '-style', 'windows'])
        self._master = master = MonitorWindow()
        master.show()

        if self._geometry == 'fullscreen':
            master.showFullScreen()
            QCursor.setPos(master.geometry().bottomRight())
        elif isinstance(self._geometry, tuple):
            w, h, x, y = self._geometry
            master.setGeometry(x, y, w, h)

        self._bgcolor = QColor('gray')
        self._black = QColor('black')
        self._yellow = QColor('yellow')
        self._green = QColor('#00ff00')
        self._red = QColor('red')
        self._gray = QColor('gray')
        self._white = QColor('white')

        master.setWindowTitle(self.title)
        self._bgcolor = master.palette().color(QPalette.Window)

        timefont  = QFont(self.font, self._fontsizebig + self._fontsize)
        blockfont = QFont(self.font, self._fontsizebig)
        self._labelfont = QFont(self.font, self._fontsize)
        stbarfont = QFont(self.font, int(self._fontsize * 0.8))
        self._valuefont = QFont(self.valuefont or self.font, self._fontsize)

        self._onechar = QFontMetrics(self._valuefont).width('0')
        blheight = QFontMetrics(blockfont).height()
        tiheight = QFontMetrics(timefont).height()

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = QFrame(master)
        masterlayout = QVBoxLayout()
        self._titlelabel = QLabel('', master)
        self._titlelabel.setFont(timefont)
        pal = self._titlelabel.palette()
        pal.setColor(QPalette.WindowText, self._gray)
        self._titlelabel.setPalette(pal)
        self._titlelabel.setAutoFillBackground(True)
        self._titlelabel.setAlignment(Qt.AlignHCenter)
        self._titlelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        masterframe.connect(self._titlelabel, SIGNAL('updatetitle'),
                            self._titlelabel.setText)

        masterlayout.addWidget(self._titlelabel)
        masterlayout.addSpacing(0.2 * tiheight)

        self._stacker = QStackedWidget(masterframe)
        masterlayout.addWidget(self._stacker)
        displayframe = QFrame(self._stacker)
        self._stacker.addWidget(displayframe)

        self._plots = {}

        def _create_field(groupframe, field):
            if isinstance(field, tuple):
                widget_class = self._class_import(field[0])
                instance = widget_class(groupframe, self, field[1], field[2])
                for f in field[2].itervalues():
                    f._widget = instance
                return instance
            if field.widget:
                widget_class = self._class_import(field.widget)
                instance = widget_class(groupframe, self, field)
                field._widget = instance
                return instance
            elif field.plot and (QwtPlot is not QWidget):
                plotwidget = self._plots.get(field.plot)
                if plotwidget:
                    field._widget = plotwidget
                    plotwidget.addcurve(field, field.name)
                    return None
                plotwidget = SMPlot(groupframe, field.plotinterval,
                                    field.min, field.max)
                field._widget = plotwidget
                self._plots[field.plot] = plotwidget
                plotwidget.setFont(self._labelfont)
                plotwidget.setMinimumSize(QSize(self._onechar * (field.width + .5),
                                                self._onechar * (field.height + .5)))
                plotwidget.addcurve(field, field.name)
                return plotwidget
            else:
                # deactivate plot if QwtPlot unavailable
                if field.plot:
                    self.log.warning('cannot create plots, Qwt5 unavailable')
                    field.plot = None
                display = SMDefaultDisplay(groupframe, self, field)
                field._widget = display
                return display

        # now iterate through the layout and create the widgets to display it
        displaylayout = QVBoxLayout()
        displaylayout.setSpacing(20)
        for superrow in self._layout:
            boxlayout = QHBoxLayout()
            boxlayout.setSpacing(20)
            boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = QVBoxLayout()
                columnlayout.setSpacing(blheight * 0.8)
                for block in column:
                    blocklayout_outer = QHBoxLayout()
                    blocklayout_outer.addStretch()
                    blocklayout = QVBoxLayout()
                    blocklayout.addSpacing(0.5 * blheight)
                    blockbox = BlockBox(displayframe, block[0]['name'],
                                        blockfont)
                    for row in block[1]:
                        if row is None:
                            blocklayout.addSpacing(12)
                        else:
                            rowlayout = QHBoxLayout()
                            rowlayout.addStretch()
                            rowlayout.addSpacing(self._padding)
                            for field in row:
                                fieldwidget = _create_field(blockbox, field)
                                if fieldwidget:
                                    rowlayout.addWidget(fieldwidget)
                                    rowlayout.addSpacing(self._padding)
                            rowlayout.addStretch()
                            blocklayout.addLayout(rowlayout)
                    if block[0]['only']:
                        self._onlymap.setdefault(block[0]['only'], []).\
                            append((blocklayout_outer, blockbox))
                    blocklayout.addSpacing(0.3 * blheight)
                    blockbox.setLayout(blocklayout)
                    blocklayout_outer.addWidget(blockbox)
                    blocklayout_outer.addStretch()
                    columnlayout.addLayout(blocklayout_outer)
                    columnlayout.addStretch()
                columnlayout.addStretch()
                boxlayout.addLayout(columnlayout)
            displaylayout.addLayout(boxlayout)
        displayframe.setLayout(displaylayout)

        self._warnpanel = QFrame(self._stacker)
        self._stacker.addWidget(self._warnpanel)
        master.connect(self._warnpanel, SIGNAL('setindex'),
                       self._stacker.setCurrentIndex)

        warningslayout = QVBoxLayout()
        lbl = QLabel('Warnings', self._warnpanel)
        lbl.setAlignment(Qt.AlignHCenter)
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        lbl.setFont(timefont)
        warningslayout.addWidget(lbl)
        self._warnlabel = QLabel('', self._warnpanel)
        self._warnlabel.setFont(blockfont)
        warningslayout.addWidget(self._warnlabel)
        warningslayout.addStretch()
        self._warnpanel.setLayout(warningslayout)

        masterframe.setLayout(masterlayout)
        master.setCentralWidget(masterframe)

        def resizeToMinimum():
            master.resize(master.sizeHint())
            if self._geometry == 'fullscreen':
                master.showFullScreen()
        master.connect(master, SIGNAL('resizeToMinimum'), resizeToMinimum)

        # initialize status bar
        self._statuslabel = QLabel()
        self._statuslabel.setFont(stbarfont)
        master.statusBar().addWidget(self._statuslabel)
        self._statustimer = None

    def signal(self, field, signal, *args):
        field._widget.emit(SIGNAL(signal), field, *args)

    def updateTitle(self, title):
        self._titlelabel.emit(SIGNAL('updatetitle'), title)

    def switchWarnPanel(self, off=False):
        if self._stacker.currentIndex() == 1 or off:
            self._warnpanel.emit(SIGNAL('setindex'), 0)
            if off:
                pal = self._titlelabel.palette()
                pal.setColor(QPalette.WindowText, self._gray)
                pal.setColor(QPalette.Window, self._bgcolor)
                self._titlelabel.setPalette(pal)
        else:
            self._warnpanel.emit(SIGNAL('setindex'), 1)
            pal = self._titlelabel.palette()
            pal.setColor(QPalette.WindowText, self._black)
            pal.setColor(QPalette.Window, self._red)
            self._titlelabel.setPalette(pal)
            self._warnlabel.setText(self._currwarnings)

    def reconfigureBoxes(self):
        for setup, boxes in self._onlymap.iteritems():
            for layout, blockbox in boxes:
                if setup.startswith('!'):
                    enabled = setup[1:] not in self._setups
                else:
                    enabled = setup in self._setups
                blockbox.emit(SIGNAL('enableDisplay'), layout, enabled)
        # HACK: master.sizeHint() is only correct a certain time *after* the
        # layout change (I've not found out what event to generate or intercept
        # to do this in a more sane way).
        def emitresize():
            sleep(1)
            self._master.emit(SIGNAL('resizeToMinimum'))
        threading.Thread(target=emitresize, name='emitresize').start()
