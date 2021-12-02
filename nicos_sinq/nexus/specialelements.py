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
#
# This file contains special elements to be used in NeXus template directories.
# It should contain only elements which are shared at least between two
# instruments.
#
# Module authors:
#   Mark Koennecke <Mark.Koennecke@psi.ch>
#
# *****************************************************************************

import time

import numpy as np

from nicos import session
from nicos.core.errors import ConfigurationError
from nicos.nexus.elements import DeviceDataset, NexusElementBase, \
    NexusSampleEnv, NXAttribute

from nicos_sinq.devices.sinqhm.configurator import HistogramConfArray
from nicos_sinq.sxtal.sample import SXTalSample


class TwoThetaArray(NexusElementBase):
    def __init__(self, startmotor, step, length, **attrs):
        self.startdevice = startmotor
        self.step = step
        self.length = length
        self.attrs = {}
        for key, val in attrs.items():
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
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (self._len,), 'float32')
        for i in range(self._len):
            dset[i] = self._start + i * self._step
        self.createAttributes(dset, sinkhandler)


class ConfArray(NexusElementBase):
    """
    Store data from a Sinqhm configuration array
    """

    def __init__(self, array_name, **attrs):
        self._scale = 1.
        self._array_name = array_name
        self.attrs = {}
        for key, val in attrs.items():
            if key == 'scale':
                self._scale = float(val)
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        try:
            array = session.getDevice(self._array_name)
            if not isinstance(array, HistogramConfArray):
                raise ConfigurationError('{self._array_name} is no '
                                         'HistogramConfArray')
        except ConfigurationError:
            session.log.warning('Array %s not found, NOT stored',
                                self._array_name)
            return
        dset = h5parent.create_dataset(name, tuple(array.dim), 'float32')
        dset[...] = np.array(array.data, dtype='float32') * self._scale
        self.createAttributes(dset, sinkhandler)


class TimeBinConfArray(ConfArray):
    """
    At SINQ we do not store the last bin in the time_binning
    in the NeXus file. Such that the dimensions of the data and
    the time binning match
    """
    def create(self, name, h5parent, sinkhandler):
        try:
            array = session.getDevice(self._array_name)
            if not isinstance(array, HistogramConfArray):
                raise ConfigurationError('%s is no HistogramConfArray' %
                                         self._array_name)
        except ConfigurationError:
            session.log.warning('Array %s not found, NOT stored',
                                self._array_name)
            return
        timeDim = array.dim[0]-1
        dset = h5parent.create_dataset(name, (timeDim,), 'float32')
        data = np.array(array.data, dtype='float32')
        data = data[0:timeDim]
        if self._scale != 1.:
            dset[...] = data * self._scale
        else:
            dset[...] = data
        self.createAttributes(dset, sinkhandler)


class ArrayParam(NexusElementBase):
    """
    For writing an array parameter to a NeXus file
    """
    def __init__(self, dev, parameter, dtype, reshape=None, **attrs):
        self.dev = dev
        self.parameter = parameter
        self.dtype = dtype
        self.reshape = reshape
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        if (self.dev, self.parameter) in sinkhandler.dataset.metainfo:
            rawvalue = sinkhandler.dataset.metainfo[
                (self.dev, self.parameter)]
            value = np.array(rawvalue, ([]), self.dtype)
            if self.reshape:
                value = value.reshape(self.reshape)
            dset = h5parent.create_dataset(name, value.shape, self.dtype)
            dset[...] = value
            self.createAttributes(dset, sinkhandler)
        else:
            session.log.warning('Failed to write %s, device %s not found',
                                name, self.dev)


class Reflection(NexusElementBase):
    """
    Writes reflection data to the NeXus file
    """
    def __init__(self, idx, reflist, **attrs):
        self.idx = idx
        self.reflist = reflist
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        try:
            rlist = session.getDevice(self.reflist)
            try:
                rfl = rlist.get_reflection(self.idx)
            except IndexError:
                session.log.warning('Failed to write %s, cannot find '
                                    'reflection %d', name, self.idx)
                return
        except ConfigurationError:
            session.log.warning('Failed to write %s, reflist %s not '
                                'found or reflection %d not found',
                                name, self.dev, self.idx)
            return
        value = np.array([el for tup in rfl for el in tup], 'float32')
        dset = h5parent.create_dataset(name, value.shape, 'float32')
        dset[...] = value
        self.createAttributes(dset, sinkhandler)


class ScanVars(NexusElementBase):
    """
    This class writes a list of scanned variables
    """
    def create(self, name, h5parent, sinkhandler):
        scanvars = ''
        if sinkhandler.startdataset.devices:
            for dev in sinkhandler.startdataset.devices:
                scanvars += dev.name + ','
        dtype = 'S{len(scanvars) + 1}'
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = scanvars


class ScanCommand(NexusElementBase):
    """
    This class writes the last scan command
    """
    def create(self, name, h5parent, sinkhandler):
        com = session._script_text
        dtype = 'S{len(com) + 1)}'
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = com


class AbsoluteTime(NexusElementBase):
    """
    Little class which stores the absolute time at each scan
    point
    """

    def create(self, name, h5parent, sinkhandler):
        h5parent.create_dataset(name, (1,), maxshape=(None,),
                                dtype='float64')
        self.doAppend = True

    def results(self, name, h5parent, sinkhandler, results):
        dset = h5parent[name]
        self.resize_dataset(dset)
        dset[self.np] = time.time()


class EnvDeviceDataset(DeviceDataset):
    """
    The OUT variable in TAS allows to have other values to be
    logged with the data. In NICOS, this is implemented by adding those
    values to the environment. In order to get the log into the NeXus
    file, this special class also searches the environment for values
    to store.
    """

    def results(self, name, h5parent, sinkhandler, results):
        if name not in h5parent:
            # can happen, when we cannot find the device on creation
            return
        dset = h5parent[name]
        for dev in sinkhandler.dataset.devices + \
                sinkhandler.dataset.environment:
            if dev.name == self.device:
                value = dev.read()
                if self.doAppend:
                    self.resize_dataset(dset)
                    dset[self.np] = value


class OutSampleEnv(NexusSampleEnv):
    """
    This class is another helper to implement the OUT
    functionality. It prevents NXlogs to be created for
    standard instrument components.
    """
    def __init__(self, blocklist=None, update_interval=10):
        self._blocklist = blocklist
        NexusSampleEnv.__init__(self, update_interval)

    def isValidDevice(self, dev):
        if self._blocklist and dev.name in self._blocklist:
            return False
        return NexusElementBase.isValidDevice(self, dev)


class OptionalDeviceDataset(DeviceDataset):
    """
    A device dataset which is only written when it is actually configured
    """
    def __init__(self, device, parameter='value', dtype=None, defaultval=None,
                 **attr):
        self.valid = False
        DeviceDataset.__init__(self, device, parameter='value', dtype=None,
                               defaultval=None, **attr)

    def create(self, name, h5parent, sinkhandler):
        try:
            _ = session.getDevice(self.device)
            self.valid = True
            DeviceDataset.create(self, name, h5parent, sinkhandler)
        except ConfigurationError:
            pass

    def update(self, name, h5parent, sinkhandler, values):
        if self.valid:
            DeviceDataset.update(self, name, h5parent, sinkhandler, values)

    def results(self, name, h5parent, sinkhandler, results):
        if self.valid:
            DeviceDataset.results(self, name, h5parent, sinkhandler, results)


class CellArray(NexusElementBase):
    """
    This little class stores the cell constants from
    nicos_sinq.sxtal.SXTalsample as an array
    """
    def create(self, name, h5parent, sinkhandler):
        sample = session.experiment.sample
        if not isinstance(sample, SXTalSample):
            session.log.error('Your sample is no SXTalSample')
            return
        data = [sample.a, sample.b, sample.c,
                sample.alpha, sample.beta, sample.gamma]
        ds = h5parent.create_dataset(name, (6,), maxshape=(None,),
                                     dtype='float64')
        ds[...] = np.array(data)
