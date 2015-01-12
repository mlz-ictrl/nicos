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
    QPrinter, QPrintDialog, QDialog, QImage, QListWidgetItem, QMessageBox
from PyQt4.QtCore import Qt, QRectF, QLine, QSize, SIGNAL

import numpy as np

from nicos.clients.gui.utils import DlgPresets, dialogFromUi
from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.fitutils import has_odr, FitError, fit_gauss, \
    fwhm_to_sigma, fit_tc, fit_pseudo_voigt, fit_pearson_vii, fit_arby, fit_linear
from nicos.clients.gui.widgets.plotting import NicosPlot
from nicos.pycompat import string_types
from nicos.guisupport.plots import ActivePlotPicker, TimeScaleEngine, \
    TimeScaleDraw


TIMEFMT = '%Y-%m-%d %H:%M:%S'


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

    def setData(self, x, y, dx = None, dy = None):
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
        return QRectF(xmin, ymin, xmax-xmin, ymax-ymin)

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
                cap = self.errorCap/2
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
                cap = self.errorCap/2
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
            yaxistext = QwtText(yaxisname + ' (norm)')
            y2axistext = QwtText(y2axisname + ' (norm)')
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

    def _beginFit(self, fittype, fitparams, fitcallback, pickcallback=None):
        if self.fittype is not None:
            return
        if not has_odr:
            return self.showError('scipy.odr is not available.')
        if not self.plotcurves:
            return self.showError('Plot must have a curve to be fitted.')
        fitcurve = self.selectCurve()
        if not fitcurve:
            return
        self.fitcurve = fitcurve
        self.fitvalues = []
        self.fitparams = fitparams
        self.fittype = fittype
        self.fitstage = 0
        self.fitcallbacks = [fitcallback, pickcallback]
        if self.fitparams:
            self.picker.active = False
            self.zoomer.setEnabled(False)

            self.window.statusBar.showMessage('Fitting: Click on %s' %
                                              fitparams[0])
            self.fitPicker = QwtPlotPicker(
                QwtPlot.xBottom, self.fitcurve.yAxis(),
                QwtPicker.PointSelection | QwtPicker.ClickSelection,
                QwtPlotPicker.CrossRubberBand,
                QwtPicker.AlwaysOn, self.canvas())
            self.connect(self.fitPicker,
                         SIGNAL('selected(const QwtDoublePoint &)'),
                         self.on_fitPicker_selected)
        else:
            self._finishFit()

    def _finishFit(self):
        try:
            if self.fitcallbacks[1]:
                if not self.fitcallbacks[1]():  # pylint: disable=E1102
                    raise FitError('Aborted.')
            curve = self.fitcurve
            if isinstance(curve, ErrorBarPlotCurve):
                args = [curve._x, curve._y, curve._dy] + self.fitvalues
            else:
                d = curve.data()
                args = [np.asarray(d.xData()), np.asarray(d.yData()), None] + \
                    self.fitvalues
            x, y, title, labelx, labely, interesting, lineinfo = \
                self.fitcallbacks[0](args)  # pylint: disable=E1102
        except FitError as err:
            self.showInfo('Fitting failed: %s.' % err)
            if self.fitPicker:
                self.fitPicker.setEnabled(False)
                self.fitPicker = None
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
        textmarker.setYAxis(curve.yAxis())
        textmarker.setLabel(QwtText(
            '\n'.join((n + ': ' if n else '') +
                      (v if isinstance(v, string_types) else '%g' % v)
                      for (n, v) in interesting)))

        # check that the given position is inside the viewport
        halign = Qt.AlignRight
        xi = self.axisScaleDiv(resultcurve.xAxis()).interval()
        xmin, xmax = xi.minValue(), xi.maxValue()
        extentx = self.canvasMap(QwtPlot.xBottom).invTransform(
            textmarker.label().textSize().width())
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

        if lineinfo:
            linefrom, lineto, liney = lineinfo
            linemarker = QwtPlotCurve()
            linemarker.setStyle(QwtPlotCurve.Lines)
            linemarker.setPen(QPen(color, 1))
            linemarker.setItemAttribute(QwtPlotItem.Legend, False)
            linemarker.setData([linefrom, lineto], [liney, liney])
            #linemarker.attach(self)
            #resultcurve.dependent.append(linemarker)

        self.replot()

        if self.fitPicker:
            self.fitPicker.setEnabled(False)
            self.fitPicker = None
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


class ViewPlot(NicosPlot):
    def __init__(self, parent, window, view):
        self.series2curve = {}
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
        for i, series in enumerate(self.view.series.values()):
            self.addCurve(i, series)

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

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
        curvename = series.name
        if series.info:
            curvename += ' (' + series.info + ')'
        plotcurve = QwtPlotCurve(curvename)
        plotcurve.setPen(pen)
        plotcurve.setSymbol(self.nosymbol)
        plotcurve.setStyle(QwtPlotCurve.Lines)
        plotcurve.setData(series.x[:series.n], series.y[:series.n])
        self.series2curve[series] = plotcurve
        self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, series):
        self.series2curve[series].setData(series.x[:series.n], series.y[:series.n])
        self.replot()

    def selectCurve(self):
        if not self.plotcurves:
            return
        if len(self.plotcurves) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for plotcurve in self.plotcurves:
                QListWidgetItem(plotcurve.title().text(), dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = dlg.list.currentRow()
        else:
            fitcurve = 0
        return self.plotcurves[fitcurve]

    def fitLinear(self):
        return self._beginFit('Linear', ['First point', 'Second point'],
                              self.linear_fit_callback)

    def linear_fit_callback(self, args):
        title = 'linear fit'
        beta, x, y = fit_linear(*args)
        _x1, x2 = min(x), max(x)
        labelx = x2
        labely = beta[0] * x2 + beta[1]
        interesting = [('Slope', '%.3f /s' % beta[0]),
                       ('', '%.3f /min' % (beta[0] * 60)),
                       ('', '%.3f /h' % (beta[0] * 3600))]
        return x, y, title, labelx, labely, interesting, None

    def saveData(self):
        curvenames = [plotcurve.title().text() for plotcurve in self.plotcurves]
        dlg = DataExportDialog(self, curvenames,
                               'Select curve, file name and format',
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
                    fp.write('%s\t%.10f\n' % (strftime(
                        '%Y-%m-%d.%H:%M:%S', localtime(curve.x(i))),
                        curve.y(i)))


arby_functions = {
    'Gaussian x2': ('a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
                    'a b c x1 x2 s1 s2'),
    'Gaussian x3 symm.':
        ('a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
         'c*exp(-(x-x0)**2/s0**2)', 'a b c x0 x1 s0 s1'),
    'Parabola': ('a*x**2 + b*x + c', 'a b c'),
}

class DataSetPlot(NicosQwtPlot):
    def __init__(self, parent, window, dataset):
        self.dataset = dataset
        NicosQwtPlot.__init__(self, parent, window)

    def titleString(self):
        return '<h3>Scan %s</h3><font size="-2">%s, started %s</font>' % \
            (self.dataset.name, self.dataset.scaninfo,
             strftime(TIMEFMT, self.dataset.started))

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
        except (IndexError, TypeError, ValueError):
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
        remaining = len(self.plotcurves)
        for plotcurve in self.plotcurves:
            namestr = str(plotcurve.title().text())
            if namestr in visible:
                self.setVisibility(plotcurve, visible[namestr])
                changed = True
                if not visible[namestr]:
                    remaining -= 1
        # no visible curve left?  enable all of them again
        if not remaining:
            for plotcurve in self.plotcurves:
                # only if it has a legend item (excludes monitor/time columns)
                if plotcurve.testItemAttribute(QwtPlotItem.Legend):
                    self.setVisibility(plotcurve, True)
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
        op = dlg.operation.text()
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
        return self._beginFit('Gauss', ['Background', 'Peak', 'Half Maximum'],
                              self.gauss_callback)

    def gauss_callback(self, args):
        title = 'peak fit'
        beta, x, y = fit_gauss(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]),
                       ('FWHM', beta[3] * fwhm_to_sigma),
                       ('Ampl', beta[1]),
                       ('Integr', beta[1] * beta[3] * np.sqrt(2 * np.pi))]
        linefrom = beta[2] - beta[3] * fwhm_to_sigma / 2
        lineto = beta[2] + beta[3] * fwhm_to_sigma / 2
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPseudoVoigtPeak(self):
        return self._beginFit('Pseudo-Voigt', ['Background', 'Peak', 'Half Maximum'],
                              self.pv_callback)

    def pv_callback(self, args):
        title = 'peak fit (PV)'
        beta, x, y = fit_pseudo_voigt(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        eta = beta[4] % 1.0
        integr = beta[1] * beta[3] * (
            eta * np.pi + (1 - eta) * np.sqrt(np.pi / np.log(2)))
        interesting = [('Center', beta[2]), ('FWHM', beta[3] * 2),
                       ('Eta', eta), ('Integr', integr)]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPearsonVIIPeak(self):
        return self._beginFit('PearsonVII', ['Background', 'Peak', 'Half Maximum'],
                              self.pvii_callback)

    def pvii_callback(self, args):
        title = 'peak fit (PVII)'
        beta, x, y = fit_pearson_vii(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]), ('FWHM', beta[3] * 2),
                       ('m', beta[4])]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitTc(self):
        return self._beginFit('Tc', ['Background', 'Tc'], self.tc_callback)

    def tc_callback(self, args):
        title = 'Tc fit'
        beta, x, y = fit_tc(*args)
        labelx = beta[2]  # at Tc
        labely = beta[0] + beta[1]  # at I_max
        interesting = [('Tc', beta[2]), (u'α', beta[3])]
        return x, y, title, labelx, labely, interesting, None

    def fitArby(self):
        return self._beginFit('Arbitrary', [], self.arby_callback,
                              self.arby_pick_callback)

    def arby_callback(self, args):
        title = 'fit'
        beta, x, y = fit_arby(*args)
        labelx = x[0]
        labely = y.max()
        interesting = list(zip(self.fitvalues[1], beta))
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
            func, params = arby_functions[item.text()]
            dlg.function.setText(func)
            dlg.fitparams.setPlainText('\n'.join(
                p + ' = ' for p in params.split()))
        dlg.connect(dlg.oftenUsed,
                    SIGNAL('itemClicked(QListWidgetItem *)'), click_cb)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return False
        pr.save()
        fcn = dlg.function.text()
        try:
            xmin = float(dlg.xfrom.text())
        except ValueError:
            xmin = None
        try:
            xmax = float(dlg.xto.text())
        except ValueError:
            xmax = None
        if xmin is not None and xmax is not None and xmin > xmax:
            xmax, xmin = xmin, xmax
        params, values = [], []
        for line in dlg.fitparams.toPlainText().splitlines():
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
        self.fitvalues = [(backx, backy), (peakx, peaky), (fwhmx, peaky / 2.)]
        self.fitparams = ['Background', 'Peak', 'Half Maximum']
        self.fittype = 'Gauss'
        self.fitcallbacks = [self.gauss_callback, None]
        self._finishFit()
