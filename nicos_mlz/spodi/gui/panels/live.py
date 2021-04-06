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

from nicos.clients.gui.panels.live import LiveDataPanel as BaseLiveDataPanel
from nicos.guisupport.livewidget import LiveWidget1D


class FullScreen1DWidget(LiveWidget1D):

    client = None

    def __init__(self, parent):
        LiveWidget1D.__init__(self, parent)
        self.plot.viewport = [0.05, .98, 0.1, .98]
        self.axes.xdual = False
        self.axes.xtick = 5
        self.axes.majorx = 10
        self.axes.ticksize = 0.005
        self.gr.update()
        self._zoomed = False

    def _adjustXAxisRange(self):
        if not self._zoomed:
            LiveWidget1D._adjustXAxisRange(self)

    def _adjustYAxisRange(self):
        if not self._zoomed:
            LiveWidget1D._adjustYAxisRange(self)

    def unzoom(self):
        labels = self._labels['x']
        self._axesrange['x'] = labels[0], labels[-1]
        self._axesrange['y'] = (0.1 if self._logscale else 0,
                                max(1, self.getYMax()))
        self._zoomed = False
        LiveWidget1D.unzoom(self)

    def zoom(self, master, dpercent, p0):
        LiveWidget1D.zoom(self, master, dpercent, p0)
        if self.plot == master:
            self._zoomed = True
            self._axesrange['x'] = self.axes.getWindow()[:2]
            self._axesrange['y'] = self.axes.getWindow()[2:]

    def select(self, master, p0, p1):
        LiveWidget1D.select(self, master, p0, p1)
        if self.plot == master:
            self._zoomed = True
            self._axesrange['x'] = self.axes.getWindow()[:2]
            self._axesrange['y'] = self.axes.getWindow()[2:]

    def getYMax(self):
        minupperedge = 1
        if self._arrays is not None:
            minupperedge = max([array.max() for array in self._arrays])
            minupperedge *= 2.15 if self._logscale else 1.05
        return minupperedge


class LiveDataPanel(BaseLiveDataPanel):

    def initLiveWidget(self, widgetcls):
        if widgetcls == LiveWidget1D:
            widgetcls = FullScreen1DWidget
        BaseLiveDataPanel.initLiveWidget(self, widgetcls)
        if widgetcls == FullScreen1DWidget:
            self.widget.client = self.client
