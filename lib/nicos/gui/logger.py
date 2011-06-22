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

"""NICOS GUI history log window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from PyQt4.QtCore import SIGNAL, QVariant, QSize, Qt
from PyQt4.Qwt5 import QwtPlot, QwtText, QwtSymbol, QwtLegend, QwtPlotItem, \
     QwtPlotZoomer, QwtPlotGrid, QwtPicker, QwtPlotPicker, QwtPlotCurve, \
     QwtLog10ScaleEngine, QwtLinearScaleEngine
from PyQt4.QtGui import QMainWindow, QDialog, QPalette, QFont, QColor, QPen, \
     QBrush, QListWidgetItem, QFontDialog, QColorDialog, QFileDialog, \
     QPrintDialog, QPrinter
from PyQt4.QtCore import pyqtSignature as qtsig

import numpy as np

from nicos.gui.utils import SettingGroup, loadUi, DlgUtils
from nicos.gui.plothelpers import XPlotPicker

TIMEFMT = '%Y-%m-%d %H:%M:%S'

def itemuid(item):
    return str(item.data(32).toString())


class LoggerWindow(QMainWindow, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'History viewer')
        loadUi(self, 'logger.ui')

        self.bulk_adding = False
        self.no_openset = False

        #self.client = parent.client
        #self.data = parent.data

        # maps view uid -> plot
        self.viewplots = {}
        # maps view uid -> list item
        self.viewitems = {}
        # current plot object
        self.currentPlot = None
        # stack of view uids
        self.viewUidStack = []

        self.userFont = self.font()
        self.userColor = self.palette().color(QPalette.Base)

        self.sgroup = SettingGroup('LoggerWindow')
        self.loadSettings()
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

        for plot in self.viewplots.itervalues():
            plot.setFonts(font, bold, larger)

    def changeColor(self):
        for plot in self.viewplots.itervalues():
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
        self.viewList.clear()
        for dataset in self.data.sets:
            if dataset.invisible:
                continue
            item = QListWidgetItem(dataset.name, self.viewList)
            item.setData(32, dataset.uid)
            self.viewitems[dataset.uid] = item

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

    def on_viewList_currentItemChanged(self, item, previous):
        if self.no_openset or item is None:
            return
        self.openDataset(itemuid(item))

    def on_viewList_itemClicked(self, item):
        # this handler is needed in addition to currentItemChanged
        # since one can't change the current item if it's the only one
        if self.no_openset or item is None:
            return
        self.openDataset(itemuid(item))

    def openDataset(self, uid):
        set = self.data.uid2set[uid]
        if set.uid not in self.viewplots:
            self.viewplots[set.uid] = DataSetPlot(self.plotFrame, self, set)
        self.viewList.setCurrentItem(self.viewitems[uid])
        plot = self.viewplots[set.uid]
        self.setCurrentDataset(plot)

    def setCurrentDataset(self, plot):
        if self.currentPlot:
            self.plotLayout.removeWidget(self.currentPlot)
            self.currentPlot.hide()
        self.currentPlot = plot
        if plot is None:
            self.enablePlotActions(False)
        else:
            try: self.viewUidStack.remove(plot.dataset.uid)
            except ValueError: pass
            self.viewUidStack.append(plot.dataset.uid)

            self.enablePlotActions(True)
            self.viewList.setCurrentItem(self.viewitems[plot.dataset.uid])
            self.actionLogScale.setChecked(
                isinstance(plot.axisScaleEngine(QwtPlot.yLeft),
                           QwtLog10ScaleEngine))
            self.actionNormalized.setChecked(plot.normalized)
            self.actionLegend.setChecked(plot.legend() is not None)
            self.plotLayout.addWidget(plot)
            plot.show()

    def on_data_datasetAdded(self, dataset):
        if dataset.uid in self.viewitems:
            self.viewitems[dataset.uid].setText(dataset.name)
            if dataset.uid in self.viewplots:
                self.viewplots[dataset.uid].updateDisplay()
        else:
            self.no_openset = True
            item = QListWidgetItem(dataset.name, self.viewList)
            item.setData(32, dataset.uid)
            self.viewitems[dataset.uid] = item
            if not self.bulk_adding:
                self.openDataset(dataset.uid)
            self.no_openset = False

    def on_data_pointsAdded(self, dataset):
        if dataset.uid in self.viewplots:
            self.viewplots[dataset.uid].pointsAdded()

    @qtsig('')
    def on_actionClosePlot_triggered(self):
        current_set = self.viewUidStack.pop()
        if self.viewUidStack:
            self.setCurrentDataset(self.viewplots[self.viewUidStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.viewplots[current_set]

    @qtsig('')
    def on_actionResetPlot_triggered(self):
        current_set = self.viewUidStack.pop()
        del self.viewplots[current_set]
        self.openDataset(current_set)

    @qtsig('')
    def on_actionDeletePlot_triggered(self):
        current_set = self.viewUidStack.pop()
        self.data.uid2set[current_set].invisible = True
        if self.viewUidStack:
            self.setCurrentDataset(self.viewplots[self.viewUidStack[-1]])
        else:
            self.setCurrentDataset(None)
        del self.viewplots[current_set]
        for i in range(self.viewList.count()):
            if itemuid(self.viewList.item(i)) == current_set:
                self.viewList.takeItem(i)
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
        plotcurve = QwtPlotCurve(title=curve.description, curvePen=pen,
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
