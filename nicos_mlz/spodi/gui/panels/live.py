#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.clients.gui.panels.livegr import LiveDataPanel as BaseLiveDataPanel
from nicos.guisupport.livewidget import LiveWidget1D

import numpy


class FullScreen1DWidget(LiveWidget1D):

    client = None

    def __init__(self, parent):
        LiveWidget1D.__init__(self, parent)
        self.plot.viewport = [0.05, .98, 0.1, .98]
        self.plot.xlabel = 'tths (deg)'
        self.plot.ylabel = 'counts'

    def setData(self, array):
        self._array = array
        nz, ny, nx = 1, 1, 1
        newrange = False

        n = len(array.shape)
        if n == 1:
            start, end, step = self._calcStartEndStep(array.shape[0])
            self.curve.x = numpy.arange(start, end, step)
            nx = end
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
        self.curve.y = numpy.ma.masked_equal(self._array.ravel(), 0).astype(
            numpy.float)
        self.curve.filly = .1 if self._logscale else 0

    def _calcStartEndStep(self, nx):
        """Calculate start, end, and step value for the x axis.

        The start and end values are calculated from the detector start value,
        number of resosteps and the detector range.
        """
        startp, steps, rg = self.client.eval('adet._startpos, adet.resosteps, '
                                             'adet.range', None)
        # The orientation of the tths is in negative direction but
        # it will be used in positive direction to avoid type the '-'
        # for each position in the frontend
        step = rg / steps
        start = -(startp - (rg - step))
        return start, start + nx * step, step

    def updateAxesRange(self, nx, ny):
        self.axes.setWindow(self.curve.x[0], self.curve.x[-1],
                            .1 if self._logscale else 0, ny)

    def unzoom(self):
        self.updateAxesRange(self._axesrange[1], self._axesrange[0])
        self.rescale()


class LiveDataPanel(BaseLiveDataPanel):

    def initLiveWidget(self, widgetcls):
        if widgetcls == LiveWidget1D:
            widgetcls = FullScreen1DWidget
        BaseLiveDataPanel.initLiveWidget(self, widgetcls)
        if widgetcls == FullScreen1DWidget:
            self.widget.client = self.client
