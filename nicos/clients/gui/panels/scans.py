#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

import os
from math import sqrt

from PyQt4.QtGui import QDialog, QMenu, QToolBar, QStatusBar, QFont, \
    QListWidgetItem, QSizePolicy, QPalette, QKeySequence, QShortcut, \
    QTableWidgetItem
from PyQt4.QtCore import QByteArray, Qt, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.utils import safeFilename
from nicos.core.data import ScanData
from nicos.core.params import INFO_CATEGORIES
from nicos.clients.gui.data import DataProxy
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.clients.gui.widgets.plotting import DataSetPlot, GaussFitter, \
    PseudoVoigtFitter, PearsonVIIFitter, TcFitter, ArbitraryFitter, \
    CosineFitter, SigmoidFitter
from nicos.pycompat import itervalues

TIMEFMT = '%Y-%m-%d %H:%M:%S'
TOGETHER, COMBINE, ADD, SUBTRACT, DIVIDE = range(5)
INTERESTING_CATS = [  # from nicos.core.params
    'general',
    'sample',
    'instrument',
    'experiment',
]


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
    'Straight line': ('m*x + t', 'm t'),
    'Parabola': ('a*x**2 + b*x + c', 'a b c'),
    'Gaussian x2': ('a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
                    'a b c x1 x2 s1 s2'),
    'Gaussian x3 symm.':
        ('a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
         'c*exp(-(x-x0)**2/s0**2)', 'a b c x0 x1 s0 s1'),
}


class ScansPanel(Panel):
    """Provides a display for the scans of the current experiment."""

    panelName = 'Scans'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'scans.ui', 'panels')

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.layout().addWidget(self.statusBar)

        self.x_menu = QMenu(self)
        self.x_menu.aboutToShow.connect(self.on_x_menu_aboutToShow)
        self.actionXAxis.setMenu(self.x_menu)

        self.actionAutoDisplay.setChecked(True)

        self.norm_menu = QMenu(self)
        self.norm_menu.aboutToShow.connect(self.on_norm_menu_aboutToShow)
        self.actionNormalized.setMenu(self.norm_menu)

        quickfit = QShortcut(QKeySequence("G"), self)
        self.connect(quickfit, SIGNAL('activated()'), self.on_quickfit)

        self.user_color = Qt.white
        self.user_font = QFont('monospace')

        self.bulk_adding = False
        self.no_openset = False
        self.last_norm_selection = None

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
        if self.tablecolwidth0 > 0:
            self.metaTable.setColumnWidth(0, self.tablecolwidth0)
            self.metaTable.setColumnWidth(1, self.tablecolwidth1)

        self.connect(self.data, SIGNAL('datasetAdded'),
                     self.on_data_datasetAdded)
        self.connect(self.data, SIGNAL('pointsAdded'),
                     self.on_data_pointsAdded)
        self.connect(self.data, SIGNAL('fitAdded'),
                     self.on_data_fitAdded)
        self.connect(client, SIGNAL('experiment'),
                     self.on_client_experiment)

        self.setCurrentDataset(None)
        self.updateList()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)
        self.tablecolwidth0 = settings.value('tablecolwidth0', 0, int)
        self.tablecolwidth1 = settings.value('tablecolwidth1', 0, int)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('tablecolwidth0', self.metaTable.columnWidth(0))
        settings.setValue('tablecolwidth1', self.metaTable.columnWidth(1))

    def setCustomStyle(self, font, back):
        self.user_font = font
        self.user_color = back

        for plot in itervalues(self.setplots):
            plot.setBackgroundColor(back)
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

    def _autoscale(self, x=None, y=None):
        xflag = x if x is not None else self.actionScaleX.isChecked()
        yflag = y if y is not None else self.actionScaleY.isChecked()
        if self.currentPlot:
            self.currentPlot.setAutoScaleFlags(xflag, yflag)
            self.actionAutoScale.setChecked(xflag or yflag)
            self.actionScaleX.setChecked(xflag)
            self.actionScaleY.setChecked(yflag)
            self.currentPlot.update()

    def enablePlotActions(self, on):
        for action in [
            self.actionSavePlot, self.actionPrint, self.actionResetPlot,
            self.actionAttachElog, self.actionCombine, self.actionClosePlot,
            self.actionDeletePlot, self.actionLogScale, self.actionAutoScale,
            self.actionScaleX, self.actionScaleY,
            self.actionXAxis, self.actionNormalized,
            self.actionUnzoom, self.actionLegend, self.actionModifyData,
            self.actionFitPeak, self.actionFitPeakPV, self.actionFitPeakPVII,
            self.actionFitTc, self.actionFitCosine, self.actionFitSigmoid,
            self.actionFitArby,
        ]:
            action.setEnabled(on)

    def enableAutoScaleActions(self, on):
        for action in [self.actionAutoScale, self.actionScaleX,
                       self.actionScaleY]:
            action.setEnabled(on)

    def getMenus(self):
        if not self.menus:
            menu1 = QMenu('&Data plot', self)
            menu1.addAction(self.actionSavePlot)
            menu1.addAction(self.actionPrint)
            menu1.addAction(self.actionAttachElog)
            menu1.addSeparator()
            menu1.addAction(self.actionResetPlot)
            menu1.addAction(self.actionAutoDisplay)
            menu1.addAction(self.actionCombine)
            menu1.addAction(self.actionClosePlot)
            menu1.addAction(self.actionDeletePlot)
            menu1.addSeparator()
            menu1.addAction(self.actionXAxis)
            menu1.addAction(self.actionNormalized)
            menu1.addSeparator()
            menu1.addAction(self.actionUnzoom)
            menu1.addAction(self.actionLogScale)
            menu1.addAction(self.actionAutoScale)
            menu1.addAction(self.actionScaleX)
            menu1.addAction(self.actionScaleY)
            menu1.addAction(self.actionLegend)
            menu1.addSeparator()
            menu2 = QMenu('Data &manipulation', self)
            menu2.addAction(self.actionModifyData)
            menu2.addSeparator()
            menu2.addAction(self.actionFitPeak)
            menu2.addAction(self.actionFitPeakPV)
            menu2.addAction(self.actionFitPeakPVII)
            menu2.addAction(self.actionFitTc)
            menu2.addAction(self.actionFitCosine)
            menu2.addAction(self.actionFitSigmoid)
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
            bar.addAction(self.actionXAxis)
            bar.addAction(self.actionNormalized)
            bar.addSeparator()
            bar.addAction(self.actionLogScale)
            bar.addAction(self.actionUnzoom)
            bar.addSeparator()
            bar.addAction(self.actionAutoScale)
            bar.addAction(self.actionScaleX)
            bar.addAction(self.actionScaleY)
            bar.addAction(self.actionLegend)
            bar.addAction(self.actionResetPlot)
            bar.addAction(self.actionDeletePlot)
            bar.addSeparator()
            bar.addAction(self.actionAutoDisplay)
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
            shortname = '%s - %s' % (dataset.name, dataset.default_xname)
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
        newplot = None
        if dataset.uid not in self.setplots:
            newplot = DataSetPlot(self.plotFrame, self, dataset)
            if self.currentPlot:
                newplot.enableCurvesFrom(self.currentPlot)
            self.setplots[dataset.uid] = newplot
        self.datasetList.setCurrentItem(self.setitems[uid])
        plot = self.setplots[dataset.uid]
        self.enableAutoScaleActions(plot.HAS_AUTOSCALE)
        if newplot and plot.HAS_AUTOSCALE:
            from gr.pygr import PlotAxes
            plot.plot.autoscale = PlotAxes.SCALE_X | PlotAxes.SCALE_Y
        self.setCurrentDataset(plot)

    def setCurrentDataset(self, plot):
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
            self.metaTable.clearContents()
        self.currentPlot = plot
        if plot is None:
            self.enablePlotActions(False)
        else:
            try:
                self.setUidStack.remove(plot.dataset.uid)
            except ValueError:
                pass
            self.setUidStack.append(plot.dataset.uid)

            num_items = 0
            for catname in INTERESTING_CATS:
                if catname in plot.dataset.headerinfo:
                    num_items += 2 + len(plot.dataset.headerinfo[catname])
            num_items -= 1  # remove last empty row
            self.metaTable.setRowCount(num_items)

            i = 0
            for catname in INTERESTING_CATS:
                if catname in plot.dataset.headerinfo:
                    values = plot.dataset.headerinfo[catname]
                    catdesc = catname
                    for name_desc in INFO_CATEGORIES:
                        if name_desc[0] == catname:
                            catdesc = name_desc[1]
                    catitem = QTableWidgetItem(catdesc)
                    font = catitem.font()
                    font.setBold(True)
                    catitem.setFont(font)
                    self.metaTable.setItem(i, 0, catitem)
                    self.metaTable.setSpan(i, 0, 1, 2)
                    i += 1
                    for dev, name, value in sorted(values):
                        key = '%s_%s' % (dev, name) if name != 'value' else dev
                        self.metaTable.setItem(i, 0, QTableWidgetItem(key))
                        self.metaTable.setItem(i, 1, QTableWidgetItem(value))
                        if self.metaTable.columnSpan(i, 0) == 2:
                            self.metaTable.setSpan(i, 0, 1, 1)
                        i += 1
                    i += 1
            self.metaTable.resizeRowsToContents()

            self.enablePlotActions(True)
            self.enableAutoScaleActions(self.currentPlot.HAS_AUTOSCALE)
            self.datasetList.setCurrentItem(self.setitems[plot.dataset.uid])

            self.actionXAxis.setText('X axis: %s' % plot.current_xname)
            self.actionNormalized.setChecked(bool(plot.normalized))

            self.actionLogScale.setChecked(plot.isLogScaling())
            self.actionLegend.setChecked(plot.isLegendEnabled())
            if plot.HAS_AUTOSCALE:
                from gr.pygr import PlotAxes
                mask = plot.plot.autoscale
                self._autoscale(x=mask & PlotAxes.SCALE_X,
                                y=mask & PlotAxes.SCALE_Y)
                plot.logYinDomain.connect(self.on_logYinDomain)
            self.plotLayout.addWidget(plot)
            plot.show()

    def on_data_datasetAdded(self, dataset):
        shortname = '%s - %s' % (dataset.name, dataset.default_xname)
        if dataset.uid in self.setitems:
            self.setitems[dataset.uid].setText(shortname)
            if dataset.uid in self.setplots:
                self.setplots[dataset.uid].updateDisplay()
        else:
            self.no_openset = True
            item = QListWidgetItem(shortname, self.datasetList)
            item.setData(32, dataset.uid)
            self.setitems[dataset.uid] = item
            if self.actionAutoDisplay.isChecked() and not self.data.bulk_adding:
                self.openDataset(dataset.uid)
            self.no_openset = False
        # If the dataset is a continuation of another dataset, automatically
        # create a combined dataset.
        contuids = dataset.continuation
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

    def on_data_fitAdded(self, dataset, res):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid]._plotFit(res)

    def on_client_experiment(self, data):
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
        suffix = self.currentPlot.SAVE_EXT
        newdlg.filename.setText(
            safeFilename('data_%s' % self.currentPlot.dataset.name + suffix))
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        descr = newdlg.description.text()
        fname = newdlg.filename.text()
        pathname = self.currentPlot.saveQuietly()
        with open(pathname, 'rb') as fp:
            remotefn = self.client.ask('transfer', fp.read())
        if remotefn is not None:
            self.client.eval('_LogAttach(%r, [%r], [%r])' %
                             (descr, remotefn, fname))
        os.unlink(pathname)

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.currentPlot.unzoom()

    @qtsig('bool')
    def on_actionLogScale_toggled(self, on):
        self.currentPlot.setLogScale(on)

    @qtsig('bool')
    def on_actionAutoScale_toggled(self, on):
        self._autoscale(on, on)

    @qtsig('bool')
    def on_actionScaleX_toggled(self, on):
        self._autoscale(x=on)

    @qtsig('bool')
    def on_actionScaleY_toggled(self, on):
        self._autoscale(y=on)

    def on_x_menu_aboutToShow(self):
        self.x_menu.clear()
        if not self.currentPlot:
            return
        done = set()
        for name in self.currentPlot.dataset.xnameunits:
            if name in done:
                continue
            done.add(name)
            action = self.x_menu.addAction(name)
            action.setCheckable(True)
            if name == self.currentPlot.current_xname:
                action.setChecked(True)
            action.triggered.connect(self.on_x_action_triggered)

    @qtsig('')
    def on_x_action_triggered(self, text=None):
        if text is None:
            sender = self.sender()
            text = sender.text()
        self.actionXAxis.setText('X axis: %s' % text)
        self.currentPlot.current_xname = text
        self.currentPlot.updateDisplay()
        self.on_actionUnzoom_triggered()

    @qtsig('')
    def on_actionXAxis_triggered(self):
        self.bar.widgetForAction(self.actionXAxis).showMenu()

    @qtsig('')
    def on_actionNormalized_triggered(self):
        if not self.currentPlot:
            return
        if self.currentPlot.normalized is not None:
            self.on_norm_action_triggered('None')
        else:
            all_normnames = [name for (_, name)
                             in self.currentPlot.dataset.normindices]
            if self.last_norm_selection and \
               self.last_norm_selection in all_normnames:
                use = self.last_norm_selection
            else:
                use = all_normnames[0] if all_normnames else 'None'
            self.on_norm_action_triggered(use)

    def on_norm_menu_aboutToShow(self):
        self.norm_menu.clear()
        if self.currentPlot:
            none_action = self.norm_menu.addAction('None')
            none_action.setCheckable(True)
            none_action.setChecked(True)
            none_action.triggered.connect(self.on_norm_action_triggered)
            max_action = self.norm_menu.addAction('Maximum')
            max_action.setCheckable(True)
            if self.currentPlot.normalized == 'Maximum':
                max_action.setChecked(True)
                none_action.setChecked(False)
            max_action.triggered.connect(self.on_norm_action_triggered)
            for _, name in self.currentPlot.dataset.normindices:
                action = self.norm_menu.addAction(name)
                action.setCheckable(True)
                if name == self.currentPlot.normalized:
                    action.setChecked(True)
                    none_action.setChecked(False)
                action.triggered.connect(self.on_norm_action_triggered)

    @qtsig('')
    def on_norm_action_triggered(self, text=None):
        if text is None:
            sender = self.sender()
            text = sender.text()
        if text == 'None':
            self.currentPlot.normalized = None
            self.actionNormalized.setChecked(False)
        else:
            self.last_norm_selection = text
            self.currentPlot.normalized = text
            self.actionNormalized.setChecked(True)
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
    def on_actionFitCosine_triggered(self):
        self.currentPlot.beginFit(CosineFitter, self.actionFitCosine)

    @qtsig('')
    def on_actionFitSigmoid_triggered(self):
        self.currentPlot.beginFit(SigmoidFitter, self.actionFitSigmoid)

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
            newset = ScanData()
            newset.name = combineattr(sets, 'name', sep=', ')
            newset.invisible = False
            newset.curves = []
            newset.scaninfo = 'combined set'
            # combine xnameunits from those that are in all sets
            all_xnu = set(sets[0].xnameunits)
            for dset in sets[1:]:
                all_xnu &= set(dset.xnameunits)
            newset.xnameunits = ['Default'] + [xnu for xnu in sets[0].xnameunits
                                               if xnu in all_xnu]
            newset.default_xname = 'Default'
            newset.normindices = sets[0].normindices
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
            newset = ScanData()
            newset.name = combineattr(sets, 'name', sep=', ')
            newset.invisible = False
            newset.curves = []
            newset.scaninfo = 'combined set'
            newset.xnameunits = firstset.xnameunits
            newset.default_xname = firstset.default_xname
            newset.normindices = firstset.normindices
            for curves in zip(*(dataset.curves for dataset in sets)):
                newcurve = curves[0].copy()
                newcurve.datay = DataProxy(c.datay for c in curves)
                newcurve.datady = DataProxy(c.datady for c in curves)
                newcurve.datax = dict((xnu, DataProxy(c.datax[xnu] for c in curves))
                                      for xnu in newset.xnameunits)
                newcurve.datanorm = dict((nn, DataProxy(c.datanorm[nn] for c in curves))
                                         for i, nn in newset.normindices)
                newset.curves.append(newcurve)
            self.data.add_existing_dataset(newset,
                                           [dataset.uid for dataset in sets])
            return newset.uid

        if op == ADD:
            sep = ' + '
        elif op == SUBTRACT:
            sep = ' - '
        elif op == DIVIDE:
            sep = ' / '

        newset = ScanData()
        newset.name = combineattr(sets, 'name', sep=sep)
        newset.invisible = False
        newset.scaninfo = 'combined set'
        newset.curves = []
        newset.xnameunits = firstset.xnameunits
        newset.default_xname = firstset.default_xname
        if op in (SUBTRACT, DIVIDE):
            # remove information about normalization -- doesn't make sense
            newset.normindices = []
        else:
            newset.normindices = firstset.normindices

        for curves in zip(*(dataset.curves for dataset in sets)):
            newcurve = curves[0].deepcopy()
            # CRUDE HACK: don't care about the x values, operate by index
            removepoints = set()
            for curve in curves[1:]:
                for i in range(len(newcurve.datay)):
                    y1, y2 = float(newcurve.datay[i]), float(curve.datay[i])
                    if newcurve.dyindex != -1:
                        dy1 = newcurve.datady[i]
                        dy2 = curve.datady[i]
                    else:
                        dy1 = dy2 = 1.
                    if op == ADD:
                        newcurve.datay[i] = y1 + y2
                        newcurve.datady[i] = sqrt(dy1**2 + dy2**2)
                        for name in newcurve.datanorm:
                            newcurve.datanorm[name][i] += curve.datanorm[name][i]
                    elif op == SUBTRACT:
                        newcurve.datay[i] = y1 - y2
                        newcurve.datady[i] = sqrt(dy1**2 + dy2**2)
                    elif op == DIVIDE:
                        if y2 == 0:
                            y2 = 1.  # generate a value for now
                            removepoints.add(i)
                        newcurve.datay[i] = y1 / y2
                        newcurve.datady[i] = sqrt((dy1/y2)**2 +
                                                  (dy2*y1 / y2**2)**2)
            # remove points where we would have divided by zero
            if removepoints:
                newcurve.datay = [v for (i, v) in enumerate(newcurve.datay)
                                  if i not in removepoints]
                newcurve.datady = [v for (i, v) in enumerate(newcurve.datady)
                                   if i not in removepoints]
                for name in newcurve.datax:
                    newcurve.datax[name] = \
                        [v for (i, v) in enumerate(newcurve.datax[name])
                         if i not in removepoints]
                for name in newcurve.datanorm:
                    newcurve.datanorm[name] = \
                        [v for (i, v) in enumerate(newcurve.datanorm[name])
                         if i not in removepoints]
            newset.curves.append(newcurve)
        self.data.add_existing_dataset(newset)
        return newset.uid
