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

"""NICOS GUI plotting helpers."""

__version__ = "$Revision$"

import os
import time
import tempfile

from numpy import asarray

from PyQt4.QtCore import Qt, QRectF, QLine, QSize, SIGNAL
from PyQt4.QtGui import QPen, QPainter, QBrush, QPalette, QFont, QFileDialog, \
     QPrinter, QPrintDialog, QDialog, QImage
from PyQt4.Qwt5 import Qwt, QwtPlot, QwtPlotItem, QwtPlotCurve, QwtPlotPicker, \
     QwtLog10ScaleEngine, QwtSymbol, QwtPlotZoomer, QwtPicker, QwtPlotGrid, \
     QwtText, QwtLegend, QwtScaleDraw

try:
    from PyQt4.Qwt5.grace import GraceProcess
except ImportError:
    GraceProcess = None


class ActivePlotPicker(QwtPlotPicker):
    """QwtPlotPicker that emits mouse move events when activated."""
    def __init__(self, *args):
        QwtPlotPicker.__init__(self, *args)
        self.active = True

    def widgetMouseMoveEvent(self, event):
        if self.active:
            self.emit(SIGNAL('moved(const QPoint &)'), event.pos())
        return QwtPlotPicker.widgetMouseMoveEvent(self, event)


class ErrorBarPlotCurve(QwtPlotCurve):
    """
    Copied from Qwt examples and applied some fixes.
    """

    def __init__(self, x=[], y=[], dx=None, dy=None,
                 curvePen=QPen(Qt.black, 1), curveStyle=QwtPlotCurve.Lines,
                 curveSymbol=QwtSymbol(), errorPen=QPen(Qt.NoPen),
                 errorCap=0, errorOnTop=False, title=None):
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
        self._x = asarray(x, float)
        if len(self._x.shape) != 1:
            raise RuntimeError, 'len(asarray(x).shape) != 1'

        self._y = asarray(y, float)
        if len(self._y.shape) != 1:
            raise RuntimeError, 'len(asarray(y).shape) != 1'
        if len(self._x) != len(self._y):
            raise RuntimeError, 'len(asarray(x)) != len(asarray(y))'

        if dx is None:
            self._dx = None
        else:
            self._dx = asarray(dx, float)
        if self._dx is not None and len(self._dx.shape) not in [0, 1, 2]:
            raise RuntimeError, 'len(asarray(dx).shape) not in [0, 1, 2]'

        if dy is None:
            self._dy = dy
        else:
            self._dy = asarray(dy, float)
        if self._dy is not None and len(self._dy.shape) not in [0, 1, 2]:
            raise RuntimeError, 'len(asarray(dy).shape) not in [0, 1, 2]'

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


class TimeScaleDraw(QwtScaleDraw):
    def label(self, value, strf=time.strftime, local=time.localtime):
        return QwtText(strf('%y-%m-%d\n%H:%M:%S', local(value)))


class NicosPlot(QwtPlot):
    def __init__(self, parent, window, timeaxis=False):
        QwtPlot.__init__(self, parent)
        self.window = window
        self.plotcurves = []
        self.normalized = False
        self.has_secondary = False
        self.show_all = False
        self.timeaxis = timeaxis

        font = self.window.user_font
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        self.setFonts(font, bold, larger)

        self.stdpen = QPen()
        self.symbol = QwtSymbol(QwtSymbol.Ellipse, QBrush(),
                                self.stdpen, QSize(6, 6))
        self.nosymbol = QwtSymbol()

        # setup zooming and unzooming
        self.zoomer = QwtPlotZoomer(QwtPlot.xBottom, QwtPlot.yLeft,
                                    self.canvas())
        self.zoomer.initMousePattern(3)
        self.connect(self.zoomer, SIGNAL('zoomed(const QwtDoubleRect &)'),
                     self.on_zoomer_zoomed)

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

    def titleString(self):
        raise NotImplementedError
    def xaxisName(self):
        raise NotImplementedError
    def yaxisName(self):
        raise NotImplementedError
    def y2axisName(self):
        return ''
    def xaxisScale(self):
        return None
    def yaxisScale(self):
        return None
    def y2axisScale(self):
        return None

    def updateDisplay(self):
        self.clear()
        self.has_secondary = False
        grid = QwtPlotGrid()
        grid.setPen(QPen(QBrush(Qt.lightGray), 1, Qt.DotLine))
        grid.attach(self)

        self.setTitle(self.titleString())
        xaxistext = QwtText(self.xaxisName())
        xaxistext.setFont(self.labelfont)
        self.setAxisTitle(QwtPlot.xBottom, xaxistext)
        if self.timeaxis:
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

    curvecolor = [Qt.black, Qt.red, Qt.green, Qt.blue,
                  Qt.magenta, Qt.cyan, Qt.darkGray]
    numcolors = len(curvecolor)

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

    def on_legendClicked(self, item):
        self.setVisibility(item, not item.isVisible())
        self.replot()

    def on_picker_moved(self, point):
        info = "X = %g, Y = %g" % (
            self.invTransform(Qwt.QwtPlot.xBottom, point.x()),
            self.invTransform(Qwt.QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

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
        filename = str(QFileDialog.getSaveFileName(
            self, 'Select file name', '', 'PDF files (*.pdf)'))
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
            self.currentPlot.print_(printer)
            return True
        return False

    def savePng(self):
        img = QImage(800, 600, QImage.Format_RGB32)
        img.fill(0xffffff)
        self.print_(img)
        h, pathname = tempfile.mkstemp('.png')
        os.close(h)
        img.save(pathname, 'png')
        return pathname


def cloneToGrace(plot, saveall="", pause=0.2):
    """Clone the plot into Grace for very high quality hard copy output.

    Know bug: Grace does not scale the data correctly when Grace cannot
    cannot keep up with gracePlot.  This happens when it takes too long
    to load Grace in memory (exit the Grace process and try again) or
    when 'pause' is too short.

    Cloned from the Qwt5.qplt module and applied some fixes.
    """
    g = GraceProcess(debug=0)
    g('title "%s"' % str(plot.title().text()).replace('"', '\\"'))
    #g('subtitle "%s"' % self.last_plotinfo['subtitle'].replace('"', '\\"'))
    index = 0
    for xAxis, yAxis, graph, xPlace, yPlace in (
        (QwtPlot.xBottom, QwtPlot.yLeft, 'g0', 'normal', 'normal'),
        (QwtPlot.xBottom, QwtPlot.yRight, 'g1', 'normal', 'opposite'),
        (QwtPlot.xTop, QwtPlot.yLeft, 'g2', 'opposite', 'normal'),
        (QwtPlot.xTop, QwtPlot.yRight, 'g3', 'opposite', 'opposite')
        ):
        if not (plot.axisEnabled(xAxis) and plot.axisEnabled(yAxis)):
            continue
        g('%s on; with %s' % (graph, graph))

        # x-axes
        xmin = plot.axisScaleDiv(xAxis).lowerBound()
        xmax = plot.axisScaleDiv(xAxis).upperBound()
        #majStep = minStep = axisScale.majStep()
        #majStep *= 2
        g('world xmin %g; world xmax %g' % (xmin, xmax))
        g('xaxis label "%s"; xaxis label char size 1.5'
          % plot.axisTitle(xAxis).text())
        g('xaxis label place %s' % xPlace)
        g('xaxis tick place %s' % xPlace)
        g('xaxis ticklabel place %s' % xPlace)
        time.sleep(pause)
        if isinstance(plot.axisScaleEngine(xAxis), QwtLog10ScaleEngine):
            g('xaxes scale Logarithmic')
            g('xaxis tick major 10')
            g('xaxis tick minor ticks 9')
        else:
            g('xaxes scale Normal')
            #g('xaxis tick major %12.6f; xaxis tick minor %12.6f'
            #  % (majStep, minStep))

        # y-axes
        ymin = plot.axisScaleDiv(yAxis).lowerBound()
        ymax = plot.axisScaleDiv(yAxis).upperBound()
        #majStep = minStep = axisScale.majStep()
        #majStep *= 2
        g('world ymin %g; world ymax %g' % (ymin, ymax))
        g('yaxis label "%s"; yaxis label char size 1.5' %
          plot.axisTitle(yAxis).text())
        g('yaxis label place %s' % yPlace)
        g('yaxis tick place %s' % yPlace)
        g('yaxis ticklabel place %s' % yPlace)
        time.sleep(pause)
        if isinstance(plot.axisScaleEngine(yAxis), QwtLog10ScaleEngine):
            g('yaxes scale Logarithmic')
            g('yaxis tick major 10')
            g('yaxis tick minor ticks 9')
        else:
            g('yaxes scale Normal')
            #g('yaxis tick major %12.6f; yaxis tick minor %12.6f' %
            #  (majStep, minStep))

        # curves
        for curve in plot.itemList():
            if not isinstance(curve, QwtPlotCurve):
                continue
            if not curve.isVisible():
                continue
            if not (xAxis == curve.xAxis() and yAxis == curve.yAxis()):
                continue
            g('s%s legend "%s"' % (index, curve.title().text()))
            if curve._dy is not None:
                g('s%s type xydy' % index)
            if curve.symbol().style() > QwtSymbol.NoSymbol:
                g('s%s symbol 1;'
                  's%s symbol size 0.4;'
                  's%s symbol fill pattern 1'
                  % (index, index, index))
            if curve.style():
                g('s%s line linestyle 1' % index)
            else:
                g('s%s line linestyle 0' % index)
            for i in xrange(curve.dataSize()):
                g('%s.s%s point %g, %g' %
                  (graph, index, curve._x[i], curve._y[i]))
                if curve._dy is not None:
                    g('%s.s%s.y1[%s] = %g' %
                      (graph, index, i, curve._dy[i]))
            index += 1

    # finalize
    g('redraw')
    if saveall:
        time.sleep(pause)
        g('saveall "%s"' % saveall)
        time.sleep(pause)
        g.kill()
