#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

import gr
import numpy
import numpy.ma
from gr.pygr import Coords2D, Coords2DList, Plot as OrigPlot, PlotAxes, \
    Point, RegionOfInterest
from gr.pygr.base import GRMeta, GRVisibility

from nicos.core import UsageError
from nicos.guisupport.plots import GRCOLORS, GRMARKS, MaskedPlotCurve
from nicos.guisupport.qt import QHBoxLayout, QWidget, pyqtSignal
from nicos.guisupport.qtgr import InteractiveGRWidget
from nicos.guisupport.utils import savePlot

DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       '<u1', '<i1', '>u1', '>i1', '<f8', '<f4', '>f8', '>f4',
                       '<u8', '<i8', '>u8', '>i8'))

COLOR_MAXINTENSITY = 1255

AXES = ['x', 'y']


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
            gr.cellarray(self.x[0], self.x[-1], self.y[-1], self.y[0],
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

    def resetPlot(self):
        self._lstAxes = []
        self._countAxes = 0


class Axes(PlotAxes):
    def __init__(self, widget, xdual=False, ydual=False, **kwds):
        PlotAxes.__init__(self, **kwds)
        self.widget = widget
        self.xdual, self.ydual = xdual, ydual

        self.drawxylines = False
        self.xlines = []  # draw vertical lines at x-coordinates
        self.ylines = []  # draw horizontal lines at y-coordinates
        self.xylinecolor = GRCOLORS['magenta']

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
            return 2 ** (int(math.log(max(amax - amin, 0.1), 2)) - 4)
        if self.xdual:
            self.xtick = tick(xmin, xmax)
            self.majorx = 4
        if self.ydual:
            self.ytick = tick(ymin, ymax)
            self.majory = 4
        return res

    def drawGR(self):
        lwidth = gr.inqlinewidth()
        gr.setlinewidth(0.)
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
        gr.setlinewidth(lwidth)

    def resetCurves(self):
        self._curves = Coords2DList()
        self._visibleCurves = Coords2DList()


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
            gr.setlinecolorind(GRCOLORS['white'])
            gr.polyline(self.x, self.y)
            gr.setlinecolorind(color)


class LiveWidgetBase(QWidget):

    closed = pyqtSignal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._arrays = None
        self._plotcount = 1
        # self._axesrange = (1, 1)  # y, x (rows, cols)
        self._axesrange = {
            'x': (0, 1, 2),
            'y': (0, 1, 2)
        }
        self._fixedsize = False
        self._axesratio = 1.0
        self._logscale = False
        self._rois = {}
        self._saveName = None

        layout = QHBoxLayout()
        self.gr = GRWidget(self)
        layout.addWidget(self.gr)
        self.setLayout(layout)

        self.plot = Plot(self, viewport=(0.1, 0.95, 0.1, 0.95))
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
            if (self._arrays is not None and plot == self.plot and
               len(self._arrays[0].shape) == 2):
                # TODO: adapt this for ``shape > 2`` once available.
                x, y = int(pWC.x), int(pWC.y)
                if self._labels['x'][0] <= x < self._labels['x'][-1] and \
                        self._labels['y'][0] <= y < self._labels['y'][-1]:
                    return x, y, self._arrays[0][y+1, x+1]
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

    def updateAxesRange(self):
        """This method will be called whenever the shape of the incoming data
        has been changed. Overwrite this method e.g. to rescale the axes."""
        self.axes.setWindow(self._axesrange['x'][0],
                            self._axesrange['x'][1],
                            self._axesrange['y'][0],
                            self._axesrange['y'][1])

    def setData(self, arrays, labels=None):
        self._arrays = arrays
        self._labels = labels
        # ensure we have labels
        if self._labels is None:
            self._labels = {}
        if not self._labels:
            self._generateDefaultLabels()

        self._prepareSetData()

        newrange = False

        if not self._fixedsize:
            xlen = self._labels['x'][-1] - self._labels['x'][0]
            self.axes.xlines = [self._labels['x'][0] + xlen / 2]

            if 'y' in self._labels:
                ylen = self._labels['y'][-1] - self._labels['y'][0]
                self.axes.ylines = [self._labels['y'][0] + ylen / 2]
            else:
                ylen = 1
                self.axes.ylines = [0.5]

            try:
                self._axesratio = ylen / float(xlen)
            except ZeroDivisionError:
                return

            newx = self.setAxisRange(self._getNewXRange(), 'x')
            newy = self.setAxisRange(self._getNewYRange(), 'y')

            if newx or newy:
                self.updateAxesRange()
                newrange = True

        self._finishSetData(newrange)

        self.updateZData()

        self.rescale()

    def _generateDefaultLabels(self):
        reference = self._arrays[0].shape

        for axis, entry in zip(AXES, reversed(reference)):
            self._labels[axis] = numpy.arange(entry)

    def _prepareSetData(self):
        """Hook at the start of setData"""

    def _finishSetData(self, newrange):
        """Hook at the end of setData"""

    def _adjustView(self):
        """Hook for adjustments of the """

    def setAxisRange(self, newrange, axis):
        try:
            if newrange == self._axesrange[axis]:
                return False
            else:
                self._axesrange[axis] = newrange
                return True
        except KeyError:
            raise UsageError('No %s axis to set') from None

    def _getNewXRange(self):
        return (self._labels['x'][0], self._labels['x'][-1],
                len(self._labels['x']))

    def _getNewYRange(self):
        if 'y' in self._labels:
            return (self._labels['y'][0], self._labels['y'][-1],
                    len(self._labels['y']))
        return (0, 1, 2)

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
        self.axes.setWindow(*(self._axesrange['x'][:2] +
                              self._axesrange['y'][:2]))
        self.rescale()

    def printDialog(self):
        self.gr.printDialog()

    def logscale(self, on):
        self._logscale = on
        if self._arrays is not None:
            self.updateZData()
            self.gr.update()

    def setCenterMark(self, flag):
        self.axes.drawxylines = flag
        self.gr.update()

    def savePlot(self):
        self._saveName = savePlot(self.gr, gr.PRINT_TYPE[gr.PRINT_PDF],
                                  self._saveName)
        return self._saveName

    def setTitles(self, titles):
        if titles is None:
            return
        for axis, title in titles.items():
            if axis in AXES:
                if axis == 'x':
                    self.plot.xlabel = title
                elif axis == 'y':
                    self.plot.ylabel = title


class LiveWidget(LiveWidgetBase):

    def __init__(self, parent):
        LiveWidgetBase.__init__(self, parent)

        self.axes.setGrid(False)
        self.axes.xylinecolor = COLOR_MAXINTENSITY
        self.surf = Cellarray([0], [0], [0], option=gr.OPTION_CELL_ARRAY)
        self.axes.addCurves(self.surf)

    def updateZData(self):
        arr = self._arrays[0].ravel()
        if self._logscale:
            arr = numpy.ma.log10(arr).filled(-1)
        # TODO: implement 'sliders' for amin, amax
        amin, amax = arr.min(), arr.max()

        if amin != amax:
            self.surf.z = 1000 + 255 / (amax - amin) * (arr - amin)
        elif amax > 0:
            self.surf.z = 1000 + 255 / amax * arr
        else:
            self.surf.z = 1000 + arr

    def _finishSetData(self, newrange):
        self.surf.x = numpy.linspace(*self._axesrange['x'])
        self.surf.y = numpy.linspace(*self._axesrange['y'])

    def getColormap(self):
        return self.surf.colormap

    def setColormap(self, colormap):
        self.surf.colormap = colormap
        self.gr.update()


class IntegralLiveWidget(LiveWidget):

    def __init__(self, parent):
        LiveWidget.__init__(self, parent)

        self.plot.viewport = (0.1, 0.75, 0.1, 0.75)
        self.axes.viewport = self.plot.viewport
        self.plotyint = Plot(self, viewport=(0.1, 0.75, 0.8, 0.95))
        self.axesyint = Axes(self, viewport=self.plotyint.viewport,
                             drawX=False, drawY=True, xdual=True)
        self.plotxint = Plot(self, viewport=(0.8, 0.95, 0.1, 0.75))
        self.axesxint = Axes(self, viewport=self.plotxint.viewport,
                             drawX=True, drawY=False, ydual=True)

        vp = self.axesxint.viewport
        self._charheight = 0.024 * (vp[3] - vp[2])

        self.axes.setXtickCallback(self.xtick)
        self.axesxint.setXtickCallback(self.xtick)
        self.axesyint.setYtickCallback(self.yinttick)

        self.plotyint.addAxes(self.axesyint)
        self.plotxint.addAxes(self.axesxint)
        self.curvey = MaskedPlotCurve([0], [0], filly=0.1,
                                      linecolor=GRCOLORS['blue'])
        self.curvex = MaskedPlotCurve([0], [0], fillx=0.1,
                                      linecolor=GRCOLORS['blue'])

        self.axesyint.addCurves(self.curvey)
        self.axesxint.addCurves(self.curvex)
        self.gr.addPlot(self.plotyint)
        self.gr.addPlot(self.plotxint)

    def xtick(self, x, y, svalue, _value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        # We want to pass through the string value, but we are passed a bytes
        # object by the C layer and gr.text() needs a string.  Since it is
        # encoded using latin1 again, this is the right encoding to use here.
        gr.text(x, y, svalue.decode('latin1'))

    def yinttick(self, x, y, svalue, _value):
        gr.setcharheight(self._charheight)
        gr.text(x, y, svalue.decode('latin1'))

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
            x0, y0 = 0.1, 0.1
            self.curvex.x = numpy.ma.masked_equal(self.curvex.x, 0)
            self.curvey.y = numpy.ma.masked_equal(self.curvey.y, 0)
        else:  # unmask if masked if not logscale
            x0, y0 = 0, 0
            if numpy.ma.is_masked(self.curvex._x):
                self.curvex.x = self.curvex._x.filled(0)
            if numpy.ma.is_masked(self.curvey._y):
                self.curvey.y = self.curvey._y.filled(0)
        # rescale axes
        self.axesyint.setWindow(xmin - 0.5, xmax - 0.5,
                                y0, self.curvey.y.max())
        self.axesxint.setWindow(x0, self.curvex.x.max(),
                                ymin - 0.5, ymax - 0.5)

    def getLabelIndices(self, axis, minimum, maximum):
        try:
            labels = self._labels[axis]
        except KeyError:
            raise UsageError('No labels for %d' % axis) from None

        if minimum < labels[0]:
            imin = 0
        elif minimum > labels[-1]:
            imin = len(labels) - 1
        else:
            imin = None

        if maximum < labels[0]:
            imax = 0
        elif maximum > labels[-1]:
            imax = len(labels) - 1
        else:
            imax = None

        if imax is None or imin is None:
            for i, label in enumerate(labels):
                if imin is None:
                    if label == minimum:
                        imin = i
                    if label > minimum:
                        imin = max(i - 1, 0)
                if imax is None:
                    if label == maximum:
                        imax = i
                    if label > maximum:
                        imax = i - 1

        return imin, imax

    def _rescale(self):
        """Rescales integral plots in respect to the main/cellarray plot."""

        # get indices for current window
        xmin, xmax, ymin, ymax = self.axes.getWindow()

        ixmin, ixmax = self.getLabelIndices('x', xmin, xmax)
        iymin, iymax = self.getLabelIndices('y', ymin, ymax)

        reference = self._arrays[0]
        ny, nx = reference.shape

        # find the indices of the relevant values
        x0 = self._labels['x'][min(max(0, ixmin), ixmax)]  # 0 <= x0 <= ixmax
        x1 = self._labels['x'][max(0, min(nx, ixmax))]     # 0 <= x1 <= ixmax
        y0 = self._labels['y'][min(max(0, iymin), iymax)]  # 0 <= y0 <= iymax
        y1 = self._labels['y'][max(0, min(ny, iymax))]     # 0 <= y1 <= iymax

        if x0 > x1 or y0 > y1:
            return

        # use float type in order to mask zeros with 0.1 for logscale
        self.curvex.x = reference[:, int(x0):int(x1)].sum(
            axis=1, dtype=numpy.float)
        self.curvey.y = reference[int(y0):int(y1), :].sum(
            axis=0, dtype=numpy.float)
        self._applymask()

    def _finishSetData(self, newrange):
        LiveWidget._finishSetData(self, newrange)

        nx = self._axesrange['x']
        ny = self._axesrange['y']

        if newrange:
            self.axesyint.setWindow(nx[0], nx[1], ny[0], ny[1])
            self.axesxint.setWindow(nx[0], nx[1], ny[0], ny[1])
            self.axesxint.ylines = self.axes.ylines
            self.axesyint.xlines = self.axes.xlines
        self.curvey.x = numpy.linspace(nx[0], nx[1], nx[2])
        self.curvex.y = numpy.linspace(ny[0], ny[1], ny[2])

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

        self.plot.resetPlot()
        self._curves = [MaskedPlotCurve([0], [1], linecolor=GRCOLORS['blue'])]
        self.axes = AutoScaleAxes(self, viewport=self.plot.viewport,
                                  xdual=True)
        self.axes.setGrid(True)
        self.axes.addCurves(self._curves[0])
        self.axes.autoscale = PlotAxes.SCALE_Y
        self.plot.addAxes(self.axes)
        # self._axesrange = dict(x=(1, 1), y=(1, 1), z=(1, 1))
        self.setSymbols(False)
        self.setLines(False)
        self.setMarks(['omark'])
        self._labels = None
        self._markersize = 1.0

    def getYMax(self):
        if self._arrays is None:
            return

        ny = self.axes.getWindow()[3]

        # leave a visually equal padding on top for logscale and normal view
        minupperedge = max([max(array) for array in self._arrays])

        if self._logscale:
            return max(ny, minupperedge * 2.15)

        return max(ny, minupperedge * 1.05)

    def setPlotCount(self, count, colors):
        self.axes.resetCurves()
        self.plot.resetPlot()

        self._curves = []

        for i in range(count):
            color = GRCOLORS.get(colors[i], GRCOLORS['blue'])
            curve = MaskedPlotCurve([0], [.1], linecolor=color)
            curve.markercolor = color
            curve.markersize = self._markersize
            self._curves.append(curve)
            self.axes.addCurves(curve)

        self.axes.autoscale = PlotAxes.SCALE_Y
        self.plot.addAxes(self.axes)

        self.setLines(self.hasLines)
        self.setSymbols(self.hasSymbols)

    def logscale(self, on):
        LiveWidgetBase.logscale(self, on)
        self.axes.setLogY(on)
        newmin = 0.1 if on else 0
        oldmin = 0.1 if not on else 0
        for curve in self._curves:
            curve.filly = newmin
        win = self.axes.getWindow()
        if win:
            if win[2] == oldmin:  # seems not to be zoomed in
                win[2] = newmin
            else:
                win[2] = max(newmin, win[2])
            self.axes.setWindow(*win)
        self.update()

    def setSymbols(self, on):
        markertype = self._marktype if on else GRMARKS['dot']
        for axis in self.plot.getAxes():
            for curve in axis.getCurves():
                curve.markertype = markertype
        self.hasSymbols = on
        self.update()

    def setLines(self, on):
        linetype = None
        if on:
            linetype = gr.LINETYPE_SOLID
        for axis in self.plot.getAxes():
            for curve in axis.getCurves():
                curve.linetype = linetype
        self.hasLines = on
        self.update()

    def setMarks(self, marktype):
        if isinstance(marktype, list):
            self._marktype = GRMARKS.get(marktype[0] if marktype else 'omark',
                                         GRMARKS['omark'])
        else:
            self._marktype = GRMARKS.get(marktype, GRMARKS['omark'])

    def setMarkerSize(self, size):
        self._markersize = size
        for curve in self._curves:
            curve.markersize = size

    def changeMarkerSize(self, size):
        gr.setmarkersize(size)

    def getMinX(self):
        pass

    def getMaxX(self):
        pass

    def unzoom(self):
        # set the window we want to see
        self.axes.setWindow(self._axesrange['x'][0], self._axesrange['x'][1],
                            self._axesrange['y'][0], self._axesrange['y'][1])

        # add some padding in x range.
        # 2nd call to avoid copy paste of the xtick function in pygr.
        window = self.axes.getWindow()
        self.axes.setWindow(self._axesrange['x'][0] - self.axes.xtick,
                            self._axesrange['x'][1] + self.axes.xtick,
                            window[2], window[3])
        self.gr.update()

    def _prepareSetData(self):
        for curve, arr in zip(self._curves, self._arrays):
            curve.y = numpy.ma.masked_equal(arr.ravel(), 0).astype(
                numpy.float)
            curve.filly = 0.1 if self._logscale else 0
            curve.x = self._labels['x']

    def _getNewYRange(self):
        ymax = self.getYMax()
        return 0.09 if self._logscale else 0, ymax, ymax
