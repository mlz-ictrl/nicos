# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Special Live panel with auto scaling display."""

from nicos.clients.gui.panels.live import LiveDataPanel
from nicos.guisupport.livewidget import IntegralLiveWidget, LiveWidget1D


class AutoScaleLiveWidget1D(LiveWidget1D):

    def __init__(self, parent=None, **kwargs):
        kwargs.update({'xscale': 'decimal'})
        LiveWidget1D.__init__(self, parent, **kwargs)

    def getYMax(self):
        minupperedge = 1
        if self._arrays is not None:
            minupperedge = max(array.max() for array in self._arrays)
            minupperedge *= 2.15 if self._logscale else 1.05
        return minupperedge

    def getYMin(self):
        maxloweredge = 0.09 if self._logscale else 0
        if self._arrays is not None:
            maxloweredge = min(array.min() for array in self._arrays)
            maxloweredge *= 0.5 if self._logscale else 0.95
        return maxloweredge

    def _getNewYRange(self):
        ymax = self.getYMax()
        ymin = self.getYMin()
        return ymin, ymax, ymax


class AutoScaleLiveDataPanel(LiveDataPanel):

    def _initLiveWidget(self, array):
        """Initialize livewidget based on array's shape"""
        if len(array.shape) == 1:
            widgetcls = AutoScaleLiveWidget1D
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)
