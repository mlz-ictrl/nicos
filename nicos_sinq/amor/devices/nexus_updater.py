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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import numpy
import h5py

from nicos.core import Param, dictof, listof
from nicos_ess.devices.datasinks.nexussink import NexusFileWriterStatus


class AmorNexusUpdater(NexusFileWriterStatus):
    """Updates the nexus files once they are written."""

    parameters = {
        'fileupdates': Param('Dict of hdf path mapped to tupleof: '
                             '(dev, dtype, unit)', type=dictof(str, tuple)),
        'binpaths': Param('Paths in file where bin information is stored',
                          type=listof(str))
    }

    def _on_close(self, jobid, dataset):
        NexusFileWriterStatus._on_close(self, jobid, dataset)
        filename = dataset.filepaths[0]
        try:
            nxfile = h5py.File(filename, 'r+')
        except (ValueError, IOError):
            self.log.error('Unable to edit file for dataset #%d!',
                           dataset.counter)
            return

        # Remove the last bins
        for path in self.binpaths:
            if path in nxfile:
                arr = numpy.delete(nxfile[path].value, -1)
                axis = nxfile[path].attrs['axis']
                unit = nxfile[path].attrs['units']
                del nxfile[path]
                ds = nxfile.create_dataset(path, arr.shape,
                                           dtype=str(arr.dtype), data=arr)
                ds.attrs['axis'] = axis
                ds.attrs['units'] = unit

        for path in self.fileupdates:
            dev, dtype, unit = self.fileupdates[path]
            if dev in dataset.values:
                value = dataset.values[dev]
                shape = numpy.atleast_1d(value).shape
                if path in nxfile:
                    del nxfile[path]
                nxdset = nxfile.create_dataset(path, shape, dtype=dtype,
                                               data=value)
                nxdset.attrs['units'] = unit
                nxdset.attrs['nicos_name'] = dev
        nxfile.close()
