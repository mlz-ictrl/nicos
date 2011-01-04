#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM GUI analysis window
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICM GUI analysis window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qwt5 import *
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicm.gui import data
from nicm.gui.data import DataSet, Curve
from nicm.gui.util import SettingGroup, loadUi, has_odr, fit_gauss, \
     fwhm_to_sigma, FitError, fit_tc, DlgUtils, fit_pseudo_voigt, fit_pearson_vii
from nicm.gui.plothelpers import ErrorBarPlotCurve, XPlotPicker, cloneToGrace

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


class AnalysisWindow(QMainWindow, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Data analysis')
        loadUi(self, 'analysis.ui')

        self.bulk_adding = False
        self.no_openset = False

        self.client = parent.client
        self.data = parent.data

        # maps set number -> plot
        self.setplots = {}
        # maps set number -> list item
        self.setitems = {}
        # current plot object
        self.currentPlot = None
        # stack of set numbers
        self.setNumStack = []

        self.userFont = self.font()
        self.userColor = self.palette().color(QPalette.Base)

        self.sgroup = SettingGroup('AnalysisWindow')
        self.loadSettings()

        self.connect(self.data, SIGNAL('datasetAdded'),
                     self.on_data_datasetAdded)

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
        for action in self.plotToolBar.actions():
            action.setEnabled(on)

    def closeEvent(self, event):
        with self.sgroup as settings:
            settings.setValue('geometry', QVariant(self.saveGeometry()))
            settings.setValue('splitter', QVariant(self.splitter.saveState()))
        event.accept()
        self.emit(SIGNAL('closed'), self)

    def updateList(self):
        self.datasetList.clear()
        for dataset in self.data.sets:
            if dataset.invisible:
                continue
            self.setitems[dataset.num] = \
                QListWidgetItem(dataset.name, self.datasetList, dataset.num)

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
        self.openDataset(item.type())

    def on_datasetList_itemClicked(self, item):
        # this handler is needed in addition to currentItemChanged
        # since one can't change the current item if it's the only one
        if self.no_openset or item is None:
            return
        self.openDataset(item.type())

    def openDataset(self, num):
        set = self.data.num2set[num]
        if set.num not in self.setplots:
            self.setplots[set.num] = DataSetPlot(self.plotFrame, self, set)
        self.datasetList.setCurrentItem(self.setitems[num])
        plot = self.setplots[set.num]
        self.setCurrentDataset(plot)

    def setCurrentDataset(self, plot):
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
        self.currentPlot = plot
        if plot is None:
            self.enablePlotActions(False)
        else:
            try: self.setNumStack.remove(plot.dataset.num)
            except ValueError: pass
            self.setNumStack.append(plot.dataset.num)

            self.enablePlotActions(True)
            self.datasetList.setCurrentItem(self.setitems[plot.dataset.num])
            self.actionLogScale.setChecked(
                isinstance(plot.axisScaleEngine(QwtPlot.yLeft),
                           QwtLog10ScaleEngine))
            self.actionNormalized.setChecked(plot.normalized)
            self.actionLegend.setChecked(plot.legend() is not None)
            self.plotLayout.addWidget(plot)
            plot.show()

    def on_data_datasetAdded(self, dataset):
        if dataset.num in self.setitems:
            self.setitems[dataset.num].setText(dataset.name)
            if dataset.num in self.setplots:
                self.setplots[dataset.num].updateDisplay()
        else:
            self.no_openset = True
            self.setitems[dataset.num] = \
                QListWidgetItem(dataset.name, self.datasetList, dataset.num)
            if not self.bulk_adding:
                self.openDataset(dataset.num)
            self.no_openset = False

    @qtsig('')
    def on_actionClosePlot_triggered(self):
        current_set = self.setNumStack.pop()
        if self.setNumStack:
            self.setCurrentDataset(self.setplots[self.setNumStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.setplots[current_set]

    @qtsig('')
    def on_actionResetPlot_triggered(self):
        current_set = self.setNumStack.pop()
        del self.setplots[current_set]
        self.openDataset(current_set)

    @qtsig('')
    def on_actionDeletePlot_triggered(self):
        current_set = self.setNumStack.pop()
        self.data.num2set[current_set].invisible = True
        if self.setNumStack:
            self.setCurrentDataset(self.setplots[self.setNumStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.setplots[current_set]
        for i in range(self.datasetList.count()):
            if self.datasetList.item(i).type() == current_set:
                self.datasetList.takeItem(i)
                break

    @qtsig('')
    def on_actionPDF_triggered(self):
        filename = str(QFileDialog.getSaveFileName(
            self, self.tr('Select file name'), '',
            self.tr('PDF files (*.pdf)')))
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
        current = self.currentPlot.dataset.num
        dlg = QDialog(self)
        loadUi(dlg, 'dataops.ui')
        for i in range(self.datasetList.count()):
            item = self.datasetList.item(i)
            newitem = QListWidgetItem(item.text(), dlg.otherList, item.type())
            if item.type() == current:
                dlg.otherList.setCurrentItem(newitem)
                # paint the current set in grey to indicate it's not allowed
                # to be selected
                newitem.setBackground(self.palette().brush(QPalette.Mid))
                newitem.setFlags(Qt.NoItemFlags)
        if dlg.exec_() != QDialog.Accepted:
            return

        items = dlg.otherList.selectedItems()
        sets = [self.data.num2set[current]]
        for item in items:
            if item.type() == current:
                return self.showError('Cannot combine set with itself.')
            sets.append(self.data.num2set[item.type()])
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
        self.connect(self.dataset, SIGNAL('curveAdded'),
                     self.on_dataset_curveAdded)
        self.connect(self.dataset, SIGNAL('pointsAdded'),
                     self.on_dataset_pointsAdded)

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

        title = '<h3>%s</h3><font size="-2">%s</font>' % \
            (self.dataset.title, self.dataset.subtitle)
        self.setTitle(title)
        xaxistext = QwtText(self.dataset.xaxisname)
        xaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.xBottom, xaxistext)
        if self.normalized:
            yaxistext = QwtText(self.dataset.yaxisname + ' (norm)')
            y2axistext = QwtText(self.dataset.y2axisname + ' (norm)')
        else:
            yaxistext = QwtText(self.dataset.yaxisname)
            y2axistext = QwtText(self.dataset.y2axisname)
        yaxistext.setFont(self.labelfont)
        y2axistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.yLeft, yaxistext)

        self.curves = []
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)
        if self.has_secondary:
            self.setAxisTitle(QwtPlot.yRight, y2axistext)

        if self.dataset.xscale == (0,0):
            self.setAxisAutoScale(QwtPlot.xBottom)
        else:
            xmin, xmax = self.dataset.xscale
            self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
        # needed for zoomer base
        self.setAxisAutoScale(QwtPlot.yLeft)
        if self.has_secondary:
            self.setAxisAutoScale(QwtPlot.yRight)
        self.zoomer.setZoomBase(True)   # does a replot

    curvecolor = [Qt.black, Qt.red, Qt.green, Qt.blue,
                  Qt.magenta, Qt.cyan, Qt.darkGray]
    numcolors = len(curvecolor)

    def addCurve(self, i, curve, replot=False):
        if 'map' in curve.modes:
            plotcurve = QwtPlotSpectrogram()
            # XXX
        else:
            pen = QPen(self.curvecolor[i % self.numcolors])
            plotcurve = ErrorBarPlotCurve(title=curve.name, curvePen=pen,
                                          errorPen=QPen(Qt.blue, 0),
                                          errorCap=8, errorOnTop=False)
            if 'lines' not in curve.modes:
                plotcurve.setSymbol(self.symbol)
            if 'points' in curve.modes:
                plotcurve.setStyle(QwtPlotCurve.NoCurve)
            if 'y2' in curve.modes:
                plotcurve.setYAxis(QwtPlot.yRight)
                self.has_secondary = True
                self.enableAxis(QwtPlot.yRight)
            if 'disabled' in curve.modes:
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

    def on_dataset_curveAdded(self, curve):
        self.addCurve(len(self.dataset.curves)-1, curve, True)

    def setCurveData(self, curve, plotcurve):
        if 'map' in curve.modes:
            pass # XXX
        else:
            x = curve.data[:, data.X]
            y = curve.data[:, data.Y]
            dx = dy = None
            if curve.has_dx:
                dx = curve.data[:, data.DX]
            if curve.has_dy:
                dy = curve.data[:, data.DY]
            if self.normalized and curve.n_norm:
                y = y.copy()
                if dy is not None: dy = dy.copy()
                for i in range(data.FIRST_NORM, data.FIRST_NORM+curve.n_norm):
                    normval = curve.data[:,i]
                    y /= normval
                    if dy is not None: dy /= normval
            plotcurve.setData(x, y, dx, dy)

    def on_dataset_pointsAdded(self, index):
        try:
            plotcurve = self.curves[index]
            curve = self.dataset.curves[index]
        except IndexError:
            print 'Invalid curve index'
            return
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
            dlg.setWindowTitle(self.tr('Select curve to fit'))
            dlg.label.setText(self.tr('Select a curve:'))
            for curve in self.dataset.curves:
                QListWidgetItem(curve.name, dlg.list)
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

        self.window.statusBar.showMessage(
            self.tr('Fitting: Click on %1').arg(fitparams[0]))
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
            self.window.statusBar.showMessage(
                self.tr('Fitting failed: %1.').arg(str(err)))
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
            self.window.statusBar.showMessage(
                self.tr('Fitting: Click on %1').arg(paramname))
        else:
            self._finishFit()
