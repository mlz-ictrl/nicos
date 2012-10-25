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

from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
     QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
     QCursor, QStackedWidget, QPen, QBrush
from PyQt4.QtCore import QSize, QVariant, Qt, SIGNAL

try:
    from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotGrid, QwtLegend
    from nicos.gui.plothelpers import TimeScaleEngine, TimeScaleDraw
except (ImportError, RuntimeError):
    QwtPlot = None

from nicos.monitor import Monitor as BaseMonitor
from nicos.core.status import statuses


class MonitorWindow(QMainWindow):
    def keyPressEvent(self, event):
        if event.text() == 'q':
            self.close()
        return QMainWindow.keyPressEvent(self, event)

class SMLabel(QLabel):
    """A label with default event handlers for setting text and colors."""
    def __init__(self, text, parent):
        QLabel.__init__(self, text, parent)
        self.connect(self, SIGNAL('settext'), self.setText)
        self.connect(self, SIGNAL('setcolors'), self.setColors)
    def setColors(self, fore, back):
        pal = self.palette()
        if fore is not None:
            pal.setColor(QPalette.WindowText, fore)
        if back is not None:
            pal.setColor(QPalette.Window, back)
        self.setPalette(pal)

class SensitiveLabel(SMLabel):
    """A label that calls back when entered/left by the mouse."""
    def __init__(self, text, parent, enter, leave):
        SMLabel.__init__(self, text, parent)
        self._enter = enter
        self._leave = leave
    def enterEvent(self, event):
        self._enter(self, event)
    def leaveEvent(self, event):
        self._leave(self, event)

if QwtPlot:
    class SMPlot(QwtPlot):
        colors = [Qt.red, Qt.green, Qt.blue, Qt.magenta, Qt.cyan, Qt.darkGray]
        def __init__(self, parent, interval, minv=None, maxv=None):
            QwtPlot.__init__(self, parent)
            self.ncurves = 0
            self.interval = interval
            self.minv = minv
            self.maxv = maxv

            self.setAxisScaleEngine(QwtPlot.xBottom, TimeScaleEngine())
            showdate = interval > 24*3600
            showsecs = interval < 300
            self.setAxisScaleDraw(QwtPlot.xBottom,
                TimeScaleDraw(showdate=showdate, showsecs=showsecs))
            self.setAxisLabelAlignment(QwtPlot.xBottom,
                                       Qt.AlignBottom | Qt.AlignLeft)
            self.setAxisLabelRotation(QwtPlot.xBottom, -45)

            grid = QwtPlotGrid()
            grid.setPen(QPen(QBrush(Qt.gray), 1, Qt.DotLine))
            grid.attach(self)

            self.legend = QwtLegend(self)
            self.legend.setMidLineWidth(100)
            self.insertLegend(self.legend, QwtPlot.TopLegend)

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

            self.connect(self, SIGNAL('updateplot'), self.updateplot)

        def setFont(self, font):
            QwtPlot.setFont(self, font)
            self.legend.setFont(font)
            self.setAxisFont(QwtPlot.yLeft, font)
            self.setAxisFont(QwtPlot.xBottom, font)

        def addcurve(self, title):
            curve = QwtPlotCurve(title)
            curve.setPen(QPen(self.colors[self.ncurves % 6], 2))
            self.ncurves += 1
            curve.attach(self)
            curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
            self.legend.find(curve).setIdentifierWidth(30)
            return curve

        def updateplot(self, field, curve):
            ll = len(field['plotx'])
            i = 0
            limit = currenttime() - self.interval
            while i < ll and field['plotx'][i] < limit:
                i += 1
            xx = field['plotx'] = field['plotx'][i:]
            yy = field['ploty'] = field['ploty'][i:]
            curve.setData(xx, yy)
            if self.mincurve:
                self.mincurve.setData([xx[0], xx[-1]], [self.minv, self.minv])
            if self.maxcurve:
                self.maxcurve.setData([xx[0], xx[-1]], [self.maxv, self.maxv])
            self.replot()


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

    def initColors(self):
        self._bgcolor = QColor('gray')
        self._black = QColor('black')
        self._yellow = QColor('yellow')
        self._green = QColor('#00ff00')
        self._red = QColor('red')
        self._gray = QColor('gray')
        self._white = QColor('white')

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

        master.setWindowTitle(self.title)
        self._bgcolor = master.palette().color(QPalette.Window)

        timefont  = QFont(self.font, self._fontsizebig + self._fontsize)
        blockfont = QFont(self.font, self._fontsizebig)
        labelfont = QFont(self.font, self._fontsize)
        stbarfont = QFont(self.font, int(self._fontsize * 0.8))
        valuefont = QFont(self.valuefont or self.font, self._fontsize)

        onechar = QFontMetrics(valuefont).width('0')
        blheight = QFontMetrics(blockfont).height()
        tiheight = QFontMetrics(timefont).height()

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = QFrame(master)
        masterlayout = QVBoxLayout()
        self._timelabel = SMLabel('', master)
        self._timelabel.setFont(timefont)
        self.setForeColor(self._timelabel, self._gray)
        self._timelabel.setAutoFillBackground(True)
        self._timelabel.setAlignment(Qt.AlignHCenter)
        self._timelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        masterlayout.addWidget(self._timelabel)
        masterlayout.addSpacing(0.2 * tiheight)

        self._stacker = QStackedWidget(masterframe)
        masterlayout.addWidget(self._stacker)
        displayframe = QFrame(self._stacker)
        self._stacker.addWidget(displayframe)

        self._plots = {}

        def _create_field(groupframe, field):
            self.updateKeymap(field)

            fieldlayout = QVBoxLayout()

            if field['plot'] and QwtPlot:
                w = self._plots.get(field['plot'])
                if w:
                    field['plotcurve'] = w.addcurve(field['name'])
                    return
                w = SMPlot(groupframe, field['plotinterval'],
                           field['min'], field['max'])
                self._plots[field['plot']] = w
                w.setFont(labelfont)
                field['plotcurve'] = w.addcurve(field['name'])
            else:
                # deactivate plot if QwtPlot unavailable
                field['plot'] = None
                # now put describing label and view label into subframe
                nl = SMLabel(' ' + escape(field['name']) + ' ', groupframe)
                if field['unit']:
                    self.setLabelUnitText(nl, field['name'], field['unit'])
                nl.setFont(labelfont)
                nl.setAlignment(Qt.AlignHCenter)
                nl.setAutoFillBackground(True)
                nl.setTextFormat(Qt.RichText)
                field['namelabel'] = nl
                fieldlayout.addWidget(nl)

                w = SensitiveLabel('----', groupframe,
                                   self._label_entered, self._label_left)
                if field['istext']:
                    w.setFont(labelfont)
                else:
                    w.setFont(valuefont)
                    w.setAlignment(Qt.AlignHCenter)
                w.setFrameShape(QFrame.Panel)
                w.setFrameShadow(QFrame.Sunken)
                w.setAutoFillBackground(True)
                w.setLineWidth(2)
                w.setMinimumSize(QSize(onechar * (field['width'] + .5), 0))
                w.setProperty('assignedField', QVariant(field))
                field['valuelabel'] = w

            tmplayout = QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(w)
            tmplayout.addStretch()
            fieldlayout.addLayout(tmplayout)

            return fieldlayout

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
                    block[0]['labelframe'] = blockbox
                    for row in block[1]:
                        if row is None:
                            blocklayout.addSpacing(12)
                        else:
                            rowlayout = QHBoxLayout()
                            rowlayout.addStretch()
                            rowlayout.addSpacing(self._padding)
                            for field in row:
                                fieldframe = _create_field(blockbox, field)
                                if fieldframe:
                                    rowlayout.addLayout(fieldframe)
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

    def setLabelText(self, label, text):
        label.emit(SIGNAL('settext'), text)

    def setLabelUnitText(self, label, text, unit, fixed=''):
        label.emit(SIGNAL('settext'), escape(text) + ' <font color="#888888">%s'
                   '</font><font color="#0000ff">%s</font> ' %
                   (escape(unit), fixed))

    def setForeColor(self, label, fore):
        label.emit(SIGNAL('setcolors'), fore, None)

    def setBackColor(self, label, back):
        label.emit(SIGNAL('setcolors'), None, back)

    def setBothColors(self, label, fore, back):
        label.emit(SIGNAL('setcolors'), fore, back)

    def updatePlot(self, field):
        curve = field['plotcurve']
        curve.plot().emit(SIGNAL('updateplot'), field, curve)

    def switchWarnPanel(self, off=False):
        if self._stacker.currentIndex() == 1 or off:
            self._warnpanel.emit(SIGNAL('setindex'), 0)
        else:
            self._warnpanel.emit(SIGNAL('setindex'), 1)

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

    # special feature: mouse-over status bar text

    def _label_entered(self, widget, event):
        field = widget.property('assignedField').toPyObject()
        statustext = '%s = %s' % (field['name'], field['valuelabel'].text())
        if field['unit']:
            statustext += ' %s' % field['unit']
        if field['status']:
            try:
                const, msg = field['status']
            except ValueError:
                const, msg = field['status'], ''
            statustext += ', status is %s: %s' % (statuses.get(const, '?'), msg)
        if field['changetime']:
            statustext += ', changed %s ago' % (
                nicedelta(currenttime() - field['changetime']))
        self._statuslabel.setText(statustext)
        self._statustimer = threading.Timer(1, lambda:
                                            self._label_entered(widget, event))
        self._statustimer.start()

    def _label_left(self, widget, event):
        self._statuslabel.setText('')
        if self._statustimer:
            self._statustimer.cancel()
            self._statustimer = None
