#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""NICOS GUI analysis window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from PyQt4.QtCore import Qt, QVariant, QSize, SIGNAL
from PyQt4.QtGui import QDialog, QMenu, QToolBar, QPalette, QFont, \
     QPen, QBrush, QColor, QListWidgetItem, QFontDialog, QColorDialog, \
     QFileDialog, QPrintDialog, QPrinter, QStatusBar, QSizePolicy
from PyQt4.Qwt5 import Qwt, QwtPlot, QwtPlotCurve, QwtPlotItem, QwtSymbol, \
     QwtLog10ScaleEngine, QwtLinearScaleEngine, QwtPlotZoomer, QwtPicker, \
     QwtPlotPicker, QwtPlotMarker, QwtPlotGrid, QwtText, QwtLegend
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

#from nicos.gui.data import DataSet, Curve
from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi
from nicos.gui.fitutils import has_odr, FitError, fit_gauss, fwhm_to_sigma, \
     fit_tc, fit_pseudo_voigt, fit_pearson_vii
from nicos.gui.plothelpers import ErrorBarPlotCurve, XPlotPicker, cloneToGrace


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
    return combinestr((getattr(x, attr) for x in it))

def itemuid(item):
    return str(item.data(32).toString())


class AnalysisPanel(Panel):
    panelName = 'Data analysis'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'analysis.ui')

        self.statusBar = QStatusBar(self)
        self.statusBar.sizePolicy().setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.bulk_adding = False
        self.no_openset = False

        self.data = parent.data

        # maps set uid -> plot
        self.setplots = {}
        # maps set uid -> list item
        self.setitems = {}
        # current plot object
        self.currentPlot = None
        # stack of set uids
        self.setUidStack = []

        self.userFont = self.font()
        self.userColor = self.palette().color(QPalette.Base)

        self.connect(self.data, SIGNAL('datasetAdded'),
                     self.on_data_datasetAdded)
        self.connect(self.data, SIGNAL('pointsAdded'),
                     self.on_data_pointsAdded)

        self.updateList()

    def loadSettings(self):
        with self.sgroup as settings:
            geometry = settings.value('geometry').toByteArray()
            font = QFont(settings.value('font'))
            color = QColor(settings.value('color'))
            splitter = settings.value('splitter').toByteArray()
        self.restoreGeometry(geometry)
        self.splitter.restoreState(splitter)
        self.userFont = font
        self.changeFont()
        if color.isValid():
            self.userColor = color
            self.changeColor()

    def changeFont(self):
        font = self.userFont
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)

        for plot in self.setplots.itervalues():
            plot.setFonts(font, bold, larger)

    def changeColor(self):
        for plot in self.setplots.itervalues():
            plot.setCanvasBackground(self.userColor)
            plot.replot()

    def enablePlotActions(self, on):
        for action in [
            self.actionPDF, self.actionGrace, self.actionPrint,
            self.actionCombine, self.actionClosePlot, self.actionDeletePlot,
            self.actionLogScale, self.actionNormalized, self.actionUnzoom,
            self.actionLegend, self.actionFitPeak, self.actionFitPeakPV,
            self.actionFitPeakPVII,
            ]:
            action.setEnabled(on)

    def getMenus(self):
        menu1 = QMenu('&Data analysis', self)
        menu1.addAction(self.actionPDF)
        menu1.addAction(self.actionGrace)
        menu1.addAction(self.actionPrint)
        menu1.addSeparator()
        menu1.addAction(self.actionResetPlot)
        menu1.addAction(self.actionCombine)
        menu1.addAction(self.actionClosePlot)
        menu1.addAction(self.actionDeletePlot)
        menu1.addSeparator()
        menu1.addAction(self.actionLogScale)
        menu1.addAction(self.actionNormalized)
        menu1.addAction(self.actionUnzoom)
        menu1.addAction(self.actionLegend)
        menu1.addSeparator()
        menu2 = QMenu('&Data fit', self)
        menu2.addAction(self.actionFitPeak)
        menu2.addAction(self.actionFitPeakPV)
        menu2.addAction(self.actionFitPeakPVII)
        menu2.addAction(self.actionFitTc)
        return [menu1, menu2]

    def getToolbars(self):
        bar = QToolBar('Data analysis')
        bar.addAction(self.actionPDF)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionNormalized)
        bar.addAction(self.actionLogScale)
        bar.addAction(self.actionLegend)
        bar.addAction(self.actionResetPlot)
        bar.addSeparator()
        bar.addAction(self.actionFitPeak)
        bar.addAction(self.actionFitTc)
        return [bar]

    def updateList(self):
        self.datasetList.clear()
        for dataset in self.data.sets:
            if dataset.invisible:
                continue
            item = QListWidgetItem(dataset.name, self.datasetList)
            item.setData(32, dataset.uid)
            self.setitems[dataset.uid] = item

    @qtsig('')
    def on_actionFont_triggered(self):
        font, ok = QFontDialog.getFont(self.userFont, self)
        if not ok:
            return
        self.userFont = font
        with self.sgroup as settings:
            settings.setValue('font', QVariant(font))
        self.changeFont()

    @qtsig('')
    def on_actionColor_triggered(self):
        color = QColorDialog.getColor(self.userColor, self)
        if not color.isValid():
            return
        self.userColor = color
        with self.sgroup as settings:
            settings.setValue('color', QVariant(color))
        self.changeColor()

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
        set = self.data.uid2set[uid]
        if set.uid not in self.setplots:
            self.setplots[set.uid] = DataSetPlot(self.plotFrame, self, set)
        self.datasetList.setCurrentItem(self.setitems[uid])
        plot = self.setplots[set.uid]
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
        if dataset.uid in self.setitems:
            self.setitems[dataset.uid].setText(dataset.name)
            if dataset.uid in self.setplots:
                self.setplots[dataset.uid].updateDisplay()
        else:
            self.no_openset = True
            item = QListWidgetItem(dataset.name, self.datasetList)
            item.setData(32, dataset.uid)
            self.setitems[dataset.uid] = item
            if not self.data.bulk_adding:
                self.openDataset(dataset.uid)
            self.no_openset = False

    def on_data_pointsAdded(self, dataset):
        if dataset.uid in self.setplots:
            self.setplots[dataset.uid].pointsAdded()

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
        printer.setCreator('NICOS plot')
        color = self.currentPlot.canvasBackground()
        self.currentPlot.setCanvasBackground(Qt.white)
        self.currentPlot.print_(printer)
        self.currentPlot.setCanvasBackground(color)
        self.statusBar.showMessage('Plot successfully saved to %s.' % filename)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.currentPlot.print_(printer)
        self.statusBar.showMessage('Plot successfully printed to %s.' %
                                   str(printer.printerName()))

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
        self.currentPlot.setAxisScaleEngine(QwtPlot.yLeft,
                                            on and QwtLog10ScaleEngine()
                                            or QwtLinearScaleEngine())
        self.currentPlot.setAxisScaleEngine(QwtPlot.yRight,
                                            on and QwtLog10ScaleEngine()
                                            or QwtLinearScaleEngine())
        self.currentPlot.replot()

    @qtsig('bool')
    def on_actionNormalized_toggled(self, on):
        self.currentPlot.normalized = on
        self.currentPlot.updateDisplay()

    @qtsig('bool')
    def on_actionLegend_toggled(self, on):
        self.currentPlot.setLegend(on)

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
    def on_actionCombine_triggered(self):
        # XXX currently not working
        return

        current = self.currentPlot.dataset.uid
        dlg = QDialog(self)
        loadUi(dlg, 'dataops.ui')
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
        if op == TOGETHER:
            newset = DataSet(
                -1,
                #title=combineattr(sets, 'title'),
                #subtitle=combineattr(sets, 'subtitle', sep='\n'),
                title=combineattr(sets, 'name', sep=', '),
                name=combineattr(sets, 'name', sep=', '),
                xaxisname=combineattr(sets, 'xaxisname'),
                yaxisname=combineattr(sets, 'yaxisname'),
                y2axisname=combineattr(sets, 'y2axisname'),
                )
            # for together only, the number of curves and their columns
            # are irrelevant, just put all together
            for set in sets:
                for curve in set.curves:
                    newcurve = curve.copy()
                    newcurve.name = (newcurve.name or '') + ' (%s)' % set.name
                    newset.curves.append(newcurve)
            self.data.add_existing_dataset(newset)
            return
        # else, need same axes, and same number and types of curves
        firstset = sets[0]
        axisprops = (firstset.xaxisname, firstset.yaxisname, firstset.y2axisname)
        curveprops = [(curve.name, curve.coldesc) for curve in firstset.curves]
        for set in sets[1:]:
            if (set.xaxisname, set.yaxisname, set.y2axisname) != axisprops:
                return self.showError('Sets have different axes.')
            if [(curve.name, curve.coldesc) for curve in set.curves] != curveprops:
                return self.showError('Sets have different curves.')
        if op == COMBINE:
            newset = DataSet(
                -1, title=combineattr(sets, 'title'),
                subtitle=combineattr(sets, 'subtitle', sep='\n'),
                name=combineattr(sets, 'name', sep=', '),
                xaxisname=firstset.xaxisname, yaxisname=firstset.yaxisname,
                y2axisname=firstset.y2axisname)
            for curves in zip(*(set.curves for set in sets)):
                newcurve = Curve(curves[0].name, curves[0].coldesc,
                                 curves[0].plotmode)
                newdata = sum((curve.data.tolist() for curve in curves), [])
                newdata.sort()
                newcurve.data = np.array(newdata)
                newset.curves.append(newcurve)
            self.data.add_existing_dataset(newset)
            return
        if op == ADD:
            sep = ' + '
        elif op == SUBTRACT:
            sep = ' - '
        elif op == DIVIDE:
            sep = ' / '
        newset = DataSet(
            -1, title=combineattr(sets, 'title', sep=sep),
            subtitle=combineattr(sets, 'subtitle', sep='\n'),
            name=combineattr(sets, 'name', sep=sep),
            xaxisname=firstset.xaxisname, yaxisname=firstset.yaxisname,
            y2axisname=firstset.y2axisname)
        for curves in zip(*(set.curves for set in sets)):
            newcurve = Curve(curves[0].name, curves[0].coldesc,
                             curves[0].plotmode)
            # CRUDE: don't care about the x values, operate by index
            newdata = curves[0].data.copy()
            for curve in curves[1:]:
                try:
                    if op == ADD:
                        newdata[:,1] += curve.data[:,1]
                    elif op == SUBTRACT:
                        newdata[:,1] -= curve.data[:,1]
                    elif op == DIVIDE:
                        newdata[:,1] /= curve.data[:,1]
                except Exception:
                    pass
            newcurve.data = newdata
            # XXX treat errors correctly
            newset.curves.append(newcurve)
        self.data.add_existing_dataset(newset)


class DataSetPlot(QwtPlot):
    def __init__(self, parent, window, dataset):
        QwtPlot.__init__(self, parent)
        self.dataset = dataset
        self.window = window
        self.curves = []
        self.normalized = False
        self.fits = 0
        self.fittype = None
        self.fitparams = None
        self.fitstage = 0
        self.has_secondary = False

        font = self.window.userFont
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        self.setFonts(font, bold, larger)

        self.stdpen = QPen()
        self.symbol = QwtSymbol(QwtSymbol.Ellipse, QBrush(),
                                self.stdpen, QSize(6, 6))

        # setup zooming and unzooming
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())
        self.zoomer.initMousePattern(3)
        self.connect(self.zoomer, SIGNAL('zoomed(const QwtDoubleRect &)'),
                     self.on_zoomer_zoomed)

        # setup picking and mouse tracking of coordinates
        self.picker = XPlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                                  QwtPicker.PointSelection |
                                  QwtPicker.DragSelection,
                                  QwtPlotPicker.NoRubberBand,
                                  QwtPicker.AlwaysOff,
                                  self.canvas())

        self.setCanvasBackground(self.window.userColor)
        self.canvas().setMouseTracking(True)
        self.connect(self.picker, SIGNAL('moved(const QPoint &)'),
                     self.on_picker_moved)

        self.updateDisplay()

        self.setLegend(True)
        self.connect(self, SIGNAL('legendClicked(QwtPlotItem*)'),
                     self.on_legendClicked)

    def on_zoomer_zoomed(self, rect):
        #print self.zoomer.zoomStack()
        pass

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
        self.has_secondary = False
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.lightGray), 1, Qt.DotLine))
        grid.attach(self)

        title = '<h3>%s</h3><font size="-2">started %s</font>' % \
            (self.dataset.name, time.strftime(TIMEFMT, self.dataset.started))
        self.setTitle(title)
        xaxisname = '%s (%s)' % (self.dataset.xnames[self.dataset.xindex],
                                 self.dataset.xunits[self.dataset.xindex])
        xaxistext = QwtText(xaxisname)
        xaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.xBottom, xaxistext)
        yaxisname = ''  # XXX determine good axis names
        y2axisname = ''
        if self.normalized:
            yaxistext = QwtText(yaxisname + ' (norm)')
            y2axistext = QwtText(y2axisname + ' (norm)')
        else:
            yaxistext = QwtText(yaxisname)
            y2axistext = QwtText(y2axisname)
        yaxistext.setFont(self.labelfont)
        y2axistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.yLeft, yaxistext)

        self.curves = []
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)
        if self.has_secondary:
            self.setAxisTitle(QwtPlot.yRight, y2axistext)

        try:
            xscale = (self.dataset.positions[0][self.dataset.xindex],
                      self.dataset.positions[-1][self.dataset.xindex])
        except IndexError:
            self.setAxisAutoScale(QwtPlot.xBottom)
        else:
            self.setAxisScale(QwtPlot.xBottom, xscale[0], xscale[1])
        # needed for zoomer base
        self.setAxisAutoScale(QwtPlot.yLeft)
        if self.has_secondary:
            self.setAxisAutoScale(QwtPlot.yRight)
        self.zoomer.setZoomBase(True)   # does a replot

    curvecolor = [Qt.black, Qt.red, Qt.green, Qt.blue,
                  Qt.magenta, Qt.cyan, Qt.darkGray]
    numcolors = len(curvecolor)

    def addCurve(self, i, curve, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = ErrorBarPlotCurve(title=curve.description, curvePen=pen,
                                      errorPen=QPen(Qt.blue, 0),
                                      errorCap=8, errorOnTop=False)
        if not curve.function:
            plotcurve.setSymbol(self.symbol)
        if curve.yaxis == 2:
            plotcurve.setYAxis(QwtPlot.yRight)
            self.has_secondary = True
            self.enableAxis(QwtPlot.yRight)
        if curve.disabled:
            plotcurve.setVisible(False)
        plotcurve.setRenderHint(QwtPlotItem.RenderAntialiased)
        self.setCurveData(curve, plotcurve)
        plotcurve.attach(self)
        if self.legend():
            item = self.legend().find(plotcurve)
            if not plotcurve.isVisible():
                #item.setFont(self.disabledfont)
                item.text().setText('(' + item.text().text() + ')')
        self.curves.append(plotcurve)
        if replot:
            self.zoomer.setZoomBase(True)

    def setCurveData(self, curve, plotcurve):
        x = np.array(curve.datax)
        y = np.array(curve.datay, float)
        dy = None
        if curve.dyindex > -1:
            dy = np.array(curve.datady)
        if self.normalized:
            norm = None
            if curve.monindex > -1:
                norm = np.array(curve.datamon)
            elif curve.timeindex > -1:
                norm = np.array(curve.datatime)
            if norm is not None:
                y /= norm
                if dy is not None: dy /= norm
        plotcurve.setData(x, y, None, dy)

    def pointsAdded(self):
        for curve, plotcurve in zip(self.dataset.curves, self.curves):
            self.setCurveData(curve, plotcurve)
        self.replot()

    def setLegend(self, on):
        if on:
            legend = QwtLegend(self)
            legend.setItemMode(QwtLegend.ClickableItem)
            legend.palette().setColor(QPalette.Base, self.window.userColor)
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
            if isinstance(item, ErrorBarPlotCurve):
                for dep in item.dependent:
                    dep.setVisible(False)
            #legenditem.setFont(self.disabledfont)
            legenditemtext.setText('(' + legenditemtext.text() + ')')
        else:
            item.setVisible(True)
            if isinstance(item, ErrorBarPlotCurve):
                for dep in item.dependent:
                    dep.setVisible(True)
            #legenditem.setFont(self.font())
            legenditemtext.setText(legenditemtext.text())
        self.replot()

    def on_picker_moved(self, point):
        info = "X = %g, Y = %g" % (
            self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def fitGaussPeak(self):
        self._beginFit('Gauss', ['Background', 'Peak', 'Half Maximum'])

    def fitPseudoVoigtPeak(self):
        self._beginFit('Pseudo-Voigt', ['Background', 'Peak', 'Half Maximum'])

    def fitPearsonVIIPeak(self):
        self._beginFit('PearsonVII', ['Background', 'Peak', 'Half Maximum'])

    def fitTc(self):
        self._beginFit('Tc', ['Background', 'Tc'])

    def _beginFit(self, fittype, fitparams):
        if self.fittype is not None:
            return
        if not has_odr:
            return self.showError('scipy.odr is not available.')
        if not self.curves:
            return self.showError('Plot must have a curve to be fitted.')
        self.fitcurve = 0
        if len(self.curves) > 1:
            dlg = QDialog(self)
            loadUi(dlg, 'selector.ui')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for curve in self.dataset.curves:
                QListWidgetItem(curve.description, dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            self.fitcurve = dlg.list.currentRow()
        self.picker.active = False
        self.zoomer.setEnabled(False)
        self.fitvalues = []
        self.fitparams = fitparams
        self.fittype = fittype
        self.fitstage = 0

        self.window.statusBar.showMessage('Fitting: Click on %s' % fitparams[0])
        self.fitPicker = QwtPlotPicker(
            QwtPlot.xBottom, self.curves[self.fitcurve].yAxis(),
            QwtPicker.PointSelection | QwtPicker.ClickSelection,
            QwtPlotPicker.CrossRubberBand,
            QwtPicker.AlwaysOn, self.canvas())
        self.connect(self.fitPicker,
                     SIGNAL('selected(const QwtDoublePoint &)'),
                     self.on_fitPicker_selected)

    def _finishFit(self):
        curve = self.curves[self.fitcurve]
        args = [curve._x, curve._y, curve._dy] + self.fitvalues
        try:
            labelalign = Qt.AlignRight | Qt.AlignBottom
            linefrom = lineto = liney = None
            if self.fittype == 'Gauss':
                title = 'peak fit'
                beta, x, y = fit_gauss(*args)
                labelx = beta[2] + beta[3]
                labely = beta[0] + beta[1]
                interesting = [('Center', beta[2]),
                               ('FWHM', beta[3] * fwhm_to_sigma),
                               ('Int', beta[1]*beta[3]*np.sqrt(2*np.pi))]
                linefrom = beta[2] - beta[3]*fwhm_to_sigma/2
                lineto = beta[2] + beta[3]*fwhm_to_sigma/2
                liney = beta[0] + beta[1]/2
            elif self.fittype == 'Pseudo-Voigt':
                title = 'peak fit (PV)'
                beta, x, y = fit_pseudo_voigt(*args)
                labelx = beta[2] + beta[3]
                labely = beta[0] + beta[1]
                eta = beta[4] % 1.0
                integr = beta[1] * beta[3] * (
                    eta*np.pi + (1-eta)*np.sqrt(np.pi/np.log(2)))
                interesting = [('Center', beta[2]), ('FWHM', beta[3]*2),
                               ('Eta', eta), ('Int', integr)]
                linefrom = beta[2] - beta[3]
                lineto = beta[2] + beta[3]
                liney = beta[0] + beta[1]/2
            elif self.fittype == 'PearsonVII':
                title = 'peak fit (PVII)'
                beta, x, y = fit_pearson_vii(*args)
                labelx = beta[2] + beta[3]
                labely = beta[0] + beta[1]
                interesting = [('Center', beta[2]), ('FWHM', beta[3]*2),
                               ('m', beta[4])]
                linefrom = beta[2] - beta[3]
                lineto = beta[2] + beta[3]
                liney = beta[0] + beta[1]/2
            elif self.fittype == 'Tc':
                title = 'Tc fit'
                beta, x, y = fit_tc(*args)
                labelx = beta[2]  # at Tc
                labely = beta[0]  # at I_background
                labelalign = Qt.AlignLeft | Qt.AlignTop
                interesting = [('Tc', beta[2]), (u'α', beta[3])]
        except FitError, err:
            self.window.statusBar.showMessage('Fitting failed: %s.' % err)
            self.fitPicker.setEnabled(False)
            del self.fitPicker
            self.picker.active = True
            self.zoomer.setEnabled(True)
            self.fittype = None
            return

        color = [Qt.darkRed, Qt.darkMagenta, Qt.darkGreen,
                 Qt.darkGray][self.fits % 4]

        resultcurve = ErrorBarPlotCurve(title=title)
        resultcurve.setYAxis(curve.yAxis())
        resultcurve.setRenderHint(QwtPlotItem.RenderAntialiased)
        resultcurve.setStyle(QwtPlotCurve.Lines)
        resultcurve.setPen(QPen(color, 2))
        resultcurve.setData(x, y)
        resultcurve.attach(self)

        textmarker = QwtPlotMarker()
        textmarker.setLabelAlignment(labelalign)
        textmarker.setLabel(QwtText(
            '\n'.join('%s: %g' % i for i in interesting)))

        # check that the given position is inside the viewport
        xi = self.axisScaleDiv(resultcurve.xAxis()).interval()
        xmin, xmax = xi.minValue(), xi.maxValue()
        yi = self.axisScaleDiv(resultcurve.yAxis()).interval()
        ymin, ymax = yi.minValue(), yi.maxValue()

        labelx = max(labelx, xmin)
        labelx = min(labelx, xmax)
        labely = max(labely, ymin)
        labely = min(labely, ymax)

        textmarker.setValue(labelx, labely)
        textmarker.attach(self)
        resultcurve.dependent.append(textmarker)

        if linefrom:
            linemarker = QwtPlotCurve()
            linemarker.setStyle(QwtPlotCurve.Lines)
            linemarker.setPen(QPen(color, 1))
            linemarker.setItemAttribute(QwtPlotItem.Legend, False)
            linemarker.setData([linefrom, lineto], [liney, liney])
            #linemarker.attach(self)
            #resultcurve.dependent.append(linemarker)

        self.replot()

        self.fitPicker.setEnabled(False)
        del self.fitPicker
        self.picker.active = True
        self.zoomer.setEnabled(True)
        self.fittype = None
        self.fits += 1

    def on_fitPicker_selected(self, point):
        self.fitvalues.append((point.x(), point.y()))
        self.fitstage += 1
        if self.fitstage < len(self.fitparams):
            paramname = self.fitparams[self.fitstage]
            self.window.statusBar.showMessage('Fitting: Click on %s' %
                                              paramname)
        else:
            self._finishFit()
