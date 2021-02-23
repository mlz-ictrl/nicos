#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2021 by the NICOS contributors (see AUTHORS)
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

import numpy

from nicos.clients.gui.panels.live import LiveDataPanel as BaseLiveDataPanel
from nicos.guisupport.livewidget import LiveWidget1D


class FullScreen1DWidget(LiveWidget1D):

    client = None

    def __init__(self, parent):
        LiveWidget1D.__init__(self, parent)
        self.plot.viewport = [0.05, .98, 0.1, .98]
        self.plot.xlabel = 'tths (deg)'
        self.plot.ylabel = 'counts'
        self.axes.xdual = False
        self.axes.xtick = 5
        self.axes.majorx = 10
        self.axes.ticksize = 0.005
        self.curve.x = numpy.arange(0, 2, 1)
        self.gr.update()
        self._zoomed = False

    def _setData(self, array, nx, ny, nz, newrange):
        self.curve.x = numpy.arange(*self._calcStartEndStep(array.shape[0]))
        self.curve.y = numpy.ma.masked_equal(array.ravel(), 0).astype(
            numpy.float)
        self.curve.filly = .1 if self._logscale else 0

        if not self._zoomed:
            self.axes.setWindow(self.curve.x[0], self.curve.x[-1],
                                .1 if self._logscale else 0,
                                max(self.curve.y))

    def _calcStartEndStep(self, nx):
        """Calculate start, end, and step value for the x axis.

        The start and end values are calculated from the detector start value,
        number of resosteps and the detector range.
        """
        startp, steps, rg = self.client.eval('adet._startpos, adet.resosteps, '
                                             'adet.range', None)
        # The orientation of the tths is in negative direction but it will be
        # used in positive direction to avoid type the '-' for each position in
        # the frontend
        step = rg / steps
        start = -(startp - (rg - step))
        return start, start + nx * step, step

    def unzoom(self):
        self.axes.setWindow(self.curve.x[0], self.curve.x[-1],
                            0.1 if self._logscale else 0,
                            max(1, self.getYMax()))
        self._zoomed = False
        self.gr.update()

    def zoom(self, master, dpercent, p0):
        if self.plot == master:
            self._zoomed = True
        LiveWidget1D.zoom(self, master, dpercent, p0)

    def select(self, master, p0, p1):
        if self.plot == master:
            self._zoomed = True
        LiveWidget1D.select(self, master, p0, p1)


class LiveDataPanel(BaseLiveDataPanel):

    def initLiveWidget(self, widgetcls):
        if widgetcls == LiveWidget1D:
            widgetcls = FullScreen1DWidget
        BaseLiveDataPanel.initLiveWidget(self, widgetcls)
        if widgetcls == FullScreen1DWidget:
            self.widget.client = self.client
