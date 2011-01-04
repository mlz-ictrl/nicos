#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM GUI plotting helpers
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

"""NICM GUI plotting helpers."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from numpy import asarray

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qwt5 import *

try:
    from PyQt4.Qwt5.grace import GracePlotter
except ImportError:
    GracePlotter = None


class SpectrogramData(QwtRasterData):
    def __init__(self, xscale, yscale, curve):
        QwtRasterData.__init__(self, QRectF(xscale[0], yscale[0],
                                            xscale[1], yscale[1]))
        self.curve = curve

    def copy(self):
        return self

    def range(self):
        return QwtDoubleInterval(0.0, 10.0);

    def value(self, x, y):
        return 1


class XPlotPicker(QwtPlotPicker):
    """QwtPlotPicker that emits mouse move events when activated."""
    def __init__(self, *args):
        QwtPlotPicker.__init__(self, *args)
        self.active = True

    def widgetMouseMoveEvent(self, event):
        if self.active:
            self.emit(SIGNAL('moved(const QPoint &)'), event.pos())
        return QwtPlotPicker.widgetMouseMoveEvent(self, event)


def cloneToGrace(plot, saveall="", pause=0.2):
    """Clone the plot into Grace for very high quality hard copy output.

    Know bug: Grace does not scale the data correctly when Grace cannot
    cannot keep up with gracePlot.  This happens when it takes too long
    to load Grace in memory (exit the Grace process and try again) or
    when 'pause' is too short.

    Cloned from the Qwt5.qplt module and applied some fixes.
    """
    g = GracePlotter(debug=0)
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
        xmin = plot.axisScaleDiv(xAxis).lBound()
        xmax = plot.axisScaleDiv(xAxis).hBound()
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
        ymin = plot.axisScaleDiv(yAxis).lBound()
        ymax = plot.axisScaleDiv(yAxis).hBound()
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
            ymin = QwtPlotCurve.boundingRect(self).y()
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
                min_y = self._y.min()
                ymin = ymin.clip(min_y, ymin)
            x = self._x
            n, i, = len(x), 0
            lines = []
            while i < n:
                xi = xMap.transform(x[i])
                tmin = yMap.transform(ymin[i])
                lines.append(QLine(xi, tmin,
                                   xi, yMap.transform(ymax[i])))
                i += 1
            painter.drawLines(lines)
            # draw the caps
            if self.errorCap > 0:
                cap = self.errorCap/2
                n, i = len(x), 0
                lines = []
                while i < n:
                    xi = xMap.transform(x[i])
                    tmin = yMap.transform(ymin[i])
                    lines.append(
                        QLine(xi - cap, tmin,
                              xi + cap, tmin))
                    lines.append(
                        QLine(xi - cap, yMap.transform(ymax[i]),
                              xi + cap, yMap.transform(ymax[i])))
                    i += 1
            painter.drawLines(lines)

        painter.restore()

        if not self.errorOnTop:
            QwtPlotCurve.drawFromTo(self, painter, xMap, yMap, first, last)
