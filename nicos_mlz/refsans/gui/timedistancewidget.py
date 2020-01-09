# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

# pylint:disable=no-name-in-module
from matplotlib.backends.qt_compat import is_pyqt5
from matplotlib.figure import Figure

from nicos.guisupport.qt import QVBoxLayout, QWidget

from nicos_mlz.refsans.lib.timedistancediagram import timedistancediagram

if is_pyqt5():
    # pylint:disable=no-name-in-module
    from matplotlib.backends.backend_qt5agg import FigureCanvas
else:
    # pylint:disable=no-name-in-module
    from matplotlib.backends.backend_qt4agg import FigureCanvas


class TimeDistanceWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure(figsize=(20, 16)))
        self._static_ax = self.canvas.figure.subplots()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, speed, angles, nperiods, disc2_pos, D, Actual_D=None):
        # discards the old graph
        self._static_ax.clear()

        timedistancediagram(speed, angles, n_per=nperiods, D=D,
                            disk2_pos=disc2_pos, plot=self._static_ax,
                            Actual_D=Actual_D)

        # refresh canvas
        self._static_ax.figure.canvas.draw()
