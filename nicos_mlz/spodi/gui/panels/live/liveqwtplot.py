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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""SPODI live data plot widget (Qwt version)."""

from nicos.guisupport.qt import Qt, QPen

from PyQt4.Qwt5 import QwtPlotCurve

from nicos.clients.gui.widgets.plotting import NicosQwtPlot


class LiveDataPlot(NicosQwtPlot):

    def __init__(self, parent, window):
        NicosQwtPlot.__init__(self, parent, window)

    def titleString(self):
        return 'Live data'

    def xaxisName(self):
        return 'tths (deg)'

    def yaxisName(self):
        return 'Counts'

    def addAllCurves(self):
        self.curve = QwtPlotCurve('Live spectrum')
        self.curve.setPen(QPen(Qt.black, 1))
        self.curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.curve.attach(self)

    def setCurveData(self, data):
        self.curve.setData(data[0], data[1])
        self.replot()
