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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos import session
from nicos.nexus.elements import NexusElementBase

from nicos_sinq.nexus.specialelements import ArrayParam


class CameaAzimuthalAngle(NexusElementBase):
    """
    Store the azimuthal_angle which gets calculated from the
    sample scattering sense
    """
    def __init__(self, name):
        self.name = name
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        if (self.dev, 'scattering_sense') in sinkhandler.dataset.metainfo:
            ss = sinkhandler.dataset.metainfo[
                (self.dev, 'scattering_sense')]
            if ss == 1:
                value = 0.
            else:
                value = 180.
            dset = h5parent.create_dataset(name, (1,), dtype='float32')
            dset[0] = value
            self.createAttributes(dset, sinkhandler)
        else:
            session.log.warning('Failed to write azimuthal_angle, '
                                'device %s not found',
                                self.dev)


class BoundaryArrayParam(ArrayParam):
    """
    This little class handles the reshaping of the boundary array and
    gets rid of accessing the device directly in NexusSink
    """
    def create(self, name, h5parent, sinkhandler):
        if (self.dev, self.parameter) in sinkhandler.dataset.metainfo:
            rawvalue = sinkhandler.dataset.metainfo[
                (self.dev, self.parameter)]
            value = np.array(rawvalue, ([]), self.dtype)
            length = value.size
            value = value.reshape((length/2, 2))
            dset = h5parent.create_dataset(name, value.shape, self.dtype)
            dset[...] = value
            self.createAttributes(dset, sinkhandler)
        else:
            session.log.warning('Failed to write %s, device %s not found',
                                name, self.dev)
