# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
from nicos.core.device import Readable
from nicos.core.errors import ConfigurationError
from nicos.nexus.elements import DeviceDataset, NexusElementBase, \
    NexusSampleEnv, NXAttribute

from nicos_sinq.devices.sample import CrystalSample
from nicos_sinq.devices.sinqhm.configurator import HistogramConfArray


class TwoThetaArray(NexusElementBase):
    def __init__(self, startmotor, step, length, **attrs):
        NexusElementBase.__init__(self)
        self.startdevice = startmotor
        self.step = step
        self.length = length
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val

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
        NexusElementBase.__init__(self)
        self._start = start
        self._step = step
        self._len = length
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val

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
        NexusElementBase.__init__(self)
        self._scale = 1.
        self._array_name = array_name
        self.attrs = {}
        for key, val in attrs.items():
            if key == 'scale':
                self._scale = float(val)
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val

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
        NexusElementBase.__init__(self)
        self.dev = dev
        self.parameter = parameter
        self.dtype = dtype
        self.reshape = reshape
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val

    def create(self, name, h5parent, sinkhandler):
        if (self.dev, self.parameter) in sinkhandler.dataset.metainfo:
            rawvalue = sinkhandler.dataset.metainfo[
                (self.dev, self.parameter)][0]
            value = np.array(rawvalue, self.dtype)
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
        NexusElementBase.__init__(self)
        self.idx = idx
        self.reflist = reflist
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
                self.attrs[key] = val

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
        dtype = f'S{len(scanvars) + 1}'
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = scanvars


class ScanCommand(NexusElementBase):
    """
    This class writes the last scan command
    """
    def create(self, name, h5parent, sinkhandler):
        com = session._script_text
        dtype = f'S{len(com) + 1}'
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
        dataset = sinkhandler.dataset
        for dev, value in zip(dataset.devices + dataset.environment,
                              dataset.devvaluelist + dataset.envvaluelist):
            if dev.name == self.device:
                if self.doAppend:
                    self.resize_dataset(dset)
                    dset[self.np] = value


class OutSampleEnv(NexusSampleEnv):
    """
    This class is another helper to implement the OUT
    functionality. It prevents NXlogs to be created for
    standard instrument components.
    """
    def __init__(self, blocklist=None, update_interval=10, postfix=None):
        self._blocklist = blocklist
        NexusSampleEnv.__init__(self, update_interval, postfix)

    def isValidDevice(self, dev):
        if self._blocklist and dev.name in self._blocklist:
            return False
        return True

    def create(self, name, h5parent, sinkhandler):
        self.starttime = time.time()
        for dev, value in zip(sinkhandler.dataset.environment,
                              sinkhandler.dataset.envvaluelist):
            # There can be DeviceStatistics in the environment.
            # We do not know how to write those
            if isinstance(dev, Readable) and self.isValidDevice(dev):
                self.createNXlog(h5parent, dev.name, value)

    def updatelog(self, h5parent, dataset):
        current_time = time.time()
        for dev, val in zip(dataset.environment, dataset.envvaluelist):
            if not isinstance(dev, Readable) or not self.isValidDevice(dev):
                continue
            logname = dev.name
            if self._postfix:
                logname += self._postfix
            loggroup = h5parent[logname]
            dset = loggroup['value']
            if val is None:
                return
            idx = len(dset)
            # We need to control the amount of data written as update
            # gets called frequently. This tests:
            # - The value has changed at all
            # - Against a maximum update interval
            if val != dset[idx - 1] and \
               current_time > self._last_update[dev.name] +\
                    self._update_interval:
                dset.resize((idx + 1,))
                dset[idx] = val
                dset = loggroup['time']
                dset.resize((idx + 1,))
                dset[idx] = current_time - self.starttime
                self._last_update[dev.name] = current_time


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
    nicos_sinq.devices.CrystalSample, nicos_sinq.sxtal.SXTalsample as an array
    """
    def create(self, name, h5parent, sinkhandler):
        sample = session.experiment.sample
        if not isinstance(sample, CrystalSample):
            session.log.error('Your sample is no CrystalSample or SXTalSample')
            return
        data = [sample.a, sample.b, sample.c,
                sample.alpha, sample.beta, sample.gamma]
        ds = h5parent.create_dataset(name, (6,), maxshape=(None,),
                                     dtype='float64')
        ds[...] = np.array(data)


class DevStat(NexusElementBase):
    """
    This class stores data from a DevStatistics environment
    contribution. This is allways optional and will only be
    written when it exists.
    """
    def __init__(self, statname, **attr):
        NexusElementBase.__init__(self)
        self._statname = statname
        self.attrs = {}
        for key, val in attr.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def _find_devstatistics(self, sinkhandler):
        for dev in sinkhandler.dataset.environment:
            if dev.name == self._statname:
                return dev
        return None

    def create(self, name, h5parent, sinkhandler):
        if self._find_devstatistics(sinkhandler):
            h5parent.create_dataset(name, (1,), maxshape=(None,),
                                    dtype='float64')
            self.createAttributes(sinkhandler.dataset, sinkhandler)
            self.testAppend(sinkhandler)

    def results(self, name, h5parent, sinkhandler, results):
        devstat = self._find_devstatistics(sinkhandler)
        if devstat:
            dset = h5parent[name]
            val = devstat.retrieve(sinkhandler.dataset.valuestats)
            if self.doAppend:
                self.resize_dataset(dset)
                dset[self.np] = val
            else:
                dset[0] = val


class ScanSampleEnv(NexusElementBase):
    """
    This class stores all known environment devices using their NICOS
    names.
    """

    def __init__(self):
        NexusElementBase.__init__(self)
        self.doAppend = True
        self._managed_devices = []

    def create(self, name, h5parent, sinkhandler):
        for dev, inf in zip(sinkhandler.dataset.environment,
                            sinkhandler.dataset.envvalueinfo):
            # Prevent duplicate creations
            if dev.name not in h5parent:
                dset = h5parent.create_dataset(dev.name, (1,),
                                               maxshape=(None,), dtype=float)
                dset.attrs['units'] = np.bytes_(inf.unit)
                self._managed_devices.append(dev.name)

    def results(self, name, h5parent, sinkhandler, results):
        for dev, value in zip(sinkhandler.dataset.environment,
                              sinkhandler.dataset.envvaluelist):
            if dev.name in self._managed_devices:
                dset = h5parent[dev.name]
                self.resize_dataset(dset)
                dset[self.np] = value


class SaveSampleEnv(NexusElementBase):
    """Element for storing sample environment data.

    It looks at the dataset.environment field and creates a NXlog structure
    with the sample environment devices name and a postfix appended.
    To this NXlog structure, incoming data is appended whenever
    data can be found.

    It also creates arrays using the names found in dataset.environment
    in order to recreate the traditional NeXus structure of having one
    array entry per scan point.

    This also attempts to translate the secop names into NeXus names. This
    may be highly specific to SINQ.

    On some instruments, most notably TAS, the dataset.environment is used to
    log additional motors together with the data. In such cases, the
    generation of a NXlog is undesirable and is suppressed. In order
    to identify such cases there is a blocklist.
    """

    def __init__(self, update_interval=10, postfix='_log',
                 blocklist=None, nexus_map=None):
        NexusElementBase.__init__(self)
        self._update_interval = update_interval
        self._last_update = {}
        self._postfix = postfix
        if blocklist:
            self._blocklist = blocklist
        else:
            self._blocklist = []
        if nexus_map:
            self.nexus_map = nexus_map
        else:
            self.nexus_map = {'Ts': 'temperature', 'B': 'magnetic_field'}
        self.doAppend = True
        self._managed_devices = []

    def _get_logname(self, devicename):
        return self.nexus_map.get(devicename, devicename)

    def isValidDevice(self, dev):
        if self._blocklist and dev.name in self._blocklist:
            return False
        return isinstance(dev, Readable)

    def createNXlog(self, h5parent, devname, value):
        logname = self._get_logname(devname)
        if self._postfix:
            logname += self._postfix
        loggroup = h5parent.create_group(logname)
        loggroup.attrs['NX_class'] = np.bytes_('NXlog')
        dset = loggroup.create_dataset('time', (1,), maxshape=(None,),
                                       dtype='float32')
        dset[0] = .0
        dset.attrs['start'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.starttime))
        dset = loggroup.create_dataset('value', (1,), maxshape=(None,),
                                       dtype='float32')
        dset[0] = value
        self._last_update[devname] = time.time()

    def create(self, name, h5parent, sinkhandler):
        self.starttime = time.time()
        for dev, value in zip(sinkhandler.dataset.environment,
                              sinkhandler.dataset.envvaluelist):
            # There can be DeviceStatistics in the environment.
            # We do not know how to write those
            if self.isValidDevice(dev):
                self.createNXlog(h5parent, dev.name, value)
        self.createArrays(name, h5parent, sinkhandler)

    def updatelog(self, h5parent, dataset):
        current_time = time.time()
        for dev, val in zip(dataset.environment, dataset.envvaluelist):
            if not self.isValidDevice(dev):
                continue
            logname = self._get_logname(dev.name)
            if self._postfix:
                logname += self._postfix
            loggroup = h5parent[logname]
            dset = loggroup['value']
            if val is None:
                continue
            idx = len(dset)
            # We need to control the amount of data written as update
            # gets called frequently. This tests:
            # - The value has changed at all
            # - Against a maximum update interval
            if val != dset[idx - 1] and \
               current_time > self._last_update[dev.name] +\
                    self._update_interval:
                dset.resize((idx + 1,))
                dset[idx] = val
                dset = loggroup['time']
                dset.resize((idx + 1,))
                dset[idx] = current_time - self.starttime
                self._last_update[dev.name] = current_time

    def createArrays(self, name, h5parent, sinkhandler):
        for dev, inf in zip(sinkhandler.dataset.environment,
                            sinkhandler.dataset.envvalueinfo):
            # Prevent duplicate creations
            arrayname = self._get_logname(dev.name)
            if arrayname not in h5parent:
                dset = h5parent.create_dataset(arrayname, (1,),
                                               maxshape=(None,), dtype=float)
                dset.attrs['units'] = np.bytes_(inf.unit)
                self._managed_devices.append(arrayname)

    def resultsArray(self, name, h5parent, sinkhandler, results):
        for dev, value in zip(sinkhandler.dataset.environment,
                              sinkhandler.dataset.envvaluelist):
            arrayname = self._get_logname(dev.name)
            if arrayname in self._managed_devices:
                dset = h5parent[arrayname]
                self.resize_dataset(dset)
                dset[self.np] = value

    def update(self, name, h5parent, sinkhandler, values):
        self.updatelog(h5parent, sinkhandler.dataset)

    def results(self, name, h5parent, sinkhandler, results):
        self.updatelog(h5parent, sinkhandler.dataset)
        self.resultsArray(name, h5parent, sinkhandler, results)
