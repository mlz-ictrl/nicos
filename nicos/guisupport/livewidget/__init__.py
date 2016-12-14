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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS livewidget with GR."""

import numpy
import numpy.ma

from PyQt4.QtGui import QWidget, QHBoxLayout

import gr
from gr.pygr.base import GRMeta, GRVisibility
from qtgr import InteractiveGRWidget
from gr.pygr import Plot as OrigPlot, PlotAxes, Point, RegionOfInterest, \
    Coords2D, PlotCurve

# from PyQt4.QtCore import QByteArray, Qt, SIGNAL, SLOT
# from PyQt4.QtCore import pyqtSignature as qtsig, QSize

try:
    import pyfits
except ImportError:
    pyfits = None


# the empty string means: no live data is coming, only the filename is important
DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4', ''))

FILETYPES = ('fits',)

COLOR_WHITE = 91
COLOR_BLUE = 4


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


class Data(object):

    def __init__(self, nx, ny, nz, fmt, data):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.fmt = fmt
        self.arr = numpy.frombuffer(data, fmt)

    @classmethod
    def fromfile(cls, filename, filetype=None):
        pass


class GRWidget(InteractiveGRWidget):
    def __init__(self, widget, **kwds):
        InteractiveGRWidget.__init__(self, widget, **kwds)
        self.widget = widget

    def adjustSelectRect(self, p0, p1):
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
    def __init__(self, widget, **kwds):
        PlotAxes.__init__(self, **kwds)
        self.widget = widget


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


class LiveWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._data = None
        self._axesrange = (1, 1)
        self._axesratio = 1.0
        self._logscale = False

        layout = QHBoxLayout()
        self.gr = GRWidget(self)
        layout.addWidget(self.gr)
        self.setLayout(layout)

        self.gr.keepRatio = 0.999
        self.plot = Plot(self, viewport=(.1, .75, .1, .75))
        self.axes = Axes(self, viewport=self.plot.viewport)
        self.plotyint = Plot(self, viewport=(.1, .75, .8, .95))
        self.axesyint = Axes(self, viewport=self.plotyint.viewport,
                             drawX=False, drawY=True)
        self.plotxint = Plot(self, viewport=(.8, .95, .1, .75))
        self.axesxint = Axes(self, viewport=self.plotxint.viewport,
                             drawX=True, drawY=False)

        vp = self.axesxint.viewport
        self._charheight = .024 * (vp[3] - vp[2])

        self.axes.setXtickCallback(self.xtick)
        self.axesxint.setXtickCallback(self.xtick)
        self.axesyint.setYtickCallback(self.yinttick)

        self.axes.setGrid(True)
        self.plot.addAxes(self.axes)
        self.plotyint.addAxes(self.axesyint)
        self.plotxint.addAxes(self.axesxint)
        self.surf = Cellarray([0], [0], [0],
                                        option=gr.OPTION_CELL_ARRAY)
        self.curvey = PlotCurve([0], [0], linecolor=COLOR_BLUE)
        self.curvex = PlotCurve([0], [0], linecolor=COLOR_BLUE)

        self._rois = {}
        self.axes.addCurves(self.surf)
        self.axesyint.addCurves(self.curvey)
        self.axesxint.addCurves(self.curvex)
        self.gr.addPlot(self.plot)
        self.gr.addPlot(self.plotyint)
        self.gr.addPlot(self.plotxint)

    def xtick(self, x, y, svalue, _value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        gr.text(x, y, svalue)

    def yinttick(self, x, y, svalue, _value):
        gr.setcharheight(self._charheight)
        gr.text(x, y, svalue)

    def _rescale(self):
        """Rescales integral plots in respect to the main/cellarray plot."""
        xmin, xmax, ymin, ymax = self.axes.getWindow()
        _, _, y0, y1 = self.axesyint.getWindow()
        x0, x1, _, _ = self.axesxint.getWindow()
        self.axesyint.setWindow(xmin - .5, xmax - .5, y0, y1)
        self.axesxint.setWindow(x0, x1, ymin - .5, ymax - .5)
        self.gr.update()

    def zoom(self, master, dpercent, p0):
        if self.plot == master:
            w, h = self.width(), self.height()
            self.plot.zoom(dpercent, p0, w, h)
            self._rescale()

    def select(self, master, p0, p1):
        if self.plot == master:
            w, h = self.width(), self.height()
            self.plot.select(p0, p1, w, h)
            self._rescale()

    def pan(self, p0, dp):
        w, h = self.width(), self.height()
        self.plot.pan(dp, w, h)
        self._rescale()

    def _updateZData(self):
        if self._logscale:
            arr = numpy.ma.log10(self._data.arr).filled(0)
        else:
            arr = self._data.arr
        amax = arr.max()
        if amax > 0:
            arr = 255 * arr / amax
        self.surf.z = 1000 + arr

    def setData(self, data):
        self._data = data
        self._axesratio = data.ny / float(data.nx)
        if (data.nx, data.ny) != self._axesrange:
            self.axes.setWindow(0, data.nx, 0, data.ny)
            self.axesyint.setWindow(0, data.nx, 1, data.ny)
            self.axesxint.setWindow(1, data.nx, 0, data.ny)
            #self.plot.viewport = (.1, .95, .1, .1 + .85 * self._axesratio)
            #self.axes.xtick = self.axes.ytick = 4
            #self.axes.majorx = self.axes.majory = 4
        self._axesrange = (data.nx, data.ny)
        self.surf.x = numpy.linspace(0, data.nx, data.nx)
        self.surf.y = numpy.linspace(0, data.ny, data.ny)
        self._updateZData()
        arr2d = data.arr.reshape((data.ny, data.nx))
        self.curvey.x = numpy.arange(0, data.nx)
        self.curvey.y = arr2d.sum(axis=0)
        self.curvex.y = numpy.arange(0, data.ny)
        self.curvex.x = arr2d.sum(axis=1)
        self.axesyint.setWindow(0, data.nx, 1, self.curvey.y.max())
        self.axesxint.setWindow(1, self.curvex.x.max(), 0, data.ny)
        self._rescale()

    def getColormap(self):
        return self.surf.colormap

    def setColormap(self, colormap):
        self.surf.colormap = colormap
        self.gr.update()

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
        self.axes.setWindow(0, self._axesrange[0],
                            0, self._axesrange[1])
        nx, ny = len(self.curvey.x), len(self.curvex.y)
        self.axesyint.setWindow(0, nx, 1, self.curvey.y.max())
        self.axesxint.setWindow(1, self.curvex.x.max(), 0, ny)
        self._rescale()

    def printDialog(self):
        self.gr.printDialog()

    def logscale(self, on):
        self._logscale = on
        self.axesxint.setLogX(on)
        self.axesyint.setLogY(on)
        self._updateZData()
        self.gr.update()
