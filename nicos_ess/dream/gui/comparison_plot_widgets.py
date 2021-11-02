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
#   Ebad Kamil <ebad.kamil@ess.eu>
#
# *****************************************************************************

import numpy as np

from nicos.guisupport.livewidget import IntegralLiveWidget
from nicos.guisupport.plots import MaskedPlotCurve
from nicos.guisupport.qt import QLabel, QSizePolicy, Qt, QVBoxLayout, QWidget

from nicos_mlz.toftof.gui.resolutionpanel import COLOR_GREEN, PlotWidget


class PlotWidget1D(PlotWidget):
    def setData(self, x1, y1, x2=None, y2=None, difference=False):
        """
        Widget has 3 MaskedPlotCurves. The first two curves are used to plot
        y1 and y2 and the last curve to plot the difference y1 - y2.
        """
        for curve, (x, y) in zip(self.plot._curves[:-1], ((x1, y1), (x2, y2))):
            if y is not None:
                curve.x = np.array(x)
                curve.y = np.array(y)
        if difference:
            self.plot._curves[-1].x = np.array(x1)
            self.plot._curves[-1].y = np.array(y1) - np.array(y2)
        else:
            self.plot._curves[-1].x = np.array([0])
            self.plot._curves[-1].y = np.array([0])
        self._plot_reset()

    def reset_reference(self):
        for curve in self.plot._curves[1:]:
            curve.x = np.array([0])
            curve.y = np.array([0])
        self._plot_reset()

    def _plot_reset(self):
        self.plot.reset()
        self.plot.update()


class ComparisonPlot1D(PlotWidget1D):
    def __init__(self, title, x_label, y_label, n_curves, parent=None):
        PlotWidget1D.__init__(self, title, x_label, y_label, n_curves, parent=parent)
        curve = MaskedPlotCurve(
            [0], [1], linewidth=2, legend='Difference', linecolor=COLOR_GREEN
        )
        self.plot.axes.addCurves(curve)
        self.plot._curves.append(curve)
        self.plot._curves[0].legend = 'Current'
        self.plot._curves[1].legend = 'Reference'


class ComparisonPlot2D(QWidget):
    def __init__(self, title, parent=None):
        QWidget.__init__(self, parent)
        parent.setLayout(QVBoxLayout())
        self.plot = IntegralLiveWidget(self)
        titleLabel = QLabel(title)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet('QLabel {font-weight: 600}')
        parent.layout().insertWidget(0, titleLabel)
        self.plot.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )
        parent.layout().insertWidget(1, self.plot)

    def setData(self, array, labels=None):
        self.plot.setData([array], labels=labels)
