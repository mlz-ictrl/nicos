#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
"""SPODI live data plot widget (GR version)."""

from nicos.clients.gui.widgets.plotting import NicosGrPlot, NicosPlotCurve
from nicos.clients.gui.widgets.grplotting import NicosPlotAxes


class LivePlotAxes(NicosPlotAxes):

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
        return NicosPlotAxes.doAutoScale(self, curvechanged)


class LiveDataPlot(NicosGrPlot):

    axescls = LivePlotAxes

    def __init__(self, parent, window):
        NicosGrPlot.__init__(self, parent, window)
        self.setAutoScaleFlags(True, True)
        self.setSymbols(False)

    def titleString(self):
        return 'Live data'

    def xaxisName(self):
        return 'tths (deg)'

    def yaxisName(self):
        return 'Counts'

    def addAllCurves(self):
        self.curve = NicosPlotCurve([], [])
        self.curve.legend = 'Live spectrum'

    def setCurveData(self, data):
        self.curve.x = data[0]
        self.curve.y = data[1]
        # self.curve.legend = ''
        self.addPlotCurve(self.curve)
