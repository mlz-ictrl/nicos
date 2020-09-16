#  -*- coding: utf-8 -*-
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

""" Extend the array description and support additional data for histograms
"""

from nicos.core import ArrayDesc
from nicos.core.errors import ConfigurationError


class HistogramDimDesc:
    """Class to describe metadata one dimension in histogram
    """

    def __init__(self, length, label='', unit='', bins=None):
        self.length = length
        self.label = label
        self.unit = unit
        self.bins = bins if bins else []


class HistogramDesc(ArrayDesc):
    """Describes the metadata of a histogram.
    """

    def __init__(self, name, dtype, dims):
        shape = []
        dimnames = []
        dimunits = []
        dimbins = []
        for dim in dims:
            if not isinstance(dim, HistogramDimDesc):
                raise ConfigurationError('%s should be of type '
                                         'HistogramDimDesc' % dim)
            shape.append(dim.length)
            dimnames.append(dim.label)
            dimunits.append(dim.unit)
            dimbins.append(dim.bins)
        ArrayDesc.__init__(self, name, shape, dtype, dimnames)
        self.dimunits = dimunits
        self.dimbins = dimbins
        self.dimbins = dimbins
