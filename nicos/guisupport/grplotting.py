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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import numpy.ma
from gr.pygr import PlotCurve


class MaskedPlotCurve(PlotCurve):

    def __init__(self, *args, **kwargs):
        # fill values for masked x, y
        self.fillx = kwargs.pop("fillx", 0)
        self.filly = kwargs.pop("filly", 0)
        PlotCurve.__init__(self, *args, **kwargs)

    @property
    def x(self):
        x = PlotCurve.x.__get__(self)
        if numpy.ma.is_masked(x):
            return x.filled(self.fillx)
        return x

    @x.setter
    def x(self, x):
        PlotCurve.x.__set__(self, x)

    @property
    def y(self):
        y = PlotCurve.y.__get__(self)
        if numpy.ma.is_masked(y):
            return y.filled(self.filly)
        return y

    @y.setter
    def y(self, y):
        PlotCurve.y.__set__(self, y)
