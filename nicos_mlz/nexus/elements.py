# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""Some convenience classes for NeXus data writing."""

import numpy as np

from nicos.core.params import tupleof
from nicos.nexus.elements import DeviceDataset, NexusElementBase
from nicos_mlz.nexus.structures import nounit


class ScanDeviceDataset(DeviceDataset):
    """Place holder a device which has a value for each scan point."""

    def testAppend(self, sinkhandler):
        NexusElementBase.testAppend(self, sinkhandler)


class Reflection(NexusElementBase):
    """Place holder for reflection of single crystal, stored as an array.

    The sample should be `nicos.devices.tas.Cell` or
    `nicos.devices.sxtal.SXTalSample`.
    """
    def __init__(self, device, parameter='reflection', defaultval=(1, 1, 1)):
        self.attrs = {}
        NexusElementBase.__init__(self)
        self.device = device
        self.parameter = parameter
        self.defaultval = tupleof(int, int, int)(defaultval)
        self.attrs['units'] = nounit

    def create(self, name, h5parent, sinkhandler):
        if (self.device, self.parameter) in sinkhandler.dataset.metainfo:
            value = \
                sinkhandler.dataset.metainfo[(self.device, self.parameter)][0]
        else:
            value = self.defaultval

        dset = h5parent.create_dataset(name, (3,), maxshape=(3,),
                                       dtype='int')
        dset[...] = np.array(value)
        self.createAttributes(dset, sinkhandler)
