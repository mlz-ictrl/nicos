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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import os
import tempfile

from time import localtime, strftime

from PyQt4.Qwt5 import Qwt, QwtPlot, QwtPlotItem, QwtPlotCurve, QwtPlotPicker, \
    QwtLog10ScaleEngine, QwtSymbol, QwtPlotZoomer, QwtPicker, QwtPlotGrid, \
    QwtText, QwtLegend, QwtPlotMarker, QwtPlotPanner, QwtLinearScaleEngine
from PyQt4.QtGui import QPen, QPainter, QBrush, QPalette, QFileDialog, \
    QPrinter, QPrintDialog, QDialog, QImage
from PyQt4.QtCore import Qt, QRectF, QLine, QSize, SIGNAL

import numpy as np

from nicos.clients.gui.widgets.plotting import NicosPlot, ViewPlotMixin, \
    DataSetPlotMixin, GaussFitter, prepareData
from nicos.pycompat import string_types
from nicos.guisupport.plots import ActivePlotPicker, TimeScaleEngine, \
    TimeScaleDraw


class ErrorBarPlotCurve(QwtPlotCurve):
    """
    Copied from Qwt examples and applied some fixes.
    """

    def __init__(self, x=None, y=None, dx=None, dy=None,
                 curvePen=QPen(Qt.black, 1), curveStyle=QwtPlotCurve.Lines,
                 curveSymbol=QwtSymbol(), errorPen=QPen(Qt.NoPen),
                 errorCap=0, errorOnTop=False, title=None):
        x = x if x is not None else []
        y = y if y is not None else []
        if title is not None:
            QwtPlotCurve.__init__(self, title)
        else:
            QwtPlotCurve.__init__(self)
        self.setData(x, y, dx, dy)
        self.setPen(curvePen)
        self.setStyle(curveStyle)
        self.setSymbol(curveSymbol)
        self.errorPen = errorPen
        self.errorCap = errorCap
        self.errorOnTop = errorOnTop
        self.dependent = []

    def setData(self, x, y, dx=None, dy=None):
        self._x = np.asarray(x, float)
        if len(self._x.shape) != 1:
            raise RuntimeError('len(asarray(x).shape) != 1')

        self._y = np.asarray(y, float)
        if len(self._y.shape) != 1:
            raise RuntimeError('len(asarray(y).shape) != 1')
        if len(self._x) != len(self._y):
            raise RuntimeError('len(asarray(x)) != len(asarray(y))')

        if dx is None:
            self._dx = None
        else:
            self._dx = np.asarray(dx, float)
        if self._dx is not None and len(self._dx.shape) not in [0, 1, 2]:
            raise RuntimeError('len(asarray(dx).shape) not in [0, 1, 2]')

        if dy is None:
            self._dy = dy
        else:
            self._dy = np.asarray(dy, float)
        if self._dy is not None and len(self._dy.shape) not in [0, 1, 2]:
            raise RuntimeError('len(asarray(dy).shape) not in [0, 1, 2]')

        QwtPlotCurve.setData(self, self._x, self._y)

    def boundingRect(self):
        if len(self._x) == 0 or len(self._y) == 0:
            return QRectF()

        logplot = isinstance(self.plot().axisScaleEngine(self.yAxis()),
                             QwtLog10ScaleEngine)

        if self._dx is None:
            xmin = min(self._x)
            xmax = max(self._x)
        elif len(self._dx.shape) in [0, 1]:
            xmin = min(self._x - self._dx)
            xmax = max(self._x + self._dx)
        else:
            xmin = min(self._x - self._dx[0])
            xmax = max(self._x + self._dx[1])

        if self._dy is None:
            ymin = min(self._y)
            ymax = max(self._y)
        elif len(self._dy.shape) in [0, 1]:
            ymin = min(self._y - self._dy)
            ymax = max(self._y + self._dy)
        else:
            ymin = min(self._y - self._dy[0])
            ymax = max(self._y + self._dy[1])

        if logplot and ymin <= 0:
            ymin = QwtPlotCurve.boundingRect(self).y() or 0.1
        return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def drawFromTo(self, painter, xMap, yMap, first, last=-1):
        if last < 0:
            last = self.dataSize() - 1

        logplot = isinstance(self.plot().axisScaleEngine(self.yAxis()),
                             QwtLog10ScaleEngine)

        if self.errorOnTop:
            QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)

        # draw the error bars
        painter.save()
        painter.setPen(self.errorPen)
        # don't draw them antialiased (thick!)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # draw the error bars with caps in the x direction
        if self._dx is not None:
            # draw the bars
            if len(self._dx.shape) in [0, 1]:
                xmin = (self._x - self._dx)
                xmax = (self._x + self._dx)
            else:
                xmin = (self._x - self._dx[0])
                xmax = (self._x + self._dx[1])
            y = self._y
            n, i = len(y), 0
            lines = []
            while i < n:
                yi = yMap.transform(y[i])
                lines.append(QLine(xMap.transform(xmin[i]), yi,
                                   xMap.transform(xmax[i]), yi))
                i += 1
            painter.drawLines(lines)
            if self.errorCap > 0:
                # draw the caps
                cap = self.errorCap / 2
                n, i, = len(y), 0
                lines = []
                while i < n:
                    yi = yMap.transform(y[i])
                    lines.append(
                        QLine(xMap.transform(xmin[i]), yi - cap,
                              xMap.transform(xmin[i]), yi + cap))
                    lines.append(
                        QLine(xMap.transform(xmax[i]), yi - cap,
                              xMap.transform(xmax[i]), yi + cap))
                    i += 1
            painter.drawLines(lines)

        # draw the error bars with caps in the y direction
        if self._dy is not None:
            # draw the bars
            if len(self._dy.shape) in [0, 1]:
                ymin = (self._y - self._dy)
                ymax = (self._y + self._dy)
            else:
                ymin = (self._y - self._dy[0])
                ymax = (self._y + self._dy[1])
            if logplot:
                ymin = ymin.clip(0.1, ymin)
                ymax = ymax.clip(0.1, ymax)
            x = self._x
            n, i, = len(x), 0
            lines = []
            while i < n:
                tx = xMap.transform(x[i])
                lines.append(QLine(tx, yMap.transform(ymin[i]),
                                   tx, yMap.transform(ymax[i])))
                i += 1
            painter.drawLines(lines)
            # draw the caps
            if self.errorCap > 0:
                cap = self.errorCap / 2
                n, i = len(x), 0
                lines = []
                while i < n:
                    tx = xMap.transform(x[i])
                    tymin = yMap.transform(ymin[i])
                    tymax = yMap.transform(ymax[i])
                    lines.append(QLine(tx - cap, tymin, tx + cap, tymin))
                    lines.append(QLine(tx - cap, tymax, tx + cap, tymax))
                    i += 1
            painter.drawLines(lines)

        painter.restore()

        if not self.errorOnTop:
            QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)


class NicosQwtPlot(QwtPlot, NicosPlot):

    def __init__(self, parent, window, timeaxis=False):
        QwtPlot.__init__(self, parent)
        NicosPlot.__init__(self, window, timeaxis=timeaxis)

        self.stdpen = QPen()
        self.symbol = QwtSymbol(QwtSymbol.Ellipse, QBrush(),
                                self.stdpen, QSize(6, 6))
        self.nosymbol = QwtSymbol()

        # setup zooming and unzooming
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())
        self.zoomer.initMousePattern(2)  # this will avoid the middle button,
                                         # which we use for panning
        self.connect(self.zoomer, SIGNAL('zoomed(const QwtDoubleRect &)'),
                     self.on_zoomer_zoomed)

        self.panner = QwtPlotPanner(self.canvas())
        self.panner.setMouseButton(Qt.MidButton)

        # setup picking and mouse tracking of coordinates
        self.picker = ActivePlotPicker(QwtPlot.xBottom, QwtPlot.yLeft,
                                       QwtPicker.PointSelection |
                                       QwtPicker.DragSelection,
                                       QwtPlotPicker.NoRubberBand,
                                       QwtPicker.AlwaysOff,
                                       self.canvas())
        self.fitPicker = None
        self.nfits = 0

        self.setCanvasBackground(self.window.user_color)
        self.canvas().setMouseTracking(True)
        self.connect(self.picker, SIGNAL('moved(const QPoint &)'),
                     self.on_picker_moved)

        self.updateDisplay()

        self.setLegend(True)
        self.connect(self, SIGNAL('legendClicked(QwtPlotItem*)'),
                     self.on_legendClicked)

    def on_zoomer_zoomed(self, rect):
        # when zooming completely out, reset to auto scaling
        if self.zoomer.zoomRectIndex() == 0:
            self.setAxisAutoScale(QwtPlot.xBottom)
            self.setAxisAutoScale(QwtPlot.yLeft)
            self.zoomer.setZoomBase()

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

    def updateDisplay(self):
        self.clear()
        self.has_secondary = False
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.lightGray), 1, Qt.DotLine))
        grid.enableXMin(True)
        grid.attach(self)

        self.setTitle(self.titleString())
        xaxistext = QwtText(self.xaxisName())
        xaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.xBottom, xaxistext)
        if self.timeaxis:
            self.setAxisScaleEngine(QwtPlot.xBottom, TimeScaleEngine())
            self.setAxisScaleDraw(QwtPlot.xBottom, TimeScaleDraw())
        yaxisname = self.yaxisName()
        y2axisname = self.y2axisName()
        if self.normalized:
            yaxistext = QwtText(yaxisname + ' (norm: %s)' % self.normalized)
            y2axistext = QwtText(y2axisname + ' (norm: %s)' % self.normalized)
        else:
            yaxistext = QwtText(yaxisname)
            y2axistext = QwtText(y2axisname)
        yaxistext.setFont(self.labelfont)
        y2axistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.yLeft, yaxistext)

        self.plotcurves = []
        self.addAllCurves()
        if self.has_secondary:
            self.setAxisTitle(QwtPlot.yRight, y2axistext)

        scale = self.xaxisScale()
        if scale is None:
            self.setAxisAutoScale(QwtPlot.xBottom)
        else:
            self.setAxisScale(QwtPlot.xBottom, scale[0], scale[1])
        scale = self.yaxisScale()
        if scale is None:
            self.setAxisAutoScale(QwtPlot.yLeft)
        else:
            self.setAxisScale(QwtPlot.yLeft, scale[0], scale[1])
        if self.has_secondary:
            scale = self.y2axisScale()
            if scale is None:
                self.setAxisAutoScale(QwtPlot.yRight)
            else:
                self.setAxisScale(QwtPlot.yRight, scale[0], scale[1])
        self.zoomer.setZoomBase(True)   # does a replot

    curvecolor = [Qt.black, Qt.red, Qt.darkGreen, Qt.blue,
                  Qt.magenta, Qt.cyan, Qt.darkGray]
    numcolors = len(curvecolor)

    def isLegendEnabled(self):
        return self.legend() is not None

    def setLegend(self, on):
        if on:
            legend = QwtLegend(self)
            legend.setItemMode(QwtLegend.ClickableItem)
            legend.palette().setColor(QPalette.Base, self.window.user_color)
            legend.setBackgroundRole(QPalette.Base)
            self.insertLegend(legend, QwtPlot.BottomLegend)
            for plotcurve in self.plotcurves:
                legenditem = legend.find(plotcurve)
                if not legenditem:
                    continue
                legenditem.setIdentifierWidth(30)
                if not plotcurve.isVisible():
                    newtext = QwtText(legenditem.text())
                    newtext.setColor(Qt.darkGray)
                    legenditem.setText(newtext)
        else:
            self.insertLegend(None)

    def isLogScaling(self, idx=0):
        return isinstance(self.axisScaleEngine(QwtPlot.yLeft),
                          QwtLog10ScaleEngine)

    def setLogScale(self, on):
        self.setAxisScaleEngine(QwtPlot.yLeft,
                                on and QwtLog10ScaleEngine()
                                or QwtLinearScaleEngine())
        self.setAxisScaleEngine(QwtPlot.yRight,
                                on and QwtLog10ScaleEngine()
                                or QwtLinearScaleEngine())
        self.replot()

    def on_legendClicked(self, item):
        self.setVisibility(item, not item.isVisible())
        self.replot()

    def on_picker_moved(self, point):
        info = "X = %g, Y = %g" % (
            self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def setSymbols(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setSymbol(self.symbol)
            else:
                plotcurve.setSymbol(self.nosymbol)
        self.hasSymbols = on
        self.replot()

    def setLines(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setStyle(QwtPlotCurve.Lines)
            else:
                plotcurve.setStyle(QwtPlotCurve.NoCurve)
        self.hasLines = on
        self.replot()

    def unzoom(self):
        self.zoomer.zoom(0)

    def addPlotCurve(self, plotcurve, replot=False):
        plotcurve.setRenderHint(QwtPlotItem.RenderAntialiased)
        plotcurve.attach(self)
        if self.legend():
            legenditem = self.legend().find(plotcurve)
            if legenditem and not plotcurve.isVisible():
                newtext = QwtText(legenditem.text())
                newtext.setColor(Qt.darkGray)
                legenditem.setText(newtext)
        if not plotcurve.isVisible():
            plotcurve.setItemAttribute(QwtPlotItem.AutoScale, False)
        self.plotcurves.append(plotcurve)
        if replot:
            self.zoomer.setZoomBase(True)

    def savePlot(self):
        filename = QFileDialog.getSaveFileName(
            self, 'Select file name', '', 'PDF files (*.pdf)')
        if filename == '':
            return None
        if '.' not in filename:
            filename += '.pdf'
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName(filename)
        printer.setCreator('NICOS plot')
        color = self.canvasBackground()
        self.setCanvasBackground(Qt.white)
        self.print_(printer)
        self.setCanvasBackground(color)
        return filename

    def printPlot(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.print_(printer)
            return True
        return False

    def saveQuietly(self):
        img = QImage(800, 600, QImage.Format_RGB32)
        img.fill(0xffffff)
        self.print_(img)
        h, pathname = tempfile.mkstemp('.png')
        os.close(h)
        img.save(pathname, 'png')
        return pathname

    def _getCurveData(self, curve):
        if isinstance(curve, ErrorBarPlotCurve):
            return [curve._x, curve._y, curve._dy]
        else:
            d = curve.data()
            return [np.asarray(d.xData()), np.asarray(d.yData()), None]

    def _getCurveLegend(self, curve):
        return curve.title().text()

    def _isCurveVisible(self, curve):
        return curve.isVisible()

    def setVisibility(self, item, on):
        item.setVisible(on)
        item.setItemAttribute(QwtPlotItem.AutoScale, on)
        if isinstance(item, ErrorBarPlotCurve):
            for dep in item.dependent:
                dep.setVisible(on)
        if self.legend():
            legenditem = self.legend().find(item)
            if legenditem:
                newtext = QwtText(legenditem.text())
                if on:
                    newtext.setColor(Qt.black)
                else:
                    newtext.setColor(Qt.darkGray)
                legenditem.setText(newtext)

    def _enterFitMode(self):
        self.picker.active = False
        fitcurve = self.selectCurve()
        self.zoomer.setEnabled(False)
        self.fitPicker = QwtPlotPicker(
            QwtPlot.xBottom, fitcurve.yAxis(),
            QwtPicker.PointSelection | QwtPicker.ClickSelection,
            QwtPlotPicker.CrossRubberBand,
            QwtPicker.AlwaysOn, self.canvas())
        self.connect(self.fitPicker,
                     SIGNAL('selected(const QwtDoublePoint &)'),
                     self.on_fitPicker_selected)

    def on_fitPicker_selected(self, point):
        self.fitter.addPick((point.x(), point.y()))

    def _fitRequestPick(self, paramname):
        self.window.statusBar.showMessage('Fitting: Click on %s' % paramname)

    def _leaveFitMode(self):
        self.fitter = None
        if self.fitPicker:
            self.fitPicker.setEnabled(False)
            self.fitPicker = None
        self.picker.active = True
        self.zoomer.setEnabled(True)

    def _plotFit(self, fitter):
        color = [Qt.darkRed, Qt.darkMagenta, Qt.darkGreen,
                 Qt.darkGray][self.nfits % 4]

        resultcurve = ErrorBarPlotCurve(title=fitter.title)
        resultcurve.setYAxis(fitter.curve.yAxis())
        resultcurve.setRenderHint(QwtPlotItem.RenderAntialiased)
        resultcurve.setStyle(QwtPlotCurve.Lines)
        resultcurve.setPen(QPen(color, 2))
        resultcurve.setData(fitter.xfit, fitter.yfit)
        resultcurve.attach(self)

        textmarker = QwtPlotMarker()
        textmarker.setYAxis(fitter.curve.yAxis())
        textmarker.setLabel(QwtText('\n'.join(
            (n + ': ' if n else '') +
            (v if isinstance(v, string_types) else '%g' % v) +
            (dv if isinstance(dv, string_types) else ' +/- %g' % dv)
            for (n, v, dv) in fitter.interesting)))

        # check that the given position is inside the viewport
        halign = Qt.AlignRight
        xi = self.axisScaleDiv(resultcurve.xAxis()).interval()
        xmin, xmax = xi.minValue(), xi.maxValue()
        extentx = self.canvasMap(QwtPlot.xBottom).invTransform(
            textmarker.label().textSize().width())
        labelx, labely = fitter.labelx, fitter.labely
        if xmin < xmax:
            if labelx < xmin:
                labelx = xmin
            elif labelx + extentx > xmax:
                labelx = xmax
                halign = Qt.AlignLeft
        else:
            if labelx > xmin:
                labelx = xmin
            elif labelx - extentx < xmax:
                labelx = xmax
                halign = Qt.AlignLeft

        textmarker.setLabelAlignment(halign | Qt.AlignBottom)
        textmarker.setValue(labelx, labely)
        textmarker.attach(self)
        resultcurve.dependent.append(textmarker)

        # if fitter.lineinfo:
        #     linefrom, lineto, liney = fitter.lineinfo
        #     linemarker = QwtPlotCurve()
        #     linemarker.setStyle(QwtPlotCurve.Lines)
        #     linemarker.setPen(QPen(color, 1))
        #     linemarker.setItemAttribute(QwtPlotItem.Legend, False)
        #     linemarker.setData([linefrom, lineto], [liney, liney])
        #     #linemarker.attach(self)
        #     #resultcurve.dependent.append(linemarker)

        self.nfits += 1
        self.replot()

    def _modifyCurve(self, curve, op):
        if isinstance(curve, ErrorBarPlotCurve):
            new_y = [eval(op, {'x': v1, 'y': v2})
                     for (v1, v2) in zip(curve._x, curve._y)]
            curve.setData(curve._x, new_y, curve._dx, curve._dy)
        else:
            curve.setData(
                curve.xData(),
                [eval(op, {'x': v1, 'y': v2})
                 for (v1, v2) in zip(curve.xData(), curve.yData())])

    def update(self):
        self.replot()


class ViewPlot(ViewPlotMixin, NicosQwtPlot):
    def __init__(self, parent, window, view):
        ViewPlotMixin.__init__(self, view)
        NicosQwtPlot.__init__(self, parent, window, timeaxis=True)

    def cleanup(self):
        pass

    # pylint: disable=W0221
    def on_picker_moved(self, point, strf=strftime, local=localtime):
        # overridden to show the correct timestamp
        tstamp = local(int(self.invTransform(QwtPlot.xBottom, point.x())))
        info = "X = %s, Y = %g" % (
            strf('%y-%m-%d %H:%M:%S', tstamp),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def addCurve(self, i, series, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = QwtPlotCurve(series.title)
        plotcurve.setPen(pen)
        plotcurve.setSymbol(self.nosymbol)
        plotcurve.setStyle(QwtPlotCurve.Lines)
        plotcurve.setData(series.x[:series.n], series.y[:series.n])
        self.series2curve[series] = plotcurve
        self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, series):
        curve = self.series2curve[series]
        curve.setData(series.x[:series.n], series.y[:series.n])
        curve.setTitle(series.title)
        self.replot()


class DataSetPlot(DataSetPlotMixin, NicosQwtPlot):
    def __init__(self, parent, window, dataset):
        DataSetPlotMixin.__init__(self, dataset)
        NicosQwtPlot.__init__(self, parent, window)

    def addCurve(self, i, curve, replot=False):
        if self.current_xname != 'Default' and \
           self.current_xname not in curve.datax:
            return
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
            plotcurve.setVisible(False)
            plotcurve.setItemAttribute(QwtPlotItem.Legend, False)
        self.setCurveData(curve, plotcurve)
        self.addPlotCurve(plotcurve, replot)

    def setCurveData(self, curve, plotcurve):
        xname = curve.default_xname \
            if self.current_xname == 'Default' else self.current_xname
        norm = curve.datanorm[self.normalized] if self.normalized else None
        x, y, dy = prepareData(curve.datax[xname], curve.datay, curve.datady,
                               norm)
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
        if curve and len(curve.datay) == 1:
            self.zoomer.setZoomBase(True)
        else:
            self.replot()

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
        fitcurve = self.plotcurves[whichcurve]
        data = fitcurve.data()
        # try to find good starting parameters
        peakx, peaky = data.x(whichindex), data.y(whichindex)
        # use either left or right end of curve as background
        leftx, lefty = data.x(0), data.y(0)
        rightx, righty = data.x(data.size() - 1), data.y(data.size() - 1)
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
        self.fitter = GaussFitter(self, self.window, None, fitcurve)
        self.fitter.values = [(backx, backy), (peakx, peaky),
                              (fwhmx, peaky / 2.)]
        self.fitter.begin()
        self.fitter.finish()
