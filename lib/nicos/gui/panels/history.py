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

"""NICOS GUI history log window."""

__version__ = "$Revision$"

import os
import time
import tempfile

from PyQt4.QtCore import Qt, QDateTime, SIGNAL
from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtLog10ScaleEngine, \
     QwtLinearScaleEngine
from PyQt4.QtGui import QDialog, QFont, QPen, QListWidgetItem, QFileDialog, \
     QPrintDialog, QPrinter, QToolBar, QMenu, QStatusBar, QSizePolicy, QImage
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi, dialogFromUi, safeFilename
from nicos.gui.plothelpers import NicosPlot
from nicos.cache.utils import cache_load


class View(object):
    def __init__(self, name, keys, interval, fromtime, totime,
                 yfrom, yto, client):
        self.name = name
        self.keys = keys
        self.interval = interval
        self.fromtime = fromtime
        self.totime = totime
        self.yfrom = yfrom
        self.yto = yto

        if self.fromtime is not None:
            self.keydata = {}
            totime = self.totime or time.time()
            for key in keys:
                history = client.ask('gethistory', key,
                                     str(self.fromtime), str(totime))
                if history is None:
                    print 'Error getting history.'
                    history = []
                ltime = 0
                interval = self.interval
                x, y = np.zeros(len(history)), np.zeros(len(history))
                i = 0
                for vtime, value in history:
                    if value is not None and vtime > ltime + interval:
                        x[i] = vtime
                        y[i] = value
                        i += 1
                        ltime = vtime
                x.resize((2*i,)); y.resize((2*i,))
                self.keydata[key] = [x, y, i]
        else:
            self.keydata = dict((key, [np.zeros(1000), np.zeros(1000), 0])
                                for key in keys)

        self.listitem = None
        self.plot = None

    def newValue(self, time, key, op, value):
        if op != '=':
            return
        kd = self.keydata[key]
        n = kd[2]
        if n and kd[0][n-1] > time - self.interval:
            return
        # double array size if array is full
        if n == kd[0].shape[0]:
            kd[0].resize((2*kd[0].shape[0],))
            kd[1].resize((2*kd[0].shape[0],))
        # fill next entry
        kd[0][n] = time
        kd[1][n] = value
        kd[2] += 1


class HistoryPanel(Panel):
    panelName = 'History viewer'

    # XXX save history views when closing?

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'history.ui', 'panels')

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
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

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

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
            self.actionPDF, self.actionPrint, self.actionAttachElog,
            self.actionCloseView, self.actionDeleteView, self.actionResetView,
            self.actionUnzoom, self.actionLogScale, self.actionLegend,
            self.actionSymbols, self.actionLines
            ]:
            action.setEnabled(on)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addSeparator()
        menu.addAction(self.actionPDF)
        menu.addAction(self.actionPrint)
        menu.addAction(self.actionAttachElog)
        menu.addSeparator()
        menu.addAction(self.actionCloseView)
        menu.addAction(self.actionDeleteView)
        menu.addAction(self.actionResetView)
        menu.addSeparator()
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLegend)
        menu.addAction(self.actionSymbols)
        menu.addAction(self.actionLines)
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
        bar.addAction(self.actionDeleteView)
        return [bar]

    def on_client_cache(self, (time, key, op, value)):
        if key not in self.keyviews:
            return
        value = cache_load(value)
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
        helptext = 'Enter a comma-separated list of device names or ' \
            'parameters (as "device.parameter").  Example:\n\n' \
            'T, T.setpoint\n\nshows the value of device T, and the value ' \
            'of the T.setpoint parameter.'
        newdlg = dialogFromUi(self, 'history_new.ui', 'panels')
        newdlg.fromdate.setDateTime(QDateTime.currentDateTime())
        newdlg.todate.setDateTime(QDateTime.currentDateTime())
        newdlg.connect(newdlg.helpButton, SIGNAL('clicked()'),
                       lambda: self.showInfo(helptext))
        newdlg.customYFrom.setEnabled(False)
        newdlg.customYTo.setEnabled(False)
        def callback(on):
            newdlg.customYFrom.setEnabled(on)
            newdlg.customYTo.setEnabled(on)
            if on: newdlg.customYFrom.setFocus()
        newdlg.connect(newdlg.customY, SIGNAL('toggled(bool)'), callback)
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        parts = [part.strip().lower().replace('.', '/')
                 for part in str(newdlg.devices.text()).split(',')]
        if not parts:
            return
        keys = [part if '/' in part else part + '/value' for part in parts]
        name = str(newdlg.namebox.text())
        if not name:
            name = str(newdlg.devices.text())
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
        if newdlg.customY.isChecked():
            try:
                yfrom = float(str(newdlg.customYFrom.text()))
            except ValueError:
                return self.showError('You have to input valid y axis limits.')
            try:
                yto = float(str(newdlg.customYTo.text()))
            except ValueError:
                return self.showError('You have to input valid y axis limits.')
        else:
            yfrom = yto = None
        view = View(name, keys, interval, fromtime, totime, yfrom, yto,
                    self.client)
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
            self.actionSymbols.setChecked(view.plot.hasSymbols)
            self.actionLines.setChecked(view.plot.hasLines)
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
    def on_actionAttachElog_triggered(self):
        newdlg = dialogFromUi(self, 'plot_attach.ui', 'panels')
        newdlg.filename.setText(
            safeFilename('history_%s.png' % self.currentPlot.view.name))
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        descr = str(newdlg.description.text())
        fname = str(newdlg.filename.text())
        img = QImage(800, 600, QImage.Format_RGB32)
        img.fill(0xffffff)
        self.currentPlot.print_(img)
        h, pathname = tempfile.mkstemp('.png')
        os.close(h)
        img.save(pathname, 'png')
        self.client.ask('eval', 'LogAttach(%r, [%r], [%r])' %
                        (descr, pathname, fname))

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

    @qtsig('bool')
    def on_actionSymbols_toggled(self, on):
        self.currentPlot.setSymbols(on)

    @qtsig('bool')
    def on_actionLines_toggled(self, on):
        self.currentPlot.setLines(on)


class ViewPlot(NicosPlot):
    def __init__(self, parent, window, view):
        self.view = view
        self.hasSymbols = True
        self.hasLines = True
        NicosPlot.__init__(self, parent, window, timeaxis=True)

    def titleString(self):
        return '<h3>%s</h3>' % self.view.name

    def xaxisName(self):
        return 'time'

    def yaxisName(self):
        return 'value'

    def addAllCurves(self):
        for i, key in enumerate(self.view.keys):
            self.addCurve(i, key)

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

    def on_picker_moved(self, point, strf=time.strftime, local=time.localtime):
        # overridden to show the correct timestamp
        tstamp = local(int(self.invTransform(QwtPlot.xBottom, point.x())))
        info = "X = %s, Y = %g" % (
            strf('%y-%m-%d %H:%M:%S', tstamp),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def addCurve(self, i, key, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = QwtPlotCurve(key)
        plotcurve.setPen(pen)
        #plotcurve.setSymbol(self.symbol)
        x, y, n = self.view.keydata[key]
        plotcurve.setData(x[:n], y[:n])
        self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, whichkey):
        for key, plotcurve in zip(self.view.keys, self.plotcurves):
            if key == whichkey:
                x, y, n = self.view.keydata[key]
                plotcurve.setData(x[:n], y[:n])
                self.replot()
                return

    def setLines(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setStyle(QwtPlotCurve.Lines)
            else:
                plotcurve.setStyle(QwtPlotCurve.NoCurve)
        self.hasLines = on
        self.replot()

    def setSymbols(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setSymbol(self.symbol)
            else:
                plotcurve.setSymbol(self.nosymbol)
        self.hasSymbols = on
        self.replot()
