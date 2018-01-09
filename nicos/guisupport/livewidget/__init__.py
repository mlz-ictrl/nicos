#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""NICOS livewidget with GR."""

import math

import numpy
import numpy.ma

from nicos.guisupport.qt import pyqtSignal, QWidget, QHBoxLayout

import gr
from gr.pygr.base import GRMeta, GRVisibility
from qtgr import InteractiveGRWidget
from gr.pygr import Plot as OrigPlot, PlotAxes, Point, RegionOfInterest, \
    Coords2D

from nicos.guisupport.grplotting import MaskedPlotCurve

# the empty string means: no live data is coming, only the filename is important
DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4', ''))

COLOR_WHITE = 91
COLOR_BLUE = 4
COLOR_MANGENTA = 7
COLOR_MAXINTENSITY = 1255


def sgn(x):
    if x >= 0:
        return 1
    return -1


class Cellarray(gr.pygr.PlotSurface):

    def drawGR(self):
        if self.visible:
            gr.setcolormap(self.colormap)
            # GKS origin at upper left corner
            # swapped ymin, ymax to get have origin
            # at lower left corner (mirror y)
            gr.cellarray(0, len(self.x), len(self.y), 0,
                         len(self.x), len(self.y), self.z)


class GRWidget(InteractiveGRWidget):
    def __init__(self, widget, **kwds):
        InteractiveGRWidget.__init__(self, widget, **kwds)
        self.widget = widget
        self.adjustSelectRect = self._noadjustSelectRect

    def setAdjustSelection(self, flag):
        if flag:
            self.adjustSelectRect = self._adjustSelectRect
        else:
            self.adjustSelectRect = self._noadjustSelectRect

    def _noadjustSelectRect(self, p0, p1):
        return p0, p1

    def _adjustSelectRect(self, p0, p1):
        # adjust selection so that zoom always keeps the aspect
        img_ratio = self.widget._axesratio
        delta_x, delta_y = p1.x - p0.x, p1.y - p0.y
        rect_ratio = abs(delta_y / (delta_x or 0.0001))
        if rect_ratio < img_ratio:
            np1 = Point(p1.x, p0.y + sgn(delta_y) * abs(delta_x) * img_ratio)
        else:
            np1 = Point(p0.x + sgn(delta_x) * abs(delta_y) / img_ratio, p1.y)
        return p0, np1

    def _zoom(self, dpercent, p0):
        plots = self._getPlotsForPoint(p0)
        if len(plots) == 1:
            self.widget.zoom(plots[0], dpercent, p0)

    def _select(self, p0, p1):
        plots = self._getPlotsForPoint(p0)
        if len(plots) == 1:
            self.widget.select(plots[0], p0, p1)

    def mousePan(self, event):
        self.widget.pan(event.getNDC(), event.getOffset())


class Plot(OrigPlot):
    def __init__(self, widget, **kwds):
        OrigPlot.__init__(self, **kwds)
        self.widget = widget

    # def xpan(self, dp, width, height):
    #     window = gr.inqwindow()
    #     coord = CoordConverter(self._sizex, self._sizey)


class Axes(PlotAxes):
    def __init__(self, widget, xdual=False, ydual=False, **kwds):
        PlotAxes.__init__(self, **kwds)
        self.widget = widget
        self.xdual, self.ydual = xdual, ydual

        self.drawxylines = False
        self.xlines = []  # draw vertical lines at x-coordinates
        self.ylines = []  # draw horizontal lines at y-coordinates
        self.xylinecolor = COLOR_MANGENTA

    def setWindow(self, xmin, xmax, ymin, ymax):
        res = PlotAxes.setWindow(self, xmin, xmax, ymin, ymax)
        # use 2 ** n for tickmarks
        def tick(amin, amax):
            if amin > amax:
                amax, amin = amin, amax
            # calculate next (lower) power of two (2**n) for the
            # full range [amax - amin] and divide this:
            #
            #           ld(amax - amin)  :  number of powers of two => exponent
            #       int(        "      ) :  integral part
            #                               (cut off fractions => floor)
            # 2 ** (  "         "       ):  next lower power of two (2**n)
            # 2 ** (   int( ... ) - 4)  ):  - 4 => divided by 2 ** 4
            return 2 ** (int(math.log(amax - amin, 2)) - 4)
        if self.xdual:
            self.xtick = tick(xmin, xmax)
            self.majorx = 4
        if self.ydual:
            self.ytick = tick(ymin, ymax)
            self.majory = 4
        return res

    def drawGR(self):
        PlotAxes.drawGR(self)
        if self.drawxylines:
            xmin, xmax, ymin, ymax = self.getWindow()
            linecolor = gr.inqlinecolorind()
            gr.setlinecolorind(self.xylinecolor)
            for xpos in self.xlines:
                gr.polyline([xpos, xpos], [ymin, ymax])
            for ypos in self.ylines:
                gr.polyline([xmin, xmax], [ypos, ypos])
            gr.setlinecolorind(linecolor)


class AutoScaleAxes(Axes):

    def scaleWindow(self, xmin, xmax, xtick, ymin, ymax, ytick):
        dx, dy = 0, 0
        if self.autoscale & Axes.SCALE_X:
            dx = xtick
        if self.autoscale & Axes.SCALE_Y:
            dy = ytick
        return xmin - dx, xmax + dx, ymin, ymax + dy

    def doAutoScale(self, curvechanged=None):
        original_win = self.getWindow()
        if original_win and curvechanged:
            vc = self.getVisibleCurves() or self.getCurves()
            c = vc[0]
            xmin, xmax, ymin, ymax = original_win
            cxmin, cxmax, cymin, cymax = min(c.x), max(c.x), min(c.y), max(c.y)
            if cxmax > xmax:
                return original_win
            elif cxmin < xmin:
                return original_win
            self.setWindow(min(cxmin, xmin), max(cxmax, xmax),
                           min(cymin, ymin), max(cymax, ymax))
        return Axes.doAutoScale(self, curvechanged)


class ROI(Coords2D, RegionOfInterest, GRVisibility, GRMeta):

    def __init__(self, *args, **kwargs):
        GRVisibility.__init__(self)
        RegionOfInterest.__init__(self, *args, **kwargs)
        Coords2D.__init__(self, self.x, self.y)

    def drawGR(self):
        if self.visible:
            color = gr.inqlinecolorind()
            gr.setlinecolorind(COLOR_WHITE)
            gr.polyline(self.x, self.y)
            gr.setlinecolorind(color)


class LiveWidgetBase(QWidget):

    closed = pyqtSignal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._array = None
        self._axesrange = (1, 1)  # y, x (rows, cols)
        self._fixedsize = False
        self._axesratio = 1.0
        self._logscale = False
        self._rois = {}

        layout = QHBoxLayout()
        self.gr = GRWidget(self)
        layout.addWidget(self.gr)
        self.setLayout(layout)

        self.plot = Plot(self, viewport=(.1, .95, .1, .95))
        self.axes = Axes(self, viewport=self.plot.viewport, xdual=True,
                         ydual=True)
        self.plot.addAxes(self.axes)
        self.gr.addPlot(self.plot)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def _rescale(self):
        """Implement in derived classes e.g. to rescale different plots in
        respect to the main/cellarray plot."""

    def rescale(self):
        self._rescale()
        self.gr.update()

    def zoom(self, master, dpercent, p0):
        if self.plot == master:
            w, h = self.width(), self.height()
            self.plot.zoom(dpercent, p0, w, h)
            self.rescale()

    def select(self, master, p0, p1):
        if self.plot == master:
            w, h = self.width(), self.height()
            self.plot.select(p0, p1, w, h)
            self.rescale()

    def pan(self, p0, dp):
        w, h = self.width(), self.height()
        self.plot.pan(dp, w, h)
        self.rescale()

    def getZValue(self, event):
        plots = self.gr._getPlotsForPoint(event.getNDC())
        if plots and len(plots) == 1:
            plot = plots[0]
            pWC = event.getWC(plot.viewport)
            if (self._array is not None and plot == self.plot and
                len(self._array.shape) >= 2):
                ny, nx = self._array.shape[:2]
                x, y = int(pWC.x), int(pWC.y)
                if 0 <= x < nx and 0 <= y < ny:
                    return x, y, self._array[y, x]
            return pWC.x, pWC.y

    def setWindow(self, xmin, xmax, ymin, ymax):
        """Sets the current window for this plot and deactivates rescaling
        the window in respect to the current size of the corresponding arrays.

        """
        self.axes.setWindow(xmin, xmax, ymin, ymax)
        self._fixedsize = True
        self._axesratio = float(ymax - ymin) / (xmax - xmin)
        self.gr.keepRatio = False
        self.rescale()

    def setWindowForRoi(self, roi):
        self.setWindow(min(roi.x), max(roi.x), min(roi.y), max(roi.y))

    def updateZData(self):
        """This method will be called whenever the data or the scale has been
        changed. Overwrite this method e.g. to mask values before applying
        logscale."""

    def updateAxesRange(self, nx, ny):
        """This method will be called whenever the shape of the incoming data
        has been changed. Overwrite this method e.g. to rescale the axes."""
        self.axes.setWindow(0, nx, 0, ny)

    def setData(self, array):
        self._array = array
        nz, ny, nx = 1, 1, 1
        newrange = False
        n = len(array.shape)
        if n == 1:
            nx = array.shape[0]
        elif n >= 2:
            nx = array.shape[n - 1]
            ny = array.shape[n - 2]
        if n == 3:
            nz = array.shape[n - 3]
        if not self._fixedsize:
            self._axesratio = ny / float(nx)

        if (ny, nx) != self._axesrange:
            if not self._fixedsize:
                self.updateAxesRange(nx, ny)
                newrange = True
            self.axes.xlines = [nx / 2]
            self.axes.ylines = [ny / 2]

        self._axesrange = (ny, nx)  # rows, cols

        self._setData(array, nx, ny, nz, newrange)

        self.updateZData()
        self.rescale()
        return nz, ny, nx

    def _setData(self, array, nx, ny, nz, newrange):
        """This method will be called whenever the data has been changed.
        If *newrange* is `True` the axesrange (nx, ny) has been changed.
        """

    def getColormap(self):
        return []

    def setColormap(self, colormap):
        pass

    def setROI(self, key, roi):
        x, y, width, height = roi
        xr, yt = x + width, y + height
        roi = self._rois.get(key)
        if roi:
            curves = self.axes.getCurves()
            curves.remove(roi)
        self._rois[key] = ROI(Point(x, y), Point(x, yt), Point(xr, yt),
                              Point(xr, y), Point(x, y))
        self.axes.addCurves(self._rois[key])
        self.gr.update()

    def unzoom(self):
        self.axes.setWindow(0, self._axesrange[1],
                            0, self._axesrange[0])
        self.rescale()

    def printDialog(self):
        self.gr.printDialog()

    def logscale(self, on):
        self._logscale = on
        if self._array is not None:
            self.updateZData()
            self.gr.update()

    def setCenterMark(self, flag):
        self.axes.drawxylines = flag
        self.gr.update()


class LiveWidget(LiveWidgetBase):

    def __init__(self, parent):
        LiveWidgetBase.__init__(self, parent)

        self.axes.setGrid(False)
        self.axes.xylinecolor = COLOR_MAXINTENSITY
        self.surf = Cellarray([0], [0], [0], option=gr.OPTION_CELL_ARRAY)
        self.axes.addCurves(self.surf)

    def updateZData(self):
        arr = self._array.ravel()
        if self._logscale:
            arr = numpy.ma.log10(arr).filled(-1)
        # TODO: implement 'sliders' for amin, amax
        amin, amax = arr.min(), arr.max()
        if amin != amax:
            self.surf.z = 1000 + 255 * (arr - amin) / (amax - amin)
        elif amax > 0:
            self.surf.z = 1000 + 255 * arr / amax
        else:
            self.surf.z = 1000 + arr

    def _setData(self, array, nx, ny, nz, newrange):
        self.surf.x = numpy.linspace(0, nx, nx)
        self.surf.y = numpy.linspace(0, ny, ny)

    def getColormap(self):
        return self.surf.colormap

    def setColormap(self, colormap):
        self.surf.colormap = colormap
        self.gr.update()


class IntegralLiveWidget(LiveWidget):

    def __init__(self, parent):
        LiveWidget.__init__(self, parent)

        self.plot.viewport = (.1, .75, .1, .75)
        self.axes.viewport = self.plot.viewport
        self.plotyint = Plot(self, viewport=(.1, .75, .8, .95))
        self.axesyint = Axes(self, viewport=self.plotyint.viewport,
                             drawX=False, drawY=True, xdual=True)
        self.plotxint = Plot(self, viewport=(.8, .95, .1, .75))
        self.axesxint = Axes(self, viewport=self.plotxint.viewport,
                             drawX=True, drawY=False, ydual=True)

        vp = self.axesxint.viewport
        self._charheight = .024 * (vp[3] - vp[2])

        self.axes.setXtickCallback(self.xtick)
        self.axesxint.setXtickCallback(self.xtick)
        self.axesyint.setYtickCallback(self.yinttick)

        self.plotyint.addAxes(self.axesyint)
        self.plotxint.addAxes(self.axesxint)
        self.curvey = MaskedPlotCurve([0], [0], filly=.1, linecolor=COLOR_BLUE)
        self.curvex = MaskedPlotCurve([0], [0], fillx=.1, linecolor=COLOR_BLUE)

        self.axesyint.addCurves(self.curvey)
        self.axesxint.addCurves(self.curvex)
        self.gr.addPlot(self.plotyint)
        self.gr.addPlot(self.plotxint)

    def xtick(self, x, y, svalue, _value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        gr.text(x, y, svalue)

    def yinttick(self, x, y, svalue, _value):
        gr.setcharheight(self._charheight)
        gr.text(x, y, svalue)

    def _applymask(self):
        """Mask or unmask values in plotcurves if necessary and rescale
        plotaxes in respect to logscale."""
        win = self.axes.getWindow()
        if not win:
            return
        xmin, xmax, ymin, ymax = win
        # set minimum for sum axis in respect to logscale
        # and un-/mask values if necessary
        if self._logscale:
            x0, y0 = .1, .1
            self.curvex.x = numpy.ma.masked_equal(self.curvex.x, 0)
            self.curvey.y = numpy.ma.masked_equal(self.curvey.y, 0)
        else:  # unmask if masked if not logscale
            x0, y0 = 0, 0
            if numpy.ma.is_masked(self.curvex._x):
                self.curvex.x = self.curvex._x.filled(0)
            if numpy.ma.is_masked(self.curvey._y):
                self.curvey.y = self.curvey._y.filled(0)
        # rescale axes
        self.axesyint.setWindow(xmin - .5, xmax - .5, y0, self.curvey.y.max())
        self.axesxint.setWindow(x0, self.curvex.x.max(), ymin - .5, ymax - .5)

    def _rescale(self):
        """Rescales integral plots in respect to the main/cellarray plot."""
        xmin, xmax, ymin, ymax = self.axes.getWindow()
        ny, nx = self._array.shape
        # calculate x, y range clamped to detector image size
        x0 = min(max(0, xmin), xmax)  # 0 <= x0 <= xmax
        x1 = max(0, min(nx, xmax))    # 0 <= x1 <= xmax
        y0 = min(max(0, ymin), ymax)  # 0 <= y0 <= ymax
        y1 = max(0, min(ny, ymax))    # 0 <= y1 <= ymax
        if x0 >= x1 or y0 >= y1:
            return

        # use float type in order to mask zeros with 0.1 for logscale
        self.curvex.x = self._array[:, int(x0):int(x1)].sum(axis=1,
                                                            dtype=numpy.float)
        self.curvey.y = self._array[int(y0):int(y1), :].sum(axis=0,
                                                            dtype=numpy.float)
        self._applymask()

    def _setData(self, array, nx, ny, nz, newrange):
        LiveWidget._setData(self, array, nx, ny, nz, newrange)
        if newrange:
            self.axesyint.setWindow(0, nx, 0, ny)
            self.axesxint.setWindow(0, nx, 0, ny)
            self.axesxint.ylines = self.axes.ylines
            self.axesyint.xlines = self.axes.xlines
        self.curvey.x = numpy.arange(0, nx)
        self.curvex.y = numpy.arange(0, ny)

    def unzoom(self):
        nx, ny = len(self.curvey.x), len(self.curvex.y)
        self.axesyint.setWindow(0, nx, 1, self.curvey.y.max())
        self.axesxint.setWindow(1, self.curvex.x.max(), 0, ny)
        LiveWidget.unzoom(self)

    def printDialog(self):
        self.gr.printDialog()

    def logscale(self, on):
        LiveWidget.logscale(self, on)
        self.axesxint.setLogX(on)
        self.axesyint.setLogY(on)
        self._applymask()
        self.gr.update()

    def setCenterMark(self, flag):
        self.axesxint.drawxylines = flag
        self.axesyint.drawxylines = flag
        LiveWidget.setCenterMark(self, flag)


class LiveWidget1D(LiveWidgetBase):

    def __init__(self, parent):
        LiveWidgetBase.__init__(self, parent)

        self.plot._lstAxes = []
        self.plot._countAxes = 0
        self.curve = MaskedPlotCurve([0], [.1], linecolor=COLOR_BLUE)
        self.axes = AutoScaleAxes(self, viewport=self.plot.viewport,
                                  xdual=True)
        self.axes.setGrid(True)
        self.axes.addCurves(self.curve)
        self.axes.autoscale = PlotAxes.SCALE_Y
        self.plot.addAxes(self.axes)

    def logscale(self, on):
        LiveWidgetBase.logscale(self, on)
        self.axes.setLogY(on)
        self.curve.filly = .1 if self._logscale else 0
        win = self.axes.getWindow()
        if win:
            win[2] = max(.1, win[2])
            self.axes.setWindow(*win)
        self.gr.update()

    def unzoom(self):
        self.axes.setWindow(-self.axes.xtick,
                            self._axesrange[1] + self.axes.xtick,
                            0, max(1, self.curve.y.max()) + self.axes.ytick)
        self.gr.update()

    def updateAxesRange(self, nx, ny):
        ymin = .1 if self._logscale else 0
        self.axes.setWindow(0, nx, ymin, ny)

    def _setData(self, array, nx, ny, nz, newrange):
        self.curve.x = numpy.arange(0, nx)
        self.curve.y = numpy.ma.masked_equal(self._array.ravel(), 0).astype(
            numpy.float)
        self.curve.filly = .1 if self._logscale else 0
