#  -*- coding: utf-8 -*-
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
#   Mark Koennecke <Mark.Koennecke@psi.ch>
#
# *****************************************************************************

import numpy

from nicos import nicos_version, session
from nicos.devices.sxtal.sample import SXTalSample
from nicos.devices.tas import Cell

from .elements import ConstDataset, NexusElementBase, NXAttribute


class NicosProgramDataset(ConstDataset):
    """Place holder for the NICOS program info.

    This elememt can be used for the `program_name` entry in the NXentry group.
    """
    def __init__(self):
        ConstDataset.__init__(self, 'NICOS', 'string',
                              version=NXAttribute(nicos_version, 'string'),
                              configuration=NXAttribute(
                                  session.explicit_setups, 'string'))


class CellArray(NexusElementBase):
    """Place holder for sample cell parameters, stored as an array.

    The sample should be `nicos.devices.tas.Cell` or
    `nicos.devices.sxtal.SXTalSample`.
    """
    def __init__(self):
        self.attrs = {}
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        sample = session.experiment.sample
        if isinstance(sample, Cell):
            data = sample.lattice + sample.angles
        elif isinstance(sample, SXTalSample):
            data = [sample.a, sample.b, sample.c,
                    sample.alpha, sample.beta, sample.gamma]
        else:
            session.log.error('Your sample is no Cell and no SXTalSample')
            return
        self.attrs['units'] = NXAttribute('', 'string')
        ds = h5parent.create_dataset(name, (6,), maxshape=(None,),
                                     dtype='float64')
        ds[...] = numpy.array(data)
        self.createAttributes(ds, sinkhandler)


class UBMatrix(NexusElementBase):
    """Place holder for the UB matrix of the sample cell or SXTalSample.

    The sample should be `nicos.devices.tas.Cell` or
    `nicos.devices.sxtal.SXTalSample`.
    """
    def __init__(self):
        self.attrs = {}
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        sample = session.experiment.sample
        if isinstance(sample, Cell):
            data = sample.matrix_crystal2lab().flatten()
        elif isinstance(sample, SXTalSample):
            data = numpy.array(sample.ubmatrix, dtype='float64').flatten()
        else:
            session.log.error('Your sample is no Cell and no SXTalSample')
            return
        self.attrs['units'] = NXAttribute('', 'string')
        ds = h5parent.create_dataset(name, (9,), maxshape=(None,),
                                     dtype='float64')
        ds[...] = data
        self.createAttributes(ds, sinkhandler)
