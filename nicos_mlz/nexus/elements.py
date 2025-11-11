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

import time

import numpy as np

from nicos.core.device import Readable
from nicos.core.params import tupleof
from nicos.nexus.elements import DeviceDataset, NexusElementBase

from nicos_mlz.nexus.structures import nounit


class ScanDeviceDataset(DeviceDataset):
    """Placeholder a device which has a value for each scan point."""

    def testAppend(self, sinkhandler):
        NexusElementBase.testAppend(self, sinkhandler)


class Reflection(NexusElementBase):
    """Placeholder for reflection of single crystal, stored as an array.

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


class SampleEnv(NexusElementBase):
    """Placeholder for storing sample environment data.

    It looks at the dataset.environment field and creates a NXlog structure
    with the in devices given list of sample environment devices names.
    To this NXlog structure, incoming data is appended whenever data can be
    found. The update_interval defines the minimum time between new value
    adding into the logging list.
    """

    statistics_entries = ('average_value', 'average_value_errors',
                          'minimum_value', 'maximum_value')

    def __init__(self, devices, update_interval=10):
        NexusElementBase.__init__(self)
        self._update_interval = update_interval
        self._last_update = {}
        self._devices = devices or []

    def createNXlog(self, h5parent, devname, value):
        sensorname = devname
        sensorgroup = h5parent.create_group(sensorname)
        sensorgroup.attrs['NX_class'] = np.bytes_('NXsensor')
        loggroup = sensorgroup.create_group('value_log')
        loggroup.attrs['NX_class'] = np.bytes_('NXlog')
        dset = loggroup.create_dataset('time', (1,), maxshape=(None,),
                                       dtype='float32')
        dset[0] = .0
        dset.attrs['start'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.starttime))
        dset = loggroup.create_dataset('value', (1,), maxshape=(None,),
                                       dtype='float32')
        dset[0] = value

        self._last_update[sensorname] = time.time()

        for name in self.statistics_entries:
            dset = loggroup.create_dataset(name, (1,), maxshape=(None,),
                                           dtype='float')
            dset[0] = 0

    def create(self, name, h5parent, sinkhandler):
        self.starttime = time.time()
        for dev, value in zip(sinkhandler.dataset.environment,
                              sinkhandler.dataset.envvaluelist):
            if dev.name not in self._devices:
                continue
            # There can be DeviceStatistics in the environment.
            # We do not know how to write those
            if isinstance(dev, Readable):
                self.createNXlog(h5parent, dev.name, value)

    def updatelog(self, h5parent, dataset):
        current_time = time.time()
        for dev, val in zip(dataset.environment, dataset.envvaluelist):
            logname = dev.name
            if logname not in self._devices:
                continue
            if val is None:
                continue
            # We need to control the amount of data written as update gets
            # called frequently. Tests against a maximum update interval
            if current_time <= self._last_update[logname] +\
                    self._update_interval:
                continue
            loggroup = h5parent[logname]['value_log']

            dset = loggroup['time']
            idx = len(dset)
            dset.resize((idx + 1,))
            dset[idx] = current_time - self.starttime
            self._last_update[dev.name] = current_time

            dset = loggroup['value']
            dset.resize((idx + 1,))
            dset[idx] = val

    def updateStatistics(self, h5parent, dataset):
        for dev, values in dataset.valuestats.items():
            if dev not in self._devices:
                continue
            loggroup = h5parent[dev]['value_log']
            for name, val in zip(self.statistics_entries, values):
                dset = loggroup[name]
                dset[0] = val

    def update(self, name, h5parent, sinkhandler, values):
        self.updatelog(h5parent, sinkhandler.dataset)

    def results(self, name, h5parent, sinkhandler, results):
        self.updatelog(h5parent, sinkhandler.dataset)
        self.updateStatistics(h5parent, sinkhandler.dataset)
