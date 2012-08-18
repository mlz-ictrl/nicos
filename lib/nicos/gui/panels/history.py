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

import sys
import time

from PyQt4.QtCore import QDateTime, Qt, SIGNAL
from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtLog10ScaleEngine
from PyQt4.QtGui import QDialog, QFont, QPen, QListWidgetItem, QToolBar, \
     QMenu, QStatusBar, QSizePolicy, QMainWindow, QApplication
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi, dialogFromUi, safeFilename, DlgUtils
from nicos.gui.fitutils import fit_linear
from nicos.gui.plothelpers import NicosPlot
from nicos.cache.utils import cache_load
from nicos.cache.client import CacheClient


class View(object):
    def __init__(self, name, keys, interval, fromtime, totime,
                 yfrom, yto, window, query_func):
        self.name = name
        self.keys = keys
        self.interval = interval
        self.window = window
        self.fromtime = fromtime
        self.totime = totime
        self.yfrom = yfrom
        self.yto = yto

        if self.fromtime is not None:
            self.keydata = {}
            totime = self.totime or time.time()
            for key in keys:
                history = query_func(key, self.fromtime, totime)
                if history is None:
                    print 'Error getting history.'
                    history = []
                ltime = 0
                interval = self.interval
                x, y = np.zeros(len(history)), np.zeros(len(history))
                i = 0
                for vtime, value in history:
                    if value is not None and vtime > ltime + interval:
                        x[i] = max(vtime, fromtime)
                        y[i] = value
                        ltime = x[i]
                        i += 1
                x.resize((2*i or 100,))
                y.resize((2*i or 100,))
                self.keydata[key] = [x, y, i]
        else:
            self.keydata = dict((key, [np.zeros(500), np.zeros(500), 0])
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
            # we select a certain maximum # of points to avoid filling up memory
            # and taking forever to update
            if kd[0].shape[0] > 5000:
                # don't add more points, make existing ones more sparse
                kd[0][:n/2] = kd[0][1::2]
                kd[1][:n/2] = kd[1][1::2]
                n = kd[2] = n/2
            else:
                kd[0].resize((2*kd[0].shape[0],))
                kd[1].resize((2*kd[1].shape[0],))
        # fill next entry
        kd[0][n] = time
        kd[1][n] = value
        kd[2] += 1
        # check sliding window
        if self.window:
            i = -1
            threshold = time - self.window
            while kd[0][i+1] < threshold and i < n:
                if kd[0][i+2] > threshold:
                    kd[0][i+1] = threshold
                    break
                i += 1
            if i >= 0:
                # print 'sliding remove:', i+1
                kd[0][0:n-i] = kd[0][i+1:n+1].copy()
                kd[1][0:n-i] = kd[1][i+1:n+1].copy()
                kd[2] -= i+1


class NewViewDialog(QDialog, DlgUtils):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        DlgUtils.__init__(self, 'History viewer')
        loadUi(self, 'history_new.ui', 'panels')

        helptext = 'Enter a comma-separated list of device names or ' \
            'parameters (as "device.parameter").  Example:\n\n' \
            'T, T.setpoint\n\nshows the value of device T, and the value ' \
            'of the T.setpoint parameter.'
        self.fromdate.setDateTime(QDateTime.currentDateTime())
        self.todate.setDateTime(QDateTime.currentDateTime())
        self.connect(self.helpButton, SIGNAL('clicked()'),
                       lambda: self.showInfo(helptext))
        self.customYFrom.setEnabled(False)
        self.customYTo.setEnabled(False)
        self.connect(self.customY, SIGNAL('toggled(bool)'), self.toggleCustomY)
        self.fromdate.setEnabled(False)
        self.todate.setEnabled(False)
        self.frombox.setEnabled(False)
        self.tobox.setEnabled(False)
        self.connect(self.simpleTime, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.extTime, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.frombox, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.tobox, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.simpleTimeSpec,
                     SIGNAL('textChanged(const QString&)'), self.setIntervalFromSimple)
        self.connect(self.simpleHelpButton, SIGNAL('clicked()'),
                     self.showSimpleHelp)

    def showSimpleHelp(self):
        self.showInfo('Please enter a time interval with unit like this:\n\n'
            '30m   (30 minutes)\n'
            '12h   (12 hours)\n'
            '3d    (3 days)\n')

    def toggleCustomY(self, on):
        self.customYFrom.setEnabled(on)
        self.customYTo.setEnabled(on)
        if on:
            self.customYFrom.setFocus()

    def toggleSimpleExt(self, on):
        on = self.simpleTime.isChecked()
        self.simpleTimeSpec.setEnabled(on)
        self.slidingWindow.setEnabled(on)
        self.frombox.setEnabled(not on)
        self.fromdate.setEnabled(not on and self.frombox.isChecked())
        self.tobox.setEnabled(not on)
        self.todate.setEnabled(not on and self.tobox.isChecked())

    def setIntervalFromSimple(self, text):
        try:
            itime, interval = parseTimeSpec(str(text))
        except Exception:
            pass
        else:
            self.interval.setText(str(interval))

    def accept(self):
        if self.simpleTime.isChecked():
            try:
                itime, _ = parseTimeSpec(str(self.simpleTimeSpec.text()))
            except ValueError:
                self.showSimpleHelp()
                return
        return QDialog.accept(self)


class BaseHistoryWindow(object):

    def __init__(self):
        loadUi(self, 'history.ui', 'panels')

        self.user_color = Qt.white
        self.user_font = QFont('monospace')

        self.views = []
        # stack of views to display
        self.viewStack = []
        # maps watched keys to their views
        self.keyviews = {}
        # current plot object
        self.currentPlot = None

        self.enablePlotActions(False)

    def enablePlotActions(self, on):
        for action in [
            self.actionPDF, self.actionPrint, self.actionAttachElog,
            self.actionEditView, self.actionCloseView, self.actionDeleteView,
            self.actionResetView,
            self.actionUnzoom, self.actionLogScale, self.actionLegend,
            self.actionSymbols, self.actionLines, self.actionLinearFit,
            ]:
            action.setEnabled(on)

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

    def newvalue_callback(self, (time, key, op, value)):
        if key not in self.keyviews:
            return
        value = cache_load(value)
        for view in self.keyviews[key]:
            view.newValue(time, key, op, value)
            if view.plot:
                view.plot.pointsAdded(key)

    def _createViewFromDialog(self, newdlg):
        parts = [part.strip().lower().replace('.', '/')
                 for part in str(newdlg.devices.text()).split(',')]
        if not parts:
            return
        keys = [part if '/' in part else part + '/value' for part in parts]
        name = str(newdlg.namebox.text())
        if not name:
            name = str(newdlg.devices.text())
        window = None
        if newdlg.simpleTime.isChecked():
            intv = str(newdlg.simpleTimeSpec.text())
            try:
                itime, _ = parseTimeSpec(intv)
            except ValueError:
                return
            fromtime = time.time() - itime
            totime = None
            if newdlg.slidingWindow.isChecked():
                window = itime
        else:
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
        try:
            interval = float(newdlg.interval.text())
        except ValueError:
            interval = 5.0
        if newdlg.customY.isChecked():
            try:
                yfrom = float(str(newdlg.customYFrom.text()))
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return self.on_actionNew_triggered()
            try:
                yto = float(str(newdlg.customYTo.text()))
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return self.on_actionNew_triggered()
        else:
            yfrom = yto = None
        view = View(name, keys, interval, fromtime, totime, yfrom, yto,
                    window, self.gethistory_callback)
        self.views.append(view)
        view.listitem = QListWidgetItem(name, self.viewList)
        self.openView(view)
        if totime is None:
            for key in keys:
                self.keyviews.setdefault(key, []).append(view)

    @qtsig('')
    def on_actionNew_triggered(self):
        newdlg = NewViewDialog(self)
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        self._createViewFromDialog(newdlg)

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
    def on_actionEditView_triggered(self):
        view = self.viewStack.pop()
        self.clearView(view)
        self.setCurrentView(None)

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
        hassym = view.plot.hasSymbols
        view.plot = None
        self.openView(view)
        view.plot.setSymbols(hassym)

    @qtsig('')
    def on_actionDeleteView_triggered(self):
        view = self.viewStack.pop()
        self.clearView(view)
        if self.viewStack:
            self.setCurrentView(self.viewStack[-1])
        else:
            self.setCurrentView(None)

    def clearView(self, view):
        self.views.remove(view)
        for i in range(self.viewList.count()):
            if self.viewList.item(i) == view.listitem:
                self.viewList.takeItem(i)
                break
        if view.totime is None:
            for key in view.keys:
                self.keyviews[key].remove(view)

    @qtsig('')
    def on_actionPDF_triggered(self):
        filename = self.currentPlot.savePlot()
        if filename:
            self.statusBar.showMessage('View successfully saved to %s.' %
                                       filename)

    @qtsig('')
    def on_actionPrint_triggered(self):
        if self.currentPlot.printPlot():
            self.statusBar.showMessage('View successfully printed.')

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.currentPlot.zoomer.zoom(0)

    @qtsig('bool')
    def on_actionLogScale_toggled(self, on):
        self.currentPlot.setLogScale(on)

    @qtsig('bool')
    def on_actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)

    @qtsig('bool')
    def on_actionSymbols_toggled(self, on):
        self.currentPlot.setSymbols(on)

    @qtsig('bool')
    def on_actionLines_toggled(self, on):
        self.currentPlot.setLines(on)

    @qtsig('')
    def on_actionLinearFit_triggered(self):
        self.currentPlot.fitLinear()


class HistoryPanel(Panel, BaseHistoryWindow):
    panelName = 'History viewer'

    # XXX save history views when closing?

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        BaseHistoryWindow.__init__(self)

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.user_color = parent.user_color
        self.user_font = parent.user_font

        self.splitter.restoreState(self.splitterstate)
        self.connect(self.client, SIGNAL('cache'), self.newvalue_callback)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addSeparator()
        menu.addAction(self.actionPDF)
        menu.addAction(self.actionPrint)
        menu.addAction(self.actionAttachElog)
        menu.addSeparator()
        #menu.addAction(self.actionEditView)
        menu.addAction(self.actionCloseView)
        menu.addAction(self.actionDeleteView)
        menu.addAction(self.actionResetView)
        menu.addSeparator()
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLegend)
        menu.addAction(self.actionSymbols)
        menu.addAction(self.actionLines)
        menu.addAction(self.actionLinearFit)
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
        #bar.addAction(self.actionEditView)
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionDeleteView)
        return [bar]

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

    def gethistory_callback(self, key, fromtime, totime):
        return self.client.ask('gethistory', key, str(fromtime), str(totime))

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
        pathname = self.currentPlot.savePng()
        remotefn = self.client.ask('transfer',
                        open(pathname, 'rb').read().encode('base64'))
        self.client.ask('eval', 'LogAttach(%r, [%r], [%r])' %
                        (descr, remotefn, fname))


class ViewPlot(NicosPlot):
    def __init__(self, parent, window, view):
        self.view = view
        self.hasSymbols = False
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
        plotcurve.setSymbol(self.nosymbol)
        plotcurve.setStyle(QwtPlotCurve.Lines)
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

    def selectCurve(self):
        if len(self.view.keys) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for key in self.view.keys:
                QListWidgetItem(key, dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = dlg.list.currentRow()
        else:
            fitcurve = 0
        return self.plotcurves[fitcurve]

    def fitLinear(self):
        self._beginFit('Linear', ['First point', 'Second point'],
                       self.linear_fit_callback)

    def linear_fit_callback(self, args):
        title = 'linear fit'
        beta, x, y = fit_linear(*args)
        x1, x2 = min(x), max(x)
        labelx = x2
        labely = beta[0]*x2 + beta[1]
        interesting = [('Slope', beta[0])]
        return x, y, title, labelx, labely, interesting, None


class StandaloneHistoryWindow(QMainWindow, BaseHistoryWindow, DlgUtils):
    def __init__(self, app):
        QMainWindow.__init__(self, None)
        BaseHistoryWindow.__init__(self)
        DlgUtils.__init__(self, 'History viewer')

        self.app = app
        self.setCentralWidget(self.splitter)
        self.connect(self, SIGNAL('newvalue'), self.newvalue_callback)

        for toolbar in self.getToolbars():
            self.addToolBar(toolbar)
        for menu in self.getMenus():
            self.menuBar().addMenu(menu)
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addSeparator()
        menu.addAction(self.actionPDF)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        #menu.addAction(self.actionEditView)
        menu.addAction(self.actionCloseView)
        menu.addAction(self.actionDeleteView)
        menu.addAction(self.actionResetView)
        menu.addSeparator()
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLegend)
        menu.addAction(self.actionSymbols)
        menu.addAction(self.actionLines)
        menu.addAction(self.actionLinearFit)
        menu.addSeparator()
        menu.addAction(self.actionClose)
        return [menu]

    def getToolbars(self):
        bar = QToolBar('History viewer')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addAction(self.actionClose)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        #bar.addAction(self.actionEditView)
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionDeleteView)
        return [bar]

    def gethistory_callback(self, key, fromtime, totime):
        return self.app.history(None, key, fromtime, totime)


class StandaloneHistoryApp(CacheClient):

    def doInit(self, mode):
        self._qtapp = QApplication(sys.argv)
        self._window = StandaloneHistoryWindow(self)
        CacheClient.doInit(self, mode)

    def start(self):
        self._window.show()
        try:
            self._qtapp.exec_()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def _propagate(self, data):
        self._window.emit(SIGNAL('newvalue'), data)


def parseTimeSpec(intv):
    if not intv:
        itime = 0
    elif intv.endswith('sec'):
        itime = float(intv[:-3])
    elif intv.endswith('s'):
        itime = float(intv[:-1])
    elif intv.endswith('min'):
        itime = float(intv[:-3]) * 60
    elif intv.endswith('m'):
        itime = float(intv[:-1]) * 60
    elif intv.endswith('h'):
        itime = float(intv[:-1]) * 3600
    elif intv.endswith('days'):
        itime = float(intv[:-4]) * 24 * 3600
    elif intv.endswith('d'):
        itime = float(intv[:-1]) * 24 * 3600
    elif intv.endswith('y'):
        itime = float(intv[:-1]) * 24 * 3600 * 365
    else:
        raise ValueError
    itime = abs(itime)
    if itime >= 24 * 3600:
        interval = 30
    elif itime >= 6 * 3600:
        interval = 10
    elif itime >= 3 * 3600:
        interval = 5
    elif itime >= 1800:
        interval = 2
    else:
        interval = 1
    return itime, interval
