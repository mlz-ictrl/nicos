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
#   Mark Koennecke <Mark.Koennecke@psi.ch>
#
# *****************************************************************************
import time
from datetime import datetime

import h5py
import numpy as np

from nicos import session
from nicos.core.device import Readable
from nicos.core.errors import NicosError


class NexusElementBase:
    """Interface class to define NeXus elements.

    All NeXus elements ought to supply four methods:

    - create() which is called when the NeXus structure is created and static
      data is written
    - update() for in place updating of already created items in the NeXus file
    - append() increments the np counter when a new scan point is started
    - results() saves the result of a scan points data

    The default implementations of create(), results() and update() do nothing.
    Overload when this is not sufficient.
    """

    dtype = None

    def __init__(self):
        self.doAppend = False
        self.np = 0

    def create(self, name, h5parent, sinkhandler):
        raise NotImplementedError()

    def update(self, name, h5parent, sinkhandler, values):
        pass

    def results(self, name, h5parent, sinkhandler, results):
        pass

    def append(self, name, h5parent, sinkhandler, subset):
        if self.doAppend:
            self.np = self.np + 1

    def resize_dataset(self, dset):
        idx = self.np + 1
        if len(dset) < idx:
            dset.resize((idx,))

    def testAppend(self, sinkhandler):
        self.doAppend = bool((hasattr(sinkhandler.startdataset,
                                      'npoints') and
                              sinkhandler.startdataset.npoints > 1) or
                             hasattr(session, '_manualscan'))
        self.np = 0

    def determineType(self):
        if self.dtype is None:
            if isinstance(self.value, tuple):
                if isinstance(self.value[0], int):
                    if self.value[0] < 2**32:
                        self.dtype = 'int32'
                    else:
                        self.dtype = 'int64'
                elif isinstance(self.value[0], float):
                    self.dtype = 'double'
                elif isinstance(self.value[0], str):
                    self.dtype = 'string'

            if isinstance(self.value, str):
                self.dtype = 'string'

    def createAttributes(self, h5obj, sinkhandler):
        if not hasattr(self, 'attrs'):
            return
        for key, val in self.attrs.items():
            if isinstance(val, str):
                val = NXAttribute(val, 'string')
            val.create(key, h5obj, sinkhandler)

    def scanlink(self, name, sinkhandler, h5parent, linkroot):
        pass

    def test_written(self, name, h5obj):
        """Mainly for the external link and test if it has been written."""


class NXAttribute(NexusElementBase):
    """Placeholder for a NeXus Attribute."""

    def __init__(self, value, dtype):
        NexusElementBase.__init__(self)
        self.dtype = dtype
        self.value = value

    def create(self, name, h5parent, sinkhandler):
        if self.dtype == 'string':
            h5parent.attrs[name] = np.string_(self.value)
        else:
            h5parent.attrs.create(name, self.value, dtype=self.dtype)


class ConstDataset(NexusElementBase):
    """Placeholder for a Dataset with a constant value."""

    def __init__(self, value, dtype, **attrs):
        NexusElementBase.__init__(self)
        self.value = value
        self.dtype = dtype
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def create(self, name, h5parent, sinkhandler):
        if self.dtype == 'string':
            dtype = 'S%d' % (len(self.value.encode('utf-8')) + 1)
            dset = h5parent.create_dataset(name, (1,), dtype)
            dset[0] = np.array(self.value.encode('utf-8'), dtype=dtype)
        elif isinstance(self.value, (tuple, list)):
            dset = h5parent.create_dataset(name, (len(self.value),),
                                           dtype=self.dtype)
            for i, v in enumerate(self.value):
                dset[i] = v
        else:
            dset = h5parent.create_dataset(name, (1,), dtype=self.dtype)
            dset[0] = self.value
        self.createAttributes(dset, sinkhandler)


class DeviceAttribute(NXAttribute):
    """Placeholder for a device attribute.

    This creates a NeXus group or dataset attribute from the value or
    parameter of the device.
    """

    def __init__(self, device, parameter='value', dtype=None, defaultval=None):
        NXAttribute.__init__(self, defaultval, dtype)
        self.device = device
        self.parameter = parameter
        self.dtype = dtype
        self.defaultval = defaultval
        self.np = 0
        self.doAppend = False

    def create(self, name, h5parent, sinkhandler):
        if (self.device, self.parameter) in sinkhandler.dataset.metainfo:
            self.value = \
                sinkhandler.dataset.metainfo[(self.device, self.parameter)][0]
        else:
            self.value = self.defaultval
        if self.value is not None:
            self.determineType()
            NXAttribute.create(self, name, h5parent, sinkhandler)


class DeviceDataset(NexusElementBase):
    """Placeholder for a device.#

    This creates a NeXus dataset from the value or a parameter of a device.
    """

    def __init__(self, device, parameter='value', dtype=None, defaultval=None,
                 **attr):
        NexusElementBase.__init__(self)
        self.device = device
        self.parameter = parameter
        self.dtype = dtype
        self.defaultval = defaultval
        self.attrs = {}
        self.doAppend = False
        for key, val in attr.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def testAppend(self, sinkhandler):
        NexusElementBase.testAppend(self, sinkhandler)
        if self.device not in (v.name for v in (
                sinkhandler.startdataset.devvalueinfo +
                sinkhandler.startdataset.envvalueinfo)):
            self.doAppend = False

    def create(self, name, h5parent, sinkhandler):
        if (self.device, self.parameter) in sinkhandler.dataset.metainfo:
            self.value = sinkhandler.dataset.metainfo[
                (self.device, self.parameter)]
        else:
            self.value = (self.defaultval,)
        if self.value[0] is not None:
            self.determineType()
        else:
            try:
                dev = session.getDevice(self.device)
                self.value = (getattr(dev, self.parameter, self.defaultval),)
                self.determineType()
            except Exception as e:
                session.log.warning(
                    'Warning: failed to locate data for %s %s in NICOS (%s)',
                    self.device, self.parameter, e)
                return
        if self.parameter == 'value':
            self.testAppend(sinkhandler)
        if self.dtype == 'string':
            dtype = 'S%d' % (len(self.value[0].encode('utf-8')) + 1)
            dset = h5parent.create_dataset(name, (1,), dtype=dtype)
            dset[0] = np.array(self.value[0].encode('utf-8'), dtype=dtype)
        else:
            if self.doAppend:
                dset = h5parent.create_dataset(name, (1,), maxshape=(None,),
                                               dtype=self.dtype)
            else:
                dset = h5parent.create_dataset(name, (1,), dtype=self.dtype)
            dset[0] = self.value[0]
            if 'units' not in self.attrs:
                if self.parameter in ['target']:
                    try:
                        inf = session.getDevice(self.device).info()
                        self.attrs['units'] = NXAttribute(inf[0][3], 'string')
                    except NicosError:
                        pass
                elif len(self.value) > 2:
                    dset.attrs['units'] = np.string_(self.value[2])
        self.createAttributes(dset, sinkhandler)

    def update(self, name, h5parent, sinkhandler, values):
        # Do not try to update anything else then values
        if self.parameter != 'value':
            return
        if (self.device, self.parameter) in sinkhandler.dataset.metainfo:
            self.value = sinkhandler.dataset.metainfo[
                (self.device, self.parameter)]
            dset = h5parent[name]
            if self.dtype != 'string':
                self.resize_dataset(dset)
                dset[self.np] = self.value[0]
        else:
            # This data missing is normal
            pass

    def results(self, name, h5parent, sinkhandler, results):
        if name not in h5parent:
            # can happen, when we cannot find the device on creation
            return
        if not self.doAppend:
            return

        dset = h5parent[name]
        devinfo = (sinkhandler.dataset.devvalueinfo +
                   sinkhandler.dataset.envvalueinfo)
        values = (sinkhandler.dataset.devvaluelist +
                  sinkhandler.dataset.envvaluelist)
        for dev, val in zip(devinfo, values):
            if dev.name == self.device:
                self.resize_dataset(dset)
                dset[self.np] = val

    def scanlink(self, name, sinkhandler, h5parent, linkroot):
        for dev in sinkhandler.dataset.devices:
            if dev.name == self.device:
                dset = h5parent[name]
                parent = h5parent[linkroot]
                if name not in parent:
                    parent[name] = dset
                    dset.attrs['target'] = np.string_(dset.name)
                else:
                    session.log.warning('Trying to create %s a second time',
                                        name)


class DetectorDataset(NexusElementBase):
    """Placeholder for a detector data dataset."""

    def __init__(self, nicosname, dtype, **attr):
        NexusElementBase.__init__(self)
        self.nicosname = nicosname
        self.dtype = dtype
        # Hack for countmode which is a short text
        if self.dtype == 'string':
            self.dtype = 'S30'
        self.attrs = {}
        for key, val in attr.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    # At creation time, I do not yet have a value for detector data. This is
    # why the dtype needs to be specified. Values can only get written on
    # update()
    def create(self, name, h5parent, sinkhandler):
        self.testAppend(sinkhandler)
        if self.doAppend:
            dset = h5parent.create_dataset(name, (1,), maxshape=(None,),
                                           dtype=self.dtype)
        else:
            dset = h5parent.create_dataset(name, (1,), dtype=self.dtype)
        self.createAttributes(dset, sinkhandler)

    def update(self, name, h5parent, sinkhandler, values):
        dset = h5parent[name]
        if self.nicosname == 'mode':
            m = list(sinkhandler.startdataset.preset.keys())[0]
            if m == 't':
                mode = 'timer'
            else:
                mode = 'monitor'
            dset[0] = np.string_(mode)
        elif self.nicosname == 'preset':
            mp = sinkhandler.startdataset.preset.values()
            self.resize_dataset(dset)
            dset[0] = list(mp)[0]
        else:
            try:
                val = sinkhandler.dataset.values[self.nicosname]
                self.resize_dataset(dset)
                dset[self.np] = val
            except Exception:
                # This is normal: the dataset called with
                # SinkHandler.updateValues()
                # does not necessarily contain all the data
                pass

    def results(self, name, h5parent, sinkhandler, results):
        dset = h5parent[name]
        if self.nicosname == 'mode':
            m = list(sinkhandler.startdataset.preset.keys())[0]
            if m == 't':
                mode = 'timer'
            else:
                mode = 'monitor'
                dset[0] = np.string_(mode)
        elif self.nicosname == 'preset':
            mp = sinkhandler.startdataset.preset.values()
            dset[0] = list(mp)[0]
        else:
            try:
                val = sinkhandler.dataset.values[self.nicosname]
                if self.doAppend:
                    self.resize_dataset(dset)
                dset[self.np] = val
            except Exception:
                session.log.warning('failed to find result for %s',
                                    self.nicosname)


class ImageDataset(NexusElementBase):
    """Placeholder for a detector image."""

    def __init__(self, detectorIDX, imageIDX, **attrs):
        NexusElementBase.__init__(self)
        self.detectorIDX = detectorIDX
        self.imageIDX = imageIDX
        self.attrs = {}
        self.doAppend = False
        self.np = 0
        self.valid = True
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def create(self, name, h5parent, sinkhandler):
        self.testAppend(sinkhandler)
        if len(sinkhandler.dataset.detectors) <= self.detectorIDX:
            session.log.warning('Cannot find detector with ID %d',
                                self.detectorIDX)
            self.valid = False
            return
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        arinfo = det.arrayInfo()
        myDesc = arinfo[self.imageIDX]
        rawshape = myDesc.shape
        if self.doAppend:
            shape = list(rawshape)
            shape.insert(0, 1)
            maxshape = list(rawshape)
            maxshape.insert(0, None)
            chonk = list(rawshape)
            chonk.insert(0, 1)
            dset = h5parent.create_dataset(name, shape, maxshape=maxshape,
                                           chunks=tuple(chonk),
                                           dtype=myDesc.dtype,
                                           compression='gzip')
        else:
            dset = h5parent.create_dataset(name, rawshape,
                                           chunks=tuple(rawshape),
                                           dtype=myDesc.dtype,
                                           compression='gzip')
        self.createAttributes(dset, sinkhandler)

    def resize_dataset(self, dset, sinkhandler):
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        arinfo = det.arrayInfo()
        myDesc = arinfo[self.imageIDX]
        rawshape = myDesc.shape
        idx = self.np + 1
        shape = list(rawshape)
        shape.insert(0, idx)
        dset.resize(shape)

    def results(self, name, h5parent, sinkhandler, results):
        dset = h5parent[name]
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        data = results.get(det.name)
        if data is not None:
            array = data[1][self.imageIDX]
            if array is None:
                return
            if self.doAppend:
                idx = self.np + 1
                if len(dset) < idx:
                    self.resize_dataset(dset, sinkhandler)
                dset[self.np] = array
            else:
                h5parent[name][...] = array


class NamedImageDataset(ImageDataset):
    """Placeholder for a detector image identified by name."""
    def __init__(self, image_name, **attrs):
        self._image_name = image_name
        ImageDataset.__init__(self, -1, -1, **attrs)

    def create(self, name, h5parent, sinkhandler):
        detID = 0
        imageID = 0
        for det in sinkhandler.dataset.detectors:
            arList = det.arrayInfo()
            for ar in arList:
                if ar.name == self._image_name:
                    self.detectorIDX = detID
                    self.imageIDX = imageID
                    break
                imageID += 1
            detID += 1
        if self.detectorIDX == -1 or self.imageIDX == -1:
            self.log.warning('Cannot find named image %s', self._image_name)
            self.valid = False
            return
        ImageDataset.create(self, name, h5parent, sinkhandler)


class NXLink(NexusElementBase):
    """Placeholder for a NeXus link.

    I can only create it on update because the order of tree traversal is
    undefined and in create() the object to link against may not have been
    created yet.
    """

    def __init__(self, target):
        NexusElementBase.__init__(self)
        self.target = target
        self.linkCreated = False

    def create(self, name, h5parent, sinkhandler):
        # The __init__() linkCreated is only initialised at template
        # initialisation time!
        self.linkCreated = False

    def update(self, name, h5parent, sinkhandler, values):
        if not self.linkCreated:
            try:
                other = h5parent[self.target]
            except KeyError:
                session.log.warning(
                    'Cannot link %s to %s, target does not exist',
                    name, self.target)
                return
            h5parent[name] = other
            other.attrs['target'] = np.string_(self.target)
            self.linkCreated = True


class NXScanLink(NexusElementBase):
    """Placeholder to identify where the scan devices ought to be linked to."""

    def __init__(self):
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        pass


class NXTime(NexusElementBase):
    """Placeholder for a NeXus compatible time entry."""

    def formatTime(self):
        return datetime.now().isoformat(sep=' ', timespec='milliseconds')

    def create(self, name, h5parent, sinkhandler):
        time_str = self.formatTime()
        dtype = 'S%d' % (len(time_str) + 5)
        dset = h5parent.create_dataset(name, (1,), dtype=dtype)
        dset[0] = np.string_(time_str)

    def update(self, name, h5parent, sinkhandler, values):
        if name.find('end') >= 0:
            dset = h5parent[name]
            dset[0] = np.string_(self.formatTime())


class StartTime(NXTime):
    """Place holder for the start time of a measurement."""

    def __init__(self):
        NXTime.__init__(self)
        self.time = 0

    def formatTime(self):
        return datetime.fromtimestamp(self.time).isoformat(
            sep=' ', timespec='milliseconds')

    def create(self, name, h5parent, sinkhandler):
        self.time = sinkhandler.dataset.started
        NXTime.create(self, name, h5parent, sinkhandler)


class EndTime(StartTime):
    """Place holder for the end time of a measurement."""

    def create(self, name, h5parent, sinkhandler):
        self.time = sinkhandler.dataset.finished or time.time()
        NXTime.create(self, name, h5parent, sinkhandler)

    def update(self, name, h5parent, sinkhandler, values):
        self.time = sinkhandler.dataset.finished or time.time()
        dset = h5parent[name]
        dset[0] = np.string_(self.formatTime())


class NexusSampleEnv(NexusElementBase):
    """Placeholder for storing sample environment data.

    It looks at the dataset.environment field and creates a NXlog structure
    with the sample environment devices name. To this NXlog structure, incoming
    data is appended whenever data can be found.
    """

    def __init__(self, update_interval=10, postfix=None):
        NexusElementBase.__init__(self)
        self._update_interval = update_interval
        self._last_update = {}
        self._postfix = postfix

    def createNXlog(self, h5parent, devname, value):
        logname = devname
        if self._postfix:
            logname += self._postfix
        loggroup = h5parent.create_group(logname)
        loggroup.attrs['NX_class'] = np.string_('NXlog')
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
            if isinstance(dev, Readable):
                self.createNXlog(h5parent, dev.name, value)

    def updatelog(self, h5parent, dataset):
        current_time = time.time()
        for devidx, dev in enumerate(dataset.environment):
            if not isinstance(dev, Readable):
                continue
            logname = dev.name
            if self._postfix:
                logname += self._postfix
            loggroup = h5parent[logname]
            dset = loggroup['value']
            val = dataset.envvaluelist[devidx]
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

    def update(self, name, h5parent, sinkhandler, values):
        self.updatelog(h5parent, sinkhandler.dataset)

    def results(self, name, h5parent, sinkhandler, results):
        self.updatelog(h5parent, sinkhandler.dataset)


class CalcData(NexusElementBase):
    """ Place holder base class for all classes which calculate data for the
    NeXus file. Derived classes have to implement two methods:

    - _shape(dataset) which returns the shape of the calculate data as a tuple
    - _calcData(dataset) which actually calculates the data value. The return
      value must be a numpy array.

    Derived classes also must make sure that self.dtype points to a sensible
    value. The default is float32.
    """
    def __init__(self, **attrs):
        NexusElementBase.__init__(self)
        self.attrs = {}
        self.doAppend = False
        self.np = 0
        self.valid = True
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val
        self.dtype = 'float32'

    def create(self, name, h5parent, sinkhandler):
        self.testAppend(sinkhandler)
        if not self.valid:
            return
        rawshape = self._shape(sinkhandler.dataset)
        if self.doAppend:
            shape = list(rawshape)
            shape.insert(0, 1)
            maxshape = list(rawshape)
            maxshape.insert(0, None)
            chonk = list(rawshape)
            chonk.insert(0, 1)
            dset = h5parent.create_dataset(name, shape, maxshape=maxshape,
                                           chunks=tuple(chonk),
                                           dtype=self.dtype,
                                           compression='gzip')
        else:
            dset = h5parent.create_dataset(name, rawshape,
                                           chunks=tuple(rawshape),
                                           dtype=self.dtype,
                                           compression='gzip')
        self.createAttributes(dset, sinkhandler)

    def results(self, name, h5parent, sinkhandler, _results):
        if not self.valid:
            return
        data = self._calcData(sinkhandler.dataset)
        if data is not None:
            dset = h5parent[name]
            if self.doAppend:
                if len(dset) < self.np + 1:
                    self.resize_dataset(dset, sinkhandler)
                dset[self.np] = data
            else:
                h5parent[name][...] = data

    def resize_dataset(self, dset, sinkhandler):
        rawshape = self._shape(dset)
        idx = self.np + 1
        shape = list(rawshape)
        shape.insert(0, idx)
        dset.resize(shape)

    def _shape(self, dataset):
        raise NotImplementedError('Derived class must implement _shape(dset)')

    def _calcData(self, dataset):
        raise NotImplementedError('Derived class must implement '
                                  '_calcData(dset)')


class NXExternalLink(NexusElementBase):
    """This element creates an external link into another file."""
    def __init__(self, filename, objpath):
        self.filename = filename
        self.objpath = objpath
        NexusElementBase.__init__(self)

    def create(self, name, h5parent, sinkhandler):
        self._link_created = False

    def update(self, name, h5parent, sinkhandler, values):
        if not self._link_created:
            try:
                h5parent[name] = h5py.ExternalLink(self.filename, self.objpath)
                self._link_created = True
            except Exception as e:
                session.log.warning('Failed to create external link: %s', e)
                # Ignore and retry: the external file may not yet exist

    def test_written(self, name, h5obj):
        if not self._link_created:
            session.log.warning('Failed to create external link into %s, '
                                'path %s', self.filename, self.objpath)
        try:
            h5obj[name]
        except KeyError:
            session.log.warning('Failed to create external link into %s, '
                                'path %s', self.filename, self.objpath)
