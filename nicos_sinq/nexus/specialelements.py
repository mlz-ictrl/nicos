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
#
# This file contains special elements to be used in NeXus template directories.
# It should contain only elements which are shared at least between two
# instruments.
#
# Module authors:
#   Mark Koennecke <Mark.Koennecke@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.pycompat import iteritems

from nicos_sinq.nexus.elements import NexusElementBase, NXAttribute


class TwoThetaArray(NexusElementBase):
    def __init__(self, startmotor, step, length, **attrs):
        self.startdevice = startmotor
        self.step = step
        self.length = length
        self.attrs = {}
        for key, val in iteritems(attrs):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        if (self.startdevice, 'value') in sinkhandler.dataset.metainfo:
            start = sinkhandler.dataset.metainfo[(self.startdevice, 'value')][
                0]
        else:
            session.log.warning('Warning: failed to read startdevice %s for '
                                'TwoThetaArray, continuing with 0',
                                self.startdevice)
            start = 0
        dset = h5parent.create_dataset(name, (self.length,), 'float32')
        for i in range(self.length):
            dset[i] = start + i * self.step
        self.createAttributes(dset, sinkhandler)


class FixedArray(NexusElementBase):
    def __init__(self, start, step, length, **attrs):
        self._start = start
        self._step = step
        self._len = length
        self.attrs = {}
        for key, val in iteritems(attrs):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (self._len,), 'float32')
        for i in range(self._len):
            dset[i] = self._start + i * self._step
        self.createAttributes(dset, sinkhandler)
