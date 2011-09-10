#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""NICOS GUI history log window."""

__version__ = "$Revision$"

import time

from PyQt4.QtCore import Qt, QSize, QDateTime, SIGNAL
from PyQt4.Qwt5 import QwtPlot, QwtText, QwtSymbol, QwtLegend, QwtPlotItem, \
     QwtPlotZoomer, QwtPlotGrid, QwtPicker, QwtPlotPicker, QwtPlotCurve, \
     QwtLog10ScaleEngine, QwtLinearScaleEngine, QwtScaleDraw
from PyQt4.QtGui import QDialog, QPalette, QFont, QPen, QBrush, \
     QListWidgetItem, QFileDialog, QPrintDialog, QPrinter, QToolBar, QMenu, \
     QStatusBar, QSizePolicy
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi, dialogFromUi
from nicos.gui.plothelpers import XPlotPicker

TIMEFMT = '%Y-%m-%d %H:%M:%S'


class TimeScaleDraw(QwtScaleDraw):
    def label(self, value, strf=time.strftime, local=time.localtime):
        return QwtText(strf('%y-%m-%d\n%H:%M:%S', local(value)))


class View(object):
    def __init__(self, name, keys, interval, fromtime, totime, client):
        self.name = name
        self.keys = keys
        self.interval = interval
        self.fromtime = fromtime
        self.totime = totime

        if self.fromtime is not None:
            self.keydata = {}
            totime = self.totime or time.time()
            for key in keys:
                x, y = [], []
                self.keydata[key] = x, y
                history = client.ask('gethistory', key,
                                     str(self.fromtime), str(totime))
                if history is None:
                    return # XXX what to do?
                ltime = 0
                interval = self.interval
                for vtime, value in history:
                    if value is not None and vtime > ltime + interval:
                        x.append(vtime)
                        y.append(value)
                        ltime = vtime
        else:
            self.keydata = dict((key, [[], []]) for key in keys)

        self.listitem = None
        self.plot = None

    def newValue(self, time, key, op, value):
        if op != '=':
            return
        kd = self.keydata[key]
        if kd[0] and kd[0][-1] > time - self.interval:
            return
        kd[0].append(time)
        kd[1].append(value)


class HistoryPanel(Panel):
    panelName = 'History viewer'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'history.ui')

        self.statusBar = QStatusBar(self)
        self.statusBar.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)
        self.user_color = parent.user_color
        self.user_font = parent.user_font

        self.views = []
        # stack of views to display
        self.viewStack = []
        # maps watched keys to their views
        self.keyviews = {}
        # current plot object
        self.currentPlot = None

        self.splitter.restoreState(self.splitterstate)
        self.connect(self.client, SIGNAL('cache'), self.on_client_cache)

        self.enablePlotActions(False)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter').toByteArray()

    def setCustomStyle(self, font, back):
        self.user_font = font
        self.user_color = back

        for view in self.views:
            if view.plot:
                view.plot.setCanvasBackground(back)
                view.plot.replot()

        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        for view in self.views:
            if view.plot:
                view.plot.setFonts(font, bold, larger)

    def enablePlotActions(self, on):
        for action in [
            self.actionPDF, self.actionPrint, self.actionCloseView,
            self.actionDeleteView, self.actionResetView,
            self.actionUnzoom, self.actionLogScale, self.actionLegend
            ]:
            action.setEnabled(on)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addAction(self.actionPDF)
        menu.addAction(self.actionPrint)
        menu.addAction(self.actionCloseView)
        menu.addAction(self.actionDeleteView)
        menu.addAction(self.actionResetView)
        menu.addSeparator()
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLegend)
        menu.addSeparator()
        return [menu]

    def getToolbars(self):
        bar = QToolBar('History viewer')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionCloseView)
        return [bar]

    def on_client_cache(self, (time, key, op, value)):
        if key not in self.keyviews:
            return
        for view in self.keyviews[key]:
            view.newValue(time, key, op, value)
            if view.plot:
                view.plot.pointsAdded(key)

    def on_viewList_currentItemChanged(self, item, previous):
        if item is None:
            return
        for view in self.views:
            if view.listitem == item:
                self.openView(view)

    def on_viewList_itemClicked(self, item):
        # this handler is needed in addition to currentItemChanged
        # since one can't change the current item if it's the only one
        self.on_viewList_currentItemChanged(item, None)

    @qtsig('')
    def on_actionNew_triggered(self):
        newdlg = dialogFromUi(self, 'history_new.ui')
        newdlg.fromdate.setDateTime(QDateTime.currentDateTime())
        newdlg.todate.setDateTime(QDateTime.currentDateTime())
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        keys = str(newdlg.devices.text()).split(',')
        if not keys:
            return
        keys = [key if '/' in key else key + '/value'
                for key in keys]
        name = str(newdlg.namebox.text())
        if not name:
            name = ', '.join(keys)
        try:
            interval = float(newdlg.interval.text())
        except ValueError:
            interval = 5.0
        if newdlg.frombox.isChecked():
            fromtime = time.mktime(time.localtime(
                newdlg.fromdate.dateTime().toTime_t()))
        else:
            fromtime = None
        if newdlg.tobox.isChecked():
            totime = time.mktime(time.localtime(
                newdlg.todate.dateTime().toTime_t()))
        else:
            totime = None
        view = View(name, keys, interval, fromtime, totime, self.client)
        self.views.append(view)
        view.listitem = QListWidgetItem(name, self.viewList)
        self.openView(view)
        if totime is None:
            for key in keys:
                self.keyviews.setdefault(key, []).append(view)

    def openView(self, view):
        if not view.plot:
            view.plot = ViewPlot(self.plotFrame, self, view)
        self.viewList.setCurrentItem(view.listitem)
        self.setCurrentView(view)

    def setCurrentView(self, view):
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
        if view is None:
            self.currentPlot = None
            self.enablePlotActions(False)
        else:
            self.currentPlot = view.plot
            try: self.viewStack.remove(view)
            except ValueError: pass
            self.viewStack.append(view)

            self.enablePlotActions(True)
            self.viewList.setCurrentItem(view.listitem)
            self.actionLogScale.setChecked(
                isinstance(view.plot.axisScaleEngine(QwtPlot.yLeft),
                           QwtLog10ScaleEngine))
            self.actionLegend.setChecked(view.plot.legend() is not None)
            self.plotLayout.addWidget(view.plot)
            view.plot.show()

    @qtsig('')
    def on_actionCloseView_triggered(self):
        view = self.viewStack.pop()
        if self.viewStack:
            self.setCurrentView(self.viewStack[-1])
        else:
            self.setCurrentView(None)
        view.plot = None

    @qtsig('')
    def on_actionResetView_triggered(self):
        view = self.viewStack.pop()
        view.plot = None
        self.openView(view)

    @qtsig('')
    def on_actionDeleteView_triggered(self):
        view = self.viewStack.pop()
        self.views.remove(view)
        if self.viewStack:
            self.setCurrentView(self.viewStack[-1])
        else:
            self.setCurrentView(None)
        for i in range(self.viewList.count()):
            if self.viewList.item(i) == view.listitem:
                self.viewList.takeItem(i)
                break
        if view.totime is None:
            for key in view.keys:
                self.keyviews[key].remove(view)

    @qtsig('')
    def on_actionPDF_triggered(self):
        filename = str(QFileDialog.getSaveFileName(
            self, 'Select file name', '', 'PDF files (*.pdf)'))
        if filename == '':
            return
        if '.' not in filename:
            filename += '.pdf'
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName(filename)
        printer.setCreator('NICOS')
        color = self.currentPlot.canvasBackground()
        self.currentPlot.setCanvasBackground(Qt.white)
        self.currentPlot.print_(printer)
        self.currentPlot.setCanvasBackground(color)
        self.statusBar.showMessage('View successfully saved to %s.' % filename)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.currentPlot.print_(printer)
        self.statusBar.showMessage('View successfully printed to %s.' %
                                   str(printer.printerName()))

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.currentPlot.zoomer.zoom(0)

    @qtsig('bool')
    def on_actionLogScale_toggled(self, on):
        self.currentPlot.setAxisScaleEngine(QwtPlot.yLeft,
                                            on and QwtLog10ScaleEngine()
                                            or QwtLinearScaleEngine())
        self.currentPlot.setAxisScaleEngine(QwtPlot.yRight,
                                            on and QwtLog10ScaleEngine()
                                            or QwtLinearScaleEngine())
        self.currentPlot.replot()

    @qtsig('bool')
    def on_actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)


class ViewPlot(QwtPlot):
    def __init__(self, parent, window, view):
        QwtPlot.__init__(self, parent)
        self.view = view
        self.window = window
        self.curves = []

        font = self.window.font() # XXX userFont
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        self.setFonts(font, bold, larger)

        self.symbol = QwtSymbol(QwtSymbol.Ellipse, QBrush(),
                                QPen(), QSize(6, 6))

        # setup zooming and unzooming
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())
        self.zoomer.initMousePattern(3)

        # setup picking and mouse tracking of coordinates
        self.picker = XPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                                  QwtPicker.PointSelection |
                                  QwtPicker.DragSelection,
                                  QwtPlotPicker.NoRubberBand,
                                  QwtPicker.AlwaysOff,
                                  self.canvas())

        # XXX self.setCanvasBackground(self.window.userColor)
        self.canvas().setMouseTracking(True)
        self.connect(self.picker, SIGNAL('moved(const QPoint &)'),
                     self.on_picker_moved)

        self.updateDisplay()

        self.setLegend(True)
        self.connect(self, SIGNAL('legendClicked(QwtPlotItem*)'),
                     self.on_legendClicked)

    def setFonts(self, font, bold, larger):
        self.setFont(font)
        self.titleLabel().setFont(larger)
        self.setAxisFont(QwtPlot.yLeft, font)
        self.setAxisFont(QwtPlot.yRight, font)
        self.setAxisFont(QwtPlot.xBottom, font)
        self.axisTitle(QwtPlot.xBottom).setFont(bold)
        self.axisTitle(QwtPlot.yLeft).setFont(bold)
        self.axisTitle(QwtPlot.yRight).setFont(bold)
        self.labelfont = bold
        #self.disabledfont = QFont(font)
        #self.disabledfont.setStrikeOut(True)

    def updateDisplay(self):
        self.clear()
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.lightGray), 1, Qt.DotLine))
        grid.attach(self)

        self.setTitle('<h3>%s</h3>' % self.view.name)
        xaxistext = QwtText('time')
        xaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.xBottom, xaxistext)
        self.setAxisScaleDraw(QwtPlot.xBottom, TimeScaleDraw())
        yaxisname = 'value'
        yaxistext = QwtText(yaxisname)
        yaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.yLeft, yaxistext)

        self.curves = []
        for i, key in enumerate(self.view.keys):
            self.addCurve(i, key)

        # XXX for now
        self.setAxisAutoScale(QwtPlot.xBottom)
        #self.setAxisScale(QwtPlot.xBottom, xscale[0], xscale[1])
        # needed for zoomer base
        self.setAxisAutoScale(QwtPlot.yLeft)
        self.zoomer.setZoomBase(True)   # does a replot

    curvecolor = [Qt.black, Qt.red, Qt.green, Qt.blue,
                  Qt.magenta, Qt.cyan, Qt.darkGray]
    numcolors = len(curvecolor)

    def addCurve(self, i, key, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = QwtPlotCurve(key)
        plotcurve.setPen(pen)
        plotcurve.setSymbol(self.symbol)
        plotcurve.setRenderHint(QwtPlotItem.RenderAntialiased)
        x, y = self.view.keydata[key]
        plotcurve.setData(np.array(x), np.array(y))
        plotcurve.attach(self)
        if self.legend():
            item = self.legend().find(plotcurve)
            if not plotcurve.isVisible():
                #item.setFont(self.disabledfont)
                item.text().setText('(' + item.text().text() + ')')
        self.curves.append(plotcurve)
        if replot:
            self.zoomer.setZoomBase(True)

    def pointsAdded(self, whichkey):
        for key, plotcurve in zip(self.view.keys, self.curves):
            if key == whichkey:
                x, y = self.view.keydata[key]
                plotcurve.setData(np.array(x), np.array(y))
                self.replot()
                return

    def setLegend(self, on):
        if on:
            legend = QwtLegend(self)
            legend.setItemMode(QwtLegend.ClickableItem)
            # XXX legend.palette().setColor(QPalette.Base, self.window.userColor)
            legend.setBackgroundRole(QPalette.Base)
            self.insertLegend(legend, QwtPlot.BottomLegend)
            for curve in self.curves:
                if not curve.isVisible():
                    #legend.find(curve).setFont(self.disabledfont)
                    itemtext = legend.find(curve).text()
                    itemtext.setText('(' + itemtext.text() + ')')
        else:
            self.insertLegend(None)

    def on_legendClicked(self, item):
        legenditemtext = self.legend().find(item).text()
        if item.isVisible():
            item.setVisible(False)
            #legenditem.setFont(self.disabledfont)
            legenditemtext.setText('(' + legenditemtext.text() + ')')
        else:
            item.setVisible(True)
            #legenditem.setFont(self.font())
            legenditemtext.setText(legenditemtext.text())
        self.replot()

    def on_picker_moved(self, point):
        info = "X = %g, Y = %g" % (
            self.invTransform(QwtPlot.xBottom, point.x()),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)
