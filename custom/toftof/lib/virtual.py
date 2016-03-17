#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual devices for testing."""

from nicos.core import Override, Param
from nicos.devices.generic.virtual import VirtualImage as BaseImage

import numpy as np


class VirtualImage(BaseImage):
    """A virtual 2-dimensional detector that generates TOFTOF data from real
    measured data weighted by time.
    """

    parameters = {
        'datafile': Param('File to load the pixel data',
                          settable=False,
                          type=str,
                          default='custom/toftof/data/test/data.npz',
                          ),
    }

    parameter_overrides = {
        'sizes': Override(default=(1024, 1024), prefercache=False),
    }

    _rawdata = None

    def doInit(self, mode):
        BaseImage.doInit(self, mode)
        with open(self.datafile, 'rb') as fp:
            self._rawdata = 0.01 * np.load(fp)

    def _generate(self, t):
        return np.random.poisson(t * self._rawdata).reshape(self.sizes)
