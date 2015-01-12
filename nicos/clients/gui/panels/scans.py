#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI scan plot window."""

import sys
import os
import time

sys.QT_BACKEND_ORDER = ["PyQt4", "PySide"]

from PyQt4.QtGui import QDialog, QMenu, QToolBar, QStatusBar, QFont, \
    QListWidgetItem, QSizePolicy, QPalette, QKeySequence, QShortcut
from PyQt4.QtCore import QByteArray, Qt, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

try:
    from nicos.clients.gui.widgets.grplotting import DataSetPlot
    _gr_available = True
except ImportError as e:
    from nicos.clients.gui.widgets.qwtplotting import DataSetPlot
    _gr_available = False
    _import_error = e

from nicos.core import Dataset
from nicos.utils import safeFilename
from nicos.clients.gui.data import DataProxy
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.clients.gui.widgets.plotting import GaussFitter, \
    PseudoVoigtFitter, PearsonVIIFitter, TcFitter, ArbitraryFitter
from nicos.pycompat import itervalues

TIMEFMT = '%Y-%m-%d %H:%M:%S'
TOGETHER, COMBINE, ADD, SUBTRACT, DIVIDE = range(5)

def combinestr(strings, **kwds):
    strings = list(strings)
    sep = kwds.pop('sep', ' | ')
    res = last = strings[0]
    for item in strings[1:]:
        if item != last:
            res += sep + item
            last = item
    return res

def combineattr(it, attr, sep=' | '):
    return combinestr((getattr(x, attr) for x in it), sep=sep)

def itemuid(item):
    return str(item.data(32))

arby_functions = {
    'Gaussian x2': ('a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
                    'a b c x1 x2 s1 s2'),
    'Gaussian x3 symm.':
        ('a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
         'c*exp(-(x-x0)**2/s0**2)', 'a b c x0 x1 s0 s1'),
    'Parabola': ('a*x**2 + b*x + c', 'a b c'),
}


class ScansPanel(Panel):
    panelName = 'Scans'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'scans.ui', 'panels')

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.layout().addWidget(self.statusBar)

        quickfit = QShortcut(QKeySequence("G"), self)
        self.connect(quickfit, SIGNAL('activated()'), self.on_quickfit)

        self.user_color = Qt.white
        self.user_font = QFont('monospace')

        self.bulk_adding = False
        self.no_openset = False

        self.menus = None
        self.bar = None

        self.data = self.mainwindow.data

        # maps set uid -> plot
        self.setplots = {}
        # maps set uid -> list item
        self.setitems = {}
        # current plot object
        self.currentPlot = None
        # stack of set uids
        self.setUidStack = []
        # uids of automatically combined datasets -> uid of combined one
        self.contSetUids = {}

        self.splitter.restoreState(self.splitterstate)

        self.connect(self.data, SIGNAL('datasetAdded'),
                     self.on_data_datasetAdded)
        self.connect(self.data, SIGNAL('pointsAdded'),
                     self.on_data_pointsAdded)
        self.connect(self.data, SIGNAL('curveAdded'),
                     self.on_data_curveAdded)
        self.connect(client, SIGNAL('experiment'),
                     self.on_client_experiment)

        self.updateList()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', b'', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

    def setCustomStyle(self, font, back):
        self.user_font = font
        self.user_color = back

        for plot in itervalues(self.setplots):
            plot.setCanvasBackground(back)
            plot.update()

        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        for plot in itervalues(self.setplots):
            plot.setFonts(font, bold, larger)

    def requestClose(self):
        # Always succeeds, but break up circular references so that the panel
        # object can be deleted properly.
        self.currentPlot = None
        self.setplots.clear()
        return True

    def enablePlotActions(self, on):
        for action in [
            self.actionSavePlot, self.actionPrint,
            self.actionAttachElog, self.actionCombine, self.actionClosePlot,
            self.actionDeletePlot, self.actionLogScale, self.actionAutoScale,
            self.actionNormalized,
            self.actionUnzoom, self.actionLegend, self.actionModifyData,
            self.actionFitPeak, self.actionFitPeakPV, self.actionFitPeakPVII,
            self.actionFitArby,
            ]:
            action.setEnabled(on)
        if not _gr_available:
            self.actionAutoScale.setEnabled(False)

    def getMenus(self):
        if not self.menus:
            menu1 = QMenu('&Data plot', self)
            menu1.addAction(self.actionSavePlot)
            menu1.addAction(self.actionPrint)
            menu1.addAction(self.actionAttachElog)
            menu1.addSeparator()
            menu1.addAction(self.actionResetPlot)
            menu1.addAction(self.actionCombine)
            menu1.addAction(self.actionClosePlot)
            menu1.addAction(self.actionDeletePlot)
            menu1.addSeparator()
            menu1.addAction(self.actionUnzoom)
            menu1.addAction(self.actionLogScale)
            menu1.addAction(self.actionAutoScale)
            menu1.addAction(self.actionNormalized)
            menu1.addAction(self.actionLegend)
            menu1.addSeparator()
            menu2 = QMenu('Data &manipulation', self)
            menu2.addAction(self.actionModifyData)
            menu2.addSeparator()
            menu2.addAction(self.actionFitPeak)
            menu2.addAction(self.actionFitPeakPV)
            menu2.addAction(self.actionFitPeakPVII)
            menu2.addAction(self.actionFitTc)
            menu2.addSeparator()
            menu2.addAction(self.actionFitArby)
            self.menus = [menu1, menu2]

        return self.menus

    def getToolbars(self):
        if not self.bar:
            bar = QToolBar('Scans')
            bar.addAction(self.actionSavePlot)
            bar.addAction(self.actionPrint)
            bar.addSeparator()
            bar.addAction(self.actionUnzoom)
            bar.addAction(self.actionNormalized)
            bar.addAction(self.actionLogScale)
            bar.addAction(self.actionAutoScale)
            bar.addAction(self.actionLegend)
            bar.addAction(self.actionResetPlot)
            bar.addAction(self.actionDeletePlot)
            bar.addSeparator()
            bar.addAction(self.actionCombine)
            bar.addAction(self.actionFitPeak)
            bar.addAction(self.actionFitArby)
            self.bar = bar

        return [self.bar]

    def updateList(self):
        self.datasetList.clear()
        for dataset in self.data.sets:
            if dataset.invisible:
                continue
            try:
                xname = ' (%s)' % dataset.xnames[dataset.xindex]
            except IndexError:
                xname = ''
            shortname = dataset.name + xname
            item = QListWidgetItem(shortname, self.datasetList)
            item.setData(32, dataset.uid)
            self.setitems[dataset.uid] = item

    def on_logYinDomain(self, flag):
        if not flag:
            self.actionLogScale.setChecked(flag)

    def on_datasetList_currentItemChanged(self, item, previous):
        if self.no_openset or item is None:
            return
        self.openDataset(itemuid(item))

    def on_datasetList_itemClicked(self, item):
        # this handler is needed in addition to currentItemChanged
        # since one can't change the current item if it's the only one
        if self.no_openset or item is None:
            return
        self.openDataset(itemuid(item))

    def openDataset(self, uid):
        dataset = self.data.uid2set[uid]
        if dataset.uid not in self.setplots:
            newplot = DataSetPlot(self.plotFrame, self, dataset)
            if self.currentPlot:
                newplot.enableCurvesFrom(self.currentPlot)
            self.setplots[dataset.uid] = newplot
        self.datasetList.setCurrentItem(self.setitems[uid])
        plot = self.setplots[dataset.uid]
        if _gr_available:
            plot.setAutoScale(True)
            self.actionAutoScale.setChecked(True)
        else:
            self.actionAutoScale.setEnabled(False)
        self.setCurrentDataset(plot)

    def setCurrentDataset(self, plot):
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
        self.currentPlot = plot
        if plot is None:
            self.enablePlotActions(False)
        else:
            try: self.setUidStack.remove(plot.dataset.uid)
            except ValueError: pass
            self.setUidStack.append(plot.dataset.uid)

            self.enablePlotActions(True)
            self.datasetList.setCurrentItem(self.setitems[plot.dataset.uid])

            self.actionLogScale.setChecked(plot.isLogScaling())
            self.actionNormalized.setChecked(plot.normalized)
            self.actionLegend.setChecked(plot.isLegendEnabled())
            if _gr_available:
                self.actionAutoScale.setChecked(plot.plot.autoscale)
                plot.logYinDomain.connect(self.on_logYinDomain)
            self.plotLayout.addWidget(plot)
            plot.show()

    def on_data_datasetAdded(self, dataset):
        shortname = '%s (%s)' % (dataset.name,
                                 dataset.xnames[dataset.xindex])
        if dataset.uid in self.setitems:
            self.setitems[dataset.uid].setText(shortname)
            if dataset.uid in self.setplots:
                self.setplots[dataset.uid].updateDisplay()
        else:
            self.no_openset = True
            item = QListWidgetItem(shortname, self.datasetList)
            item.setData(32, dataset.uid)
            self.setitems[dataset.uid] = item
            if not self.data.bulk_adding:
                self.openDataset(dataset.uid)
            self.no_openset = False
        # If the dataset is a continuation of another dataset, automatically
        # create a combined dataset.
        contuids = dataset.sinkinfo.get('continuation')
        if contuids:
            alluids = tuple(contuids.split(',')) + (dataset.uid,)
            # Did we already create this set?  Then don't create it again.
            if self.contSetUids.get(alluids) in self.setitems:
                return
            allsets = list(map(self.data.uid2set.get, alluids))
            newuid = self._combine(COMBINE, allsets)
            if newuid:
                self.contSetUids[alluids] = newuid

    def on_data_pointsAdded(self, dataset):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid].pointsAdded()

    def on_data_curveAdded(self, dataset):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid].addCurve(len(dataset.curves) - 1,
                                                dataset.curves[-1])
            self.setplots[dataset.uid].update()

    def on_client_experiment(self, proposal):
        self.datasetList.clear()

        # hide plot
        self.setCurrentDataset(None)

        # back to the beginning
        self.setplots = {}
        self.setitems = {}
        self.currentPlot = None
        self.setUidStack = []

    @qtsig('')
    def on_actionClosePlot_triggered(self):
        current_set = self.setUidStack.pop()
        if self.setUidStack:
            self.setCurrentDataset(self.setplots[self.setUidStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.setplots[current_set]

    @qtsig('')
    def on_actionResetPlot_triggered(self):
        current_set = self.setUidStack.pop()
        del self.setplots[current_set]
        self.openDataset(current_set)

    @qtsig('')
    def on_actionDeletePlot_triggered(self):
        if self.currentPlot.dataset.scaninfo != 'combined set':
            if not self.askQuestion('This is not a combined set: still '
                                    'delete it from the list?'):
                return
        current_set = self.setUidStack.pop()
        self.data.uid2set[current_set].invisible = True
        if self.setUidStack:
            self.setCurrentDataset(self.setplots[self.setUidStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.setplots[current_set]
        for i in range(self.datasetList.count()):
            if itemuid(self.datasetList.item(i)) == current_set:
                self.datasetList.takeItem(i)
                break

    @qtsig('')
    def on_actionSavePlot_triggered(self):
        filename = self.currentPlot.savePlot()
        if filename:
            self.statusBar.showMessage('Plot successfully saved to %s.' %
                                       filename)

    @qtsig('')
    def on_actionPrint_triggered(self):
        if self.currentPlot.printPlot():
            self.statusBar.showMessage('Plot successfully printed.')

    @qtsig('')
    def on_actionAttachElog_triggered(self):
        newdlg = dialogFromUi(self, 'plot_attach.ui', 'panels')
        suffix = ".svg" if _gr_available else ".png"
        newdlg.filename.setText(
            safeFilename("data_%s" % self.currentPlot.dataset.name + suffix))
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        descr = newdlg.description.text()
        fname = newdlg.filename.text()
        pathname = self.currentPlot.saveQuietly()
        with open(pathname, 'rb') as fp:
            remotefn = self.client.ask('transfer', fp.read())
        self.client.eval('_LogAttach(%r, [%r], [%r])' % (descr, remotefn, fname))
        os.unlink(pathname)

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        if _gr_available:
            self.currentPlot._plot.reset()
            self.currentPlot.update()
        else:
            self.currentPlot.zoomer.zoom(0)

    @qtsig('bool')
    def on_actionLogScale_toggled(self, on):
        self.currentPlot.setLogScale(on)

    @qtsig('bool')
    def on_actionAutoScale_toggled(self, on):
        if self.currentPlot:
            self.currentPlot.setAutoScale(on)
            self.currentPlot.update()

    @qtsig('bool')
    def on_actionNormalized_toggled(self, on):
        self.currentPlot.normalized = on
        self.currentPlot.updateDisplay()
        self.on_actionUnzoom_triggered()

    @qtsig('bool')
    def on_actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)

    @qtsig('')
    def on_actionModifyData_triggered(self):
        self.currentPlot.modifyData()

    @qtsig('')
    def on_actionFitPeak_triggered(self):
        self.currentPlot.beginFit(GaussFitter, self.actionFitPeak)

    @qtsig('')
    def on_actionFitPeakPV_triggered(self):
        self.currentPlot.beginFit(PseudoVoigtFitter, self.actionFitPeakPV)

    @qtsig('')
    def on_actionFitPeakPVII_triggered(self):
        self.currentPlot.beginFit(PearsonVIIFitter, self.actionFitPeakPVII)

    @qtsig('')
    def on_actionFitTc_triggered(self):
        self.currentPlot.beginFit(TcFitter, self.actionFitTc)

    @qtsig('')
    def on_actionFitArby_triggered(self):
        # no second argument: the "arbitrary" action is not checkable
        self.currentPlot.beginFit(ArbitraryFitter, None)

    def on_quickfit(self):
        if not self.currentPlot or not self.currentPlot.underMouse():
            return
        self.currentPlot.fitQuick()

    @qtsig('')
    def on_actionCombine_triggered(self):
        current = self.currentPlot.dataset.uid
        dlg = dialogFromUi(self, 'dataops.ui', 'panels')
        for i in range(self.datasetList.count()):
            item = self.datasetList.item(i)
            newitem = QListWidgetItem(item.text(), dlg.otherList)
            newitem.setData(32, item.data(32))
            if itemuid(item) == current:
                dlg.otherList.setCurrentItem(newitem)
                # paint the current set in grey to indicate it's not allowed
                # to be selected
                newitem.setBackground(self.palette().brush(QPalette.Mid))
                newitem.setFlags(Qt.NoItemFlags)
        if dlg.exec_() != QDialog.Accepted:
            return
        items = dlg.otherList.selectedItems()
        sets = [self.data.uid2set[current]]
        for item in items:
            if itemuid(item) == current:
                return self.showError('Cannot combine set with itself.')
            sets.append(self.data.uid2set[itemuid(item)])
        for rop, rb in [(TOGETHER, dlg.opTogether),
                        (COMBINE, dlg.opCombine),
                        (ADD, dlg.opAdd),
                        (SUBTRACT, dlg.opSubtract),
                        (DIVIDE, dlg.opDivide)]:
            if rb.isChecked():
                op = rop
                break
        self._combine(op, sets)

    def _combine(self, op, sets):
        if op == TOGETHER:
            newset = Dataset()
            newset.name = combineattr(sets, 'name', sep=', ')
            newset.invisible = False
            newset.curves = []
            newset.scaninfo = 'combined set'
            newset.started = time.localtime()
            newset.xvalueinfo = sets[0].xvalueinfo # XXX combine from sets
            #newset.xnames = sets[0].xnames
            newset.xindex = sets[0].xindex
            # for together only, the number of curves and their columns
            # are irrelevant, just put all together
            for dataset in sets:
                for curve in dataset.curves:
                    newcurve = curve.copy()
                    if not newcurve.source:
                        newcurve.source = dataset.name
                    newset.curves.append(newcurve)
            self.data.add_existing_dataset(newset, [dataset.uid for dataset in sets])
            return newset.uid
        # else, need same axes, and same number and types of curves

        firstset = sets[0]
        nameprops = [firstset.xnames, firstset.xunits]
        curveprops = [(curve.description, curve.yindex)
                      for curve in firstset.curves]
        for dataset in sets[1:]:
            if [dataset.xnames, dataset.xunits] != nameprops:
                self.showError('Sets have different axes.')
                return
            if [(curve.description, curve.yindex)
                for curve in dataset.curves] != curveprops:
                self.showError('Sets have different curves.')
                return
        if op == COMBINE:
            newset = Dataset()
            newset.name = combineattr(sets, 'name', sep=', ')
            newset.invisible = False
            newset.curves = []
            newset.scaninfo = 'combined set'
            newset.started = time.localtime()
            newset.xvalueinfo = firstset.xvalueinfo
            #newset.xnames = firstset.xnames
            newset.xindex = firstset.xindex
            #newset.xunits = firstset.xunits
            for curves in zip(*(dataset.curves for dataset in sets)):
                newcurve = curves[0].copy()
                for attr in ('datax', 'datay', 'datady', 'datatime', 'datamon'):
                    setattr(newcurve, attr, DataProxy(getattr(curve, attr)
                                                      for curve in curves))
                newset.curves.append(newcurve)
            self.data.add_existing_dataset(newset, [dataset.uid for dataset in sets])
            return newset.uid

        if op == ADD:
            sep = ' + '
        elif op == SUBTRACT:
            sep = ' - '
        elif op == DIVIDE:
            sep = ' / '
        newset = Dataset()
        newset.name = combineattr(sets, 'name', sep=sep)
        newset.invisible = False
        newset.scaninfo = 'combined set'
        newset.curves = []
        newset.started = time.localtime()
        newset.xvalueinfo = firstset.xvalueinfo
        #newset.xnames = firstset.xnames
        newset.xindex = firstset.xindex
        #newset.xunits = firstset.xunits
        for curves in zip(*(dataset.curves for dataset in sets)):
            newcurve = curves[0].deepcopy()
            # CRUDE HACK: don't care about the x values, operate by index
            for curve in curves[1:]:
                for i in range(len(newcurve.datay)):
                    try:
                        if op == ADD:
                            newcurve.datay[i] += curve.datay[i]
                        elif op == SUBTRACT:
                            newcurve.datay[i] -= curve.datay[i]
                        elif op == DIVIDE:
                            newcurve.datay[i] /= float(curve.datay[i])
                    except Exception:
                        pass
            # XXX treat errors correctly
            newset.curves.append(newcurve)
        self.data.add_existing_dataset(newset)
        return newset.uid
