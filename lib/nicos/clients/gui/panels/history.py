#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

import os
import sys
import time
import cPickle as pickle
from time import time as currenttime, localtime, mktime, strftime

from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtLog10ScaleEngine
from PyQt4.QtGui import QDialog, QFont, QPen, QListWidgetItem, QToolBar, \
     QMenu, QStatusBar, QSizePolicy, QMainWindow, QApplication, QAction, \
     QFileDialog, QLabel, QComboBox, QMessageBox
from PyQt4.QtCore import QObject, QTimer, QDateTime, Qt, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.utils import safeFilename
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi, DlgUtils
from nicos.clients.gui.fitutils import fit_linear
from nicos.clients.gui.widgets.plotting import NicosPlot
from nicos.protocols.cache import cache_load
from nicos.devices.cacheclient import CacheClient


class View(QObject):
    def __init__(self, name, keys, interval, fromtime, totime,
                 yfrom, yto, window, dlginfo, query_func):
        QObject.__init__(self)
        self.name = name
        self.dlginfo = dlginfo
        self.keys = keys
        self.interval = interval
        self.window = window
        self.fromtime = fromtime
        self.totime = totime
        self.yfrom = yfrom
        self.yto = yto

        self.keyinfo = {}

        if self.fromtime is not None:
            self.keydata = {}
            totime = self.totime or currenttime()
            for key in keys:
                string_mapping = {}
                history = query_func(key, self.fromtime, totime)
                if history is None:
                    from nicos.clients.gui.main import log
                    log.error('Error getting history for %s.', key)
                    history = []
                ltime = 0
                lvalue = None
                interval = self.interval
                maxdelta = max(2*interval, 11)
                x, y = np.zeros(2*len(history)), np.zeros(2*len(history))
                i = 0
                for vtime, value in history:
                    if value is None:
                        continue
                    delta = vtime - ltime
                    if delta < interval:
                        # value comes too fast -> ignore
                        continue
                    if isinstance(value, str):
                        # create a new unique integer value for the string
                        value = string_mapping.setdefault(
                            value, len(string_mapping))
                    if delta > maxdelta and lvalue is not None:
                        # synthesize a point inbetween
                        x[i] = vtime - interval
                        y[i] = lvalue
                        i += 1
                    x[i] = ltime = max(vtime, fromtime)
                    y[i] = lvalue = value
                    i += 1
                x.resize((2*i or 100,))
                y.resize((2*i or 100,))
                # keydata is a list of five items: x value array, y value array,
                # index of last value, index of last "real" value (not counting
                # synthesized points from the timer, see below), last received
                # value (even if thrown away)
                self.keydata[key] = [x, y, i, i, lvalue]
                if string_mapping:
                    self.keyinfo[key] = ', '.join('%s=%s' % (v, k) for (k, v) in
                                                  string_mapping.iteritems())
        else:
            self.keydata = dict((key, [np.zeros(500), np.zeros(500), 0, 0, None])
                                for key in keys)

        self.listitem = None
        self.plot = None
        if self.totime is None:
            # add another point with the same value every interval time (but not
            # more often than 11 seconds)
            self.timer = QTimer(self, interval=max(interval, 11)*1000)
            self.timer.timeout.connect(self.on_timer_timeout)
            self.timer.start()

    def on_timer_timeout(self):
        for key, kd in self.keydata.iteritems():
            if kd[0][kd[2]-1] < currenttime() - self.interval:
                self.newValue(currenttime(), key, '=', kd[4], real=False)

    def newValue(self, time, key, op, value, real=True):
        if op != '=':
            return
        kd = self.keydata[key]
        n = kd[2]
        real_n = kd[3]
        kd[4] = value
        if real_n > 0 and kd[0][real_n-1] > time - self.interval:
            return
        # double array size if array is full
        if n == kd[0].shape[0]:
            # we select a certain maximum # of points to avoid filling up memory
            # and taking forever to update
            if kd[0].shape[0] > 5000:
                # don't add more points, make existing ones more sparse
                kd[0][:n/2] = kd[0][1::2]
                kd[1][:n/2] = kd[1][1::2]
                n = kd[2] = kd[3] = n/2
            else:
                kd[0].resize((2*kd[0].shape[0],))
                kd[1].resize((2*kd[1].shape[0],))
        # fill next entry
        if not real and real_n < n:
            # do not generate endless amounts of synthesized points, one
            # is enough
            kd[0][n-1] = time
            kd[1][n-1] = value
        else:
            kd[0][n] = time
            kd[1][n] = value
            kd[2] += 1
            if real:
                kd[3] = kd[2]
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
                kd[0][0:n-i] = kd[0][i+1:n+1].copy()
                kd[1][0:n-i] = kd[1][i+1:n+1].copy()
                kd[2] -= i+1
                kd[3] -= i+1
        if self.plot:
            self.plot.pointsAdded(key)


class NewViewDialog(QDialog, DlgUtils):

    def __init__(self, parent, info=None, devlist=None):
        QDialog.__init__(self, parent)
        DlgUtils.__init__(self, 'History viewer')
        loadUi(self, 'history_new.ui', 'panels')

        self.fromdate.setDateTime(QDateTime.currentDateTime())
        self.todate.setDateTime(QDateTime.currentDateTime())

        self.connect(self.customY, SIGNAL('toggled(bool)'), self.toggleCustomY)
        self.toggleCustomY(False)

        if devlist:
            self.devices.addItems(devlist)

        self.connect(self.simpleTime, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.extTime, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.frombox, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.connect(self.tobox, SIGNAL('toggled(bool)'), self.toggleSimpleExt)
        self.toggleSimpleExt(True)

        self.connect(self.simpleTimeSpec,
                     SIGNAL('textChanged(const QString&)'),
                     self.setIntervalFromSimple)

        self.connect(self.helpButton, SIGNAL('clicked()'), self.showDeviceHelp)
        self.connect(self.simpleHelpButton, SIGNAL('clicked()'),
                     self.showSimpleHelp)

        if info is not None:
            self.devices.setEditText(info['devices'])
            self.namebox.setText(info['name'])
            self.simpleTime.setChecked(info['simpleTime'])
            self.simpleTimeSpec.setText(info['simpleTimeSpec'])
            self.slidingWindow.setChecked(info['slidingWindow'])
            self.frombox.setChecked(info['frombox'])
            self.tobox.setChecked(info['tobox'])
            self.fromdate.setDateTime(QDateTime.fromTime_t(info['fromdate']))
            self.todate.setDateTime(QDateTime.fromTime_t(info['todate']))
            self.interval.setText(info['interval'])
            self.customY.setChecked(info['customY'])
            self.customYFrom.setText(info['customYFrom'])
            self.customYTo.setText(info['customYTo'])

    def showSimpleHelp(self):
        self.showInfo('Please enter a time interval with unit like this:\n\n'
            '30m   (30 minutes)\n'
            '12h   (12 hours)\n'
            '3d    (3 days)\n')

    def showDeviceHelp(self):
        self.showInfo('Enter a comma-separated list of device names or '
            'parameters (as "device.parameter").  Example:\n\n'
            'T, T.setpoint\n\nshows the value of device T, and the value '
            'of the T.setpoint parameter.')

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
            _itime, interval = parseTimeSpec(str(text))
        except Exception:
            pass
        else:
            self.interval.setText(str(interval))

    def accept(self):
        if self.simpleTime.isChecked():
            try:
                parseTimeSpec(str(self.simpleTimeSpec.text()))
            except ValueError:
                self.showSimpleHelp()
                return
        if self.customY.isChecked():
            try:
                float(str(self.customYFrom.text()))
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return
            try:
                float(str(self.customYTo.text()))
            except ValueError:
                self.showError('You have to input valid y axis limits.')
                return
        return QDialog.accept(self)

    def infoDict(self):
        return dict(
            devices = str(self.devices.currentText()),
            name = str(self.namebox.text()),
            simpleTime = self.simpleTime.isChecked(),
            simpleTimeSpec = str(self.simpleTimeSpec.text()),
            slidingWindow = self.slidingWindow.isChecked(),
            frombox = self.frombox.isChecked(),
            tobox = self.tobox.isChecked(),
            fromdate = self.fromdate.dateTime().toTime_t(),
            todate = self.todate.dateTime().toTime_t(),
            interval = str(self.interval.text()),
            customY = self.customY.isChecked(),
            customYFrom = str(self.customYFrom.text()),
            customYTo = str(self.customYTo.text()),
        )


class BaseHistoryWindow(object):

    hasPresets = False

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
            self.actionSaveData,
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

    def _createViewFromDialog(self, info):
        parts = [part.strip().lower().replace('.', '/')
                 for part in info['devices'].split(',')]
        if not parts:
            return
        keys = [part if '/' in part else part + '/value' for part in parts]
        name = info['name']
        if not name:
            name = info['devices']
            if info['simpleTime']:
                name += ' (%s)' % info['simpleTimeSpec']
        window = None
        if info['simpleTime']:
            try:
                itime, _ = parseTimeSpec(info['simpleTimeSpec'])
            except ValueError:
                return
            fromtime = currenttime() - itime
            totime = None
            if info['slidingWindow']:
                window = itime
        else:
            if info['frombox']:
                fromtime = mktime(localtime(info['fromdate']))
            else:
                fromtime = None
            if info['tobox']:
                totime = mktime(localtime(info['todate']))
            else:
                totime = None
        try:
            interval = float(info['interval'])
        except ValueError:
            interval = 5.0
        if info['customY']:
            try:
                yfrom = float(info['customYFrom'])
            except ValueError:
                return
            try:
                yto = float(info['customYTo'])
            except ValueError:
                return
        else:
            yfrom = yto = None
        view = View(name, keys, interval, fromtime, totime, yfrom, yto,
                    window, info, self.gethistory_callback)
        self.views.append(view)
        view.listitem = QListWidgetItem(view.name, self.viewList)
        self.openView(view)
        if view.totime is None:
            for key in view.keys:
                self.keyviews.setdefault(key, []).append(view)

    @qtsig('')
    def on_actionNew_triggered(self):
        self.showNewDialog()

    def showNewDialog(self, devices=''):
        devlist = []
        if hasattr(self, 'client'):
            devlist = self.client.getDeviceList()
        newdlg = NewViewDialog(self, devlist=devlist)
        newdlg.devices.setEditText(devices)
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        info = newdlg.infoDict()
        self._createViewFromDialog(info)
        if newdlg.savePreset.isChecked() and self.hasPresets:
            self.presetdict[str(info['name'])] = pickle.dumps(info)

    def newView(self, devices):
        newdlg = NewViewDialog(self)
        newdlg.devices.setEditText(devices)
        info = newdlg.infoDict()
        self._createViewFromDialog(info)

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
        view = self.viewStack[-1]
        newdlg = NewViewDialog(self, view.dlginfo)
        newdlg.setWindowTitle('Edit history view')
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        self.viewStack.pop()
        self.clearView(view)
        self.setCurrentView(None)
        self._createViewFromDialog(newdlg.infoDict())

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

    @qtsig('')
    def on_actionSaveData_triggered(self):
        self.currentPlot.saveData()


class HistoryPanel(Panel, BaseHistoryWindow):
    panelName = 'History viewer'

    hasPresets = True

    def __init__(self, parent, client):
        self.presetdict = {}

        Panel.__init__(self, parent, client)
        BaseHistoryWindow.__init__(self)

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.splitter.restoreState(self.splitterstate)
        self.connect(self.client, SIGNAL('cache'), self.newvalue_callback)

    def getMenus(self):
        menu = QMenu('&History viewer', self)
        menu.addAction(self.actionNew)
        menu.addSeparator()
        menu.addAction(self.actionPDF)
        menu.addAction(self.actionPrint)
        menu.addAction(self.actionAttachElog)
        menu.addAction(self.actionSaveData)
        menu.addSeparator()
        menu.addAction(self.actionEditView)
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
        pmenu = QMenu('&Presets', self)
        delmenu = QMenu('Delete', self)
        for preset, info in self.presetdict.iteritems():
            paction = QAction(preset, self)
            pdelaction = QAction(preset, self)
            info = pickle.loads(str(info.toString()))
            def launchpreset(on, info=info):
                self._createViewFromDialog(info)
            def delpreset(on, name=preset, pact=paction, pdelact=pdelaction):
                pmenu.removeAction(pact)
                delmenu.removeAction(pdelact)
                self.presetdict.pop(name, None)
            self.connect(paction, SIGNAL('triggered(bool)'), launchpreset)
            pmenu.addAction(paction)
            self.connect(pdelaction, SIGNAL('triggered(bool)'), delpreset)
            delmenu.addAction(pdelaction)
        if self.presetdict:
            pmenu.addSeparator()
            pmenu.addMenu(delmenu)
        return [menu, pmenu]

    def getToolbars(self):
        bar = QToolBar('History viewer')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionEditView)
        bar.addSeparator()
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addAction(self.actionSaveData)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionDeleteView)
        return [bar]

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter').toByteArray()
        self.presetdict = settings.value('presets').toMap()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('presets', self.presetdict)

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
        with open(pathname, 'rb') as fp:
            remotefn = self.client.ask('transfer', fp.read().encode('base64'))
        self.client.eval('LogAttach(%r, [%r], [%r])' %
                         (descr, remotefn, fname))
        os.unlink(pathname)


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

    #pylint: disable=W0221
    def on_picker_moved(self, point, strf=strftime, local=localtime):
        # overridden to show the correct timestamp
        tstamp = local(int(self.invTransform(QwtPlot.xBottom, point.x())))
        info = "X = %s, Y = %g" % (
            strf('%y-%m-%d %H:%M:%S', tstamp),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def addCurve(self, i, key, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        curvename = key
        keyinfo = self.view.keyinfo.get(key)
        if keyinfo:
            curvename += ' (' + keyinfo + ')'
        plotcurve = QwtPlotCurve(curvename)
        plotcurve.setPen(pen)
        plotcurve.setSymbol(self.nosymbol)
        plotcurve.setStyle(QwtPlotCurve.Lines)
        x, y, n = self.view.keydata[key][:3]
        plotcurve.setData(x[:n], y[:n])
        self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, whichkey):
        for key, plotcurve in zip(self.view.keys, self.plotcurves):
            if key == whichkey:
                x, y, n = self.view.keydata[key][:3]
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
        _x1, x2 = min(x), max(x)
        labelx = x2
        labely = beta[0]*x2 + beta[1]
        interesting = [('Slope', '%.3f /s' % beta[0]),
                       ('', '%.3f /min' % (beta[0]*60)),
                       ('', '%.3f /h' % (beta[0]*3600))]
        return x, y, title, labelx, labely, interesting, None

    def saveData(self):
        dlg = DataExportDialog(self, 'Select curve, file name and format',
                               '', 'ASCII data files (*.dat)')
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        if not dlg.selectedFiles():
            return
        curve = self.plotcurves[dlg.curveCombo.currentIndex()]
        fmtno = dlg.formatCombo.currentIndex()
        filename = dlg.selectedFiles()[0]

        if curve.dataSize() < 1:
            QMessageBox.information(self, 'Error', 'No data in selected curve!')
            return

        with open(filename, 'wb') as fp:
            for i in range(curve.dataSize()):
                if fmtno == 0:
                    fp.write('%s\t%.10f\n' % (curve.x(i) - curve.x(0),
                                              curve.y(i)))
                elif fmtno == 1:
                    fp.write('%s\t%.10f\n' % (curve.x(i), curve.y(i)))
                else:
                    fp.write('%s\t%.10f\n' % (time.strftime(
                        '%Y-%m-%d.%H:%M:%S', time.localtime(curve.x(i))),
                        curve.y(i)))


class DataExportDialog(QFileDialog):

    def __init__(self, viewplot, *args):
        QFileDialog.__init__(self, viewplot, *args)
        self.setConfirmOverwrite(True)
        self.setAcceptMode(QFileDialog.AcceptSave)
        layout = self.layout()
        layout.addWidget(QLabel('Curve:', self), 4, 0)
        self.curveCombo = QComboBox(self)
        self.curveCombo.addItems(viewplot.view.keys)
        layout.addWidget(self.curveCombo, 4, 1)
        layout.addWidget(QLabel('Time format:', self), 5, 0)
        self.formatCombo = QComboBox(self)
        self.formatCombo.addItems(['Seconds since first datapoint',
                                   'UNIX timestamp',
                                   'Text timestamp (YYYY-MM-dd.HH:MM:SS)'])
        layout.addWidget(self.formatCombo, 5, 1)


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
        menu.addAction(self.actionSaveData)
        menu.addSeparator()
        menu.addAction(self.actionEditView)
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
        bar.addAction(self.actionEditView)
        bar.addSeparator()
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addAction(self.actionSaveData)
        bar.addAction(self.actionClose)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionDeleteView)
        return [bar]

    def gethistory_callback(self, key, fromtime, totime):
        return self.app.history(None, key, fromtime, totime)


class StandaloneHistoryApp(CacheClient):

    def doInit(self, mode):
        import nicos.guisupport.gui_rc  #pylint: disable=W0612

        self._qtapp = QApplication(sys.argv)
        self._qtapp.setOrganizationName('nicos')
        self._qtapp.setApplicationName('history')
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
