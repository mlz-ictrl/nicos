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

"""NICOS GUI scan plot window."""

from __future__ import with_statement

import os
import time

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QDialog, QMenu, QToolBar, QStatusBar, QFont, QPen, \
     QListWidgetItem, QSizePolicy, QPalette, QKeySequence, QShortcut
from PyQt4.Qwt5 import QwtPlot, QwtPlotItem, QwtText, QwtLog10ScaleEngine
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.core import Dataset
from nicos.utils import safeFilename
from nicos.clients.gui.data import DataProxy
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi, DlgPresets
from nicos.clients.gui.fitutils import fit_gauss, fwhm_to_sigma, fit_tc, \
     fit_pseudo_voigt, fit_pearson_vii, fit_arby
from nicos.clients.gui.plothelpers import NicosPlot, ErrorBarPlotCurve, cloneToGrace


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
    return str(item.data(32).toString())

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

        self.user_color = parent.user_color
        self.user_font = parent.user_font

        self.bulk_adding = False
        self.no_openset = False

        self.data = self.mainwindow.data

        # maps set uid -> plot
        self.setplots = {}
        # maps set uid -> list item
        self.setitems = {}
        # current plot object
        self.currentPlot = None
        # stack of set uids
        self.setUidStack = []

        self.splitter.restoreState(self.splitterstate)

        self.connect(self.data, SIGNAL('datasetAdded'),
                     self.on_data_datasetAdded)
        self.connect(self.data, SIGNAL('pointsAdded'),
                     self.on_data_pointsAdded)
        self.connect(self.data, SIGNAL('curveAdded'),
                     self.on_data_curveAdded)

        self.updateList()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter').toByteArray()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())

    def setCustomStyle(self, font, back):
        self.user_font = font
        self.user_color = back

        for plot in self.setplots.itervalues():
            plot.setCanvasBackground(back)
            plot.replot()

        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        for plot in self.setplots.itervalues():
            plot.setFonts(font, bold, larger)

    def enablePlotActions(self, on):
        for action in [
            self.actionPDF, self.actionGrace, self.actionPrint,
            self.actionAttachElog, self.actionCombine, self.actionClosePlot,
            self.actionDeletePlot, self.actionLogScale, self.actionNormalized,
            self.actionShowAllCurves,
            self.actionUnzoom, self.actionLegend, self.actionModifyData,
            self.actionFitPeak, self.actionFitPeakPV, self.actionFitPeakPVII,
            self.actionFitArby,
            ]:
            action.setEnabled(on)

    def getMenus(self):
        menu1 = QMenu('&Data plot', self)
        menu1.addAction(self.actionPDF)
        menu1.addAction(self.actionGrace)
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
        menu1.addAction(self.actionNormalized)
        menu1.addAction(self.actionShowAllCurves)
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
        return [menu1, menu2]

    def getToolbars(self):
        bar = QToolBar('Scans')
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionNormalized)
        bar.addAction(self.actionLogScale)
        bar.addAction(self.actionLegend)
        bar.addAction(self.actionResetPlot)
        bar.addAction(self.actionDeletePlot)
        bar.addSeparator()
        bar.addAction(self.actionCombine)
        bar.addAction(self.actionFitPeak)
        bar.addAction(self.actionFitArby)
        return [bar]

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
            self.actionLogScale.setChecked(
                isinstance(plot.axisScaleEngine(QwtPlot.yLeft),
                           QwtLog10ScaleEngine))
            self.actionNormalized.setChecked(plot.normalized)
            self.actionLegend.setChecked(plot.legend() is not None)
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
        contuids = dataset.sinkinfo.get('continuation')
        if contuids:
            alluids = contuids.split(',') + [dataset.uid]
            self._combine(COMBINE, map(self.data.uid2set.get, alluids))

    def on_data_pointsAdded(self, dataset):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid].pointsAdded()

    def on_data_curveAdded(self, dataset):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid].addCurve(len(dataset.curves)-1,
                                                dataset.curves[-1])
            self.setplots[dataset.uid].replot()

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
    def on_actionPDF_triggered(self):
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
        newdlg.filename.setText(
            safeFilename('data_%s.png' % self.currentPlot.dataset.name))
        ret = newdlg.exec_()
        if ret != QDialog.Accepted:
            return
        descr = str(newdlg.description.text())
        fname = str(newdlg.filename.text())
        pathname = self.currentPlot.savePng()
        with open(pathname, 'rb') as fp:
            remotefn = self.client.ask('transfer', fp.read().encode('base64'))
        self.client.ask('eval', 'LogAttach(%r, [%r], [%r])' %
                        (descr, remotefn, fname))
        os.unlink(pathname)

    @qtsig('')
    def on_actionGrace_triggered(self):
        try:
            cloneToGrace(self.currentPlot)
        except (TypeError, IOError):
            return self.showError('Grace is not available.')

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.currentPlot.zoomer.zoom(0)

    @qtsig('bool')
    def on_actionLogScale_toggled(self, on):
        self.currentPlot.setLogScale(on)

    @qtsig('bool')
    def on_actionNormalized_toggled(self, on):
        self.currentPlot.normalized = on
        self.currentPlot.updateDisplay()

    @qtsig('bool')
    def on_actionShowAllCurves_toggled(self, on):
        self.currentPlot.show_all = on
        self.currentPlot.updateDisplay()

    @qtsig('bool')
    def on_actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)

    @qtsig('')
    def on_actionModifyData_triggered(self):
        self.currentPlot.modifyData()

    @qtsig('')
    def on_actionFitPeak_triggered(self):
        self.currentPlot.fitGaussPeak()

    @qtsig('')
    def on_actionFitPeakPV_triggered(self):
        self.currentPlot.fitPseudoVoigtPeak()

    @qtsig('')
    def on_actionFitPeakPVII_triggered(self):
        self.currentPlot.fitPearsonVIIPeak()

    @qtsig('')
    def on_actionFitTc_triggered(self):
        self.currentPlot.fitTc()

    @qtsig('')
    def on_actionFitArby_triggered(self):
        self.currentPlot.fitArby()

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
            return
        # else, need same axes, and same number and types of curves

        firstset = sets[0]
        nameprops = [firstset.xnames, firstset.xunits]
        curveprops = [(curve.description, curve.yindex)
                      for curve in firstset.curves]
        for dataset in sets[1:]:
            if [dataset.xnames, dataset.xunits] != nameprops:
                return self.showError('Sets have different axes.')
            if [(curve.description, curve.yindex)
                for curve in dataset.curves] != curveprops:
                return self.showError('Sets have different curves.')
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
            return

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


class DataSetPlot(NicosPlot):
    def __init__(self, parent, window, dataset):
        self.dataset = dataset
        NicosPlot.__init__(self, parent, window)

    def titleString(self):
        return '<h3>Scan %s</h3><font size="-2">%s, started %s</font>' % \
            (self.dataset.name, self.dataset.scaninfo,
             time.strftime(TIMEFMT, self.dataset.started))

    def xaxisName(self):
        try:
            return '%s (%s)' % (self.dataset.xnames[self.dataset.xindex],
                                self.dataset.xunits[self.dataset.xindex])
        except IndexError:
            return ''

    def yaxisName(self):
        return ''

    def xaxisScale(self):
        if self.dataset.xrange:
            return self.dataset.xrange
        try:
            return (float(self.dataset.positions[0][self.dataset.xindex]),
                    float(self.dataset.positions[-1][self.dataset.xindex]))
        except (IndexError, TypeError):
            return None

    def yaxisScale(self):
        if self.dataset.yrange:
            return self.dataset.yrange

    def addAllCurves(self):
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)

    def enableCurvesFrom(self, otherplot):
        visible = {}
        for plotcurve in otherplot.plotcurves:
            visible[str(plotcurve.title().text())] = plotcurve.isVisible()
        changed = False
        for plotcurve in self.plotcurves:
            namestr = str(plotcurve.title().text())
            if namestr in visible:
                self.setVisibility(plotcurve, visible[namestr])
                changed = True
        if changed:
            self.replot()

    def addCurve(self, i, curve, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = ErrorBarPlotCurve(title=curve.full_description,
                                      curvePen=pen,
                                      errorPen=QPen(Qt.darkGray, 0),
                                      errorCap=8, errorOnTop=False)
        if not curve.function:
            plotcurve.setSymbol(self.symbol)
        if curve.yaxis == 2:
            plotcurve.setYAxis(QwtPlot.yRight)
            self.has_secondary = True
            self.enableAxis(QwtPlot.yRight)
        if curve.disabled:
            if not self.show_all:
                plotcurve.setVisible(False)
                plotcurve.setItemAttribute(QwtPlotItem.Legend, False)
        self.setCurveData(curve, plotcurve)
        self.addPlotCurve(plotcurve, replot)

    def setCurveData(self, curve, plotcurve):
        x = np.array(curve.datax)
        y = np.array(curve.datay, float)
        dy = None
        if curve.dyindex == -2:
            dy = np.sqrt(abs(y))
        elif curve.dyindex > -1:
            dy = np.array(curve.datady)
        if self.normalized:
            norm = None
            if curve.monindices:
                norm = np.array(curve.datamon)
            elif curve.timeindex > -1:
                norm = np.array(curve.datatime)
            if norm is not None:
                y /= norm
                if dy is not None: dy /= norm
        plotcurve.setData(x, y, None, dy)
        # setData creates a new legend item that must be styled
        if not plotcurve.isVisible() and self.legend():
            legenditem = self.legend().find(plotcurve)
            if legenditem:
                newtext = QwtText(legenditem.text())
                newtext.setColor(Qt.darkGray)
                legenditem.setText(newtext)

    def pointsAdded(self):
        curve = None
        for curve, plotcurve in zip(self.dataset.curves, self.plotcurves):
            self.setCurveData(curve, plotcurve)
        if curve and len(curve.datax) == 1:
            self.zoomer.setZoomBase(True)
        else:
            self.replot()

    def modifyData(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
        # get input from the user: which curves should be modified how
        dlg = dialogFromUi(self, 'modify.ui', 'panels')
        def checkAll():
            for i in range(dlg.list.count()):
                dlg.list.item(i).setCheckState(Qt.Checked)
        dlg.connect(dlg.selectall, SIGNAL('clicked()'), checkAll)
        for i in visible_curves:
            li = QListWidgetItem(self.dataset.curves[i].full_description,
                                 dlg.list)
            if len(visible_curves) == 1:
                li.setCheckState(Qt.Checked)
                dlg.operation.setFocus()
            else:
                li.setCheckState(Qt.Unchecked)
        if dlg.exec_() != QDialog.Accepted:
            return
        # evaluate selection
        op = str(dlg.operation.text())
        curves = []
        for i in range(dlg.list.count()):
            li = dlg.list.item(i)
            if li.checkState() == Qt.Checked:
                curves.append(i)
        # make changes to Qwt curve objects only (so that "reset" will discard
        # them again)
        for i in curves:
            curve = self.plotcurves[visible_curves[i]]
            if isinstance(curve, ErrorBarPlotCurve):
                new_y = [eval(op, {'x': v1, 'y': v2})
                         for (v1, v2) in zip(curve._x, curve._y)]
                curve.setData(curve._x, new_y, curve._dx, curve._dy)
            else:
                curve.setData(curve.xData(),
                    [eval(op, {'x': v1, 'y': v2})
                     for (v1, v2) in zip(curve.xData(), curve.yData())])
        self.replot()

    def selectCurve(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
        if len(visible_curves) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for i in visible_curves:
                QListWidgetItem(self.dataset.curves[i].full_description,
                                dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = visible_curves[dlg.list.currentRow()]
        else:
            fitcurve = visible_curves[0]
        return self.plotcurves[fitcurve]

    def fitGaussPeak(self):
        self._beginFit('Gauss', ['Background', 'Peak', 'Half Maximum'],
                       self.gauss_callback)

    def gauss_callback(self, args):
        title = 'peak fit'
        beta, x, y = fit_gauss(*args)
        labelx = beta[2] + beta[3]/2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]),
                       ('FWHM', beta[3] * fwhm_to_sigma),
                       ('Ampl', beta[1]),
                       ('Integr', beta[1]*beta[3]*np.sqrt(2*np.pi))]
        linefrom = beta[2] - beta[3]*fwhm_to_sigma/2
        lineto = beta[2] + beta[3]*fwhm_to_sigma/2
        liney = beta[0] + beta[1]/2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPseudoVoigtPeak(self):
        self._beginFit('Pseudo-Voigt', ['Background', 'Peak', 'Half Maximum'],
                       self.pv_callback)

    def pv_callback(self, args):
        title = 'peak fit (PV)'
        beta, x, y = fit_pseudo_voigt(*args)
        labelx = beta[2] + beta[3]/2
        labely = beta[0] + beta[1]
        eta = beta[4] % 1.0
        integr = beta[1] * beta[3] * (
            eta*np.pi + (1-eta)*np.sqrt(np.pi/np.log(2)))
        interesting = [('Center', beta[2]), ('FWHM', beta[3]*2),
                       ('Eta', eta), ('Integr', integr)]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1]/2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPearsonVIIPeak(self):
        self._beginFit('PearsonVII', ['Background', 'Peak', 'Half Maximum'],
                       self.pvii_callback)

    def pvii_callback(self, args):
        title = 'peak fit (PVII)'
        beta, x, y = fit_pearson_vii(*args)
        labelx = beta[2] + beta[3]/2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]), ('FWHM', beta[3]*2),
                       ('m', beta[4])]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1]/2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitTc(self):
        self._beginFit('Tc', ['Background', 'Tc'], self.tc_callback)

    def tc_callback(self, args):
        title = 'Tc fit'
        beta, x, y = fit_tc(*args)
        labelx = beta[2]  # at Tc
        labely = beta[0] + beta[1]  # at I_max
        interesting = [('Tc', beta[2]), (u'α', beta[3])]
        return x, y, title, labelx, labely, interesting, None

    def fitArby(self):
        self._beginFit('Arbitrary', [], self.arby_callback,
                       self.arby_pick_callback)

    def arby_callback(self, args):
        title = 'fit'
        beta, x, y = fit_arby(*args)
        labelx = x[0]
        labely = y.max()
        interesting = zip(self.fitvalues[1], beta)
        return x, y, title, labelx, labely, interesting, None

    def arby_pick_callback(self):
        dlg = dialogFromUi(self, 'fit_arby.ui', 'panels')
        pr = DlgPresets('fit_arby',
            [(dlg.function, ''), (dlg.fitparams, ''),
             (dlg.xfrom, ''), (dlg.xto, '')])
        pr.load()
        for name in sorted(arby_functions):
            QListWidgetItem(name, dlg.oftenUsed)
        def click_cb(item):
            func, params = arby_functions[str(item.text())]
            dlg.function.setText(func)
            dlg.fitparams.setPlainText('\n'.join(
                p + ' = ' for p in params.split()))
        dlg.connect(dlg.oftenUsed,
                    SIGNAL('itemClicked(QListWidgetItem *)'), click_cb)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return False
        pr.save()
        fcn = str(dlg.function.text())
        try:
            xmin = float(str(dlg.xfrom.text()))
        except ValueError:
            xmin = None
        try:
            xmax = float(str(dlg.xto.text()))
        except ValueError:
            xmax = None
        if xmin is not None and xmax is not None and xmin > xmax:
            xmax, xmin = xmin, xmax
        params, values = [], []
        for line in str(dlg.fitparams.toPlainText()).splitlines():
            name_value = line.strip().split('=', 2)
            if len(name_value) < 2:
                continue
            params.append(name_value[0])
            try:
                values.append(float(name_value[1]))
            except ValueError:
                values.append(0)
        self.fitvalues = [fcn, params, values, (xmin, xmax)]
        return True

    def fitQuick(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
        p = self.picker.trackerPosition()
        whichcurve = None
        whichindex = None
        mindist = None
        for i in visible_curves:
            index, dist = self.plotcurves[i].closestPoint(p)
            if mindist is None or dist < mindist:
                whichcurve = i
                whichindex = index
                mindist = dist
        self.fitcurve = self.plotcurves[whichcurve]
        data = self.fitcurve.data()
        # try to find good starting parameters
        peakx, peaky = data.x(whichindex), data.y(whichindex)
        # use either left or right end of curve as background
        leftx, lefty = data.x(0), data.y(0)
        rightx, righty = data.x(data.size()-1), data.y(data.size()-1)
        if abs(peakx - leftx) > abs(peakx - rightx):
            direction = -1
            backx, backy = leftx, lefty
        else:
            direction = 1
            backx, backy = rightx, righty
        i = whichindex
        while i > 0:
            if data.y(i) < (peaky - backy) / 2.:
                break
            i += direction
        if i != whichindex:
            fwhmx = data.x(i)
        else:
            fwhmx = (peakx + backx) / 2.
        self.fitvalues = [(backx, backy), (peakx, peaky), (fwhmx, peaky/2.)]
        self.fitparams = ['Background', 'Peak', 'Half Maximum']
        self.fittype = 'Gauss'
        self.fitcallbacks = [self.gauss_callback, None]
        self._finishFit()
