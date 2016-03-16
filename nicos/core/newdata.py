#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Data handling classes, new API."""

import logging
import os
from math import sqrt
from os import path
from time import time as currenttime
from uuid import uuid4

from nicos import session
from nicos.core.constants import SIMULATION
from nicos.core.device import Device
from nicos.core.errors import ProgrammingError
from nicos.core.params import Param, listof
from nicos.core.utils import DeviceValueDict
from nicos.pycompat import iteritems, string_types
from nicos.utils import DEFAULT_FILE_MODE, lazy_property, readFileCounter, \
    updateFileCounter


LIVE = 'live'
INTERMEDIATE = 'intermediate'
FINAL = 'final'
INTERRUPTED = 'interrupted'


class BaseDataset(object):
    """Base class for scan and point datasets."""

    settype = 'unknown'
    countertype = 'unknown'

    def __init__(self, **kwds):
        # Unique id of the scan.
        self.uid = uuid4()

        # Counter number assigned to the dataset.
        self.counter = None

        # Filename(s) assigned to the dataset.
        self.filenames = []

        # (Approximate) timestamps for the point, good for cache queries.
        self.started = currenttime()  # Can be refined later.
        self.finished = None

        # Which varying devices are important for this dataset.
        self.devices = []

        # Which environment devices are important for this dataset.
        # (XXX: for block datasets, what to do when envlist changes?)
        self.environment = []

        # Which detectors were involved in measuring this dataset.
        # (XXX: for block datasets, SetDetectors should finish the set.)
        self.detectors = []

        # Subsets of this dataset.  (Empty for point datasets.)
        self.subsets = []

        # Sink handlers involved in this dataset.
        self.handlers = []

        # A user-defined "info string" for this dataset.
        self.info = ''

        self.__dict__.update(kwds)

    def __str__(self):
        return '<%s dataset %s..%s>' % (self.settype, str(self.uid)[:3],
                                        str(self.uid)[-3:])

    def __getstate__(self):
        # Pickling support: remove sink handler instances that likely contain
        # data that cannot be pickled, such as file objects.
        state = self.__dict__.copy()
        state.pop('handlers', None)
        return state

    def dispatch(self, method, *args):
        """Dispatch calling 'method' to all sink handlers."""
        for handler in self.handlers:
            getattr(handler, method)(*args)

    @lazy_property
    def devvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.devices), ())

    @lazy_property
    def envvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.environment), ())

    @lazy_property
    def detvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.detectors), ())

    @lazy_property
    def detarrayinfo(self):
        return sum((dev.arrayInfo() for dev in self.detectors), ())


class PointDataset(BaseDataset):
    """Collects data related to a single count/measurement."""

    settype = 'point'
    countertype = 'point'

    def __init__(self, **kwds):
        # Point number within a scan.
        self.pointnumber = None

        # Point results: values of detectors.
        self.results = {}

        # Values of "interesting" devices (time series).
        self.values = {}
        self._valuestats = {}

        # Instrument metainfo ("header data").
        # A dictionary of (device, key) -> (value, str_value, unit, category).
        # keys are usually parameters or 'value', 'status'.
        self.metainfo = {}

        BaseDataset.__init__(self, **kwds)

    def _addvalues(self, values):
        for devname, (timestamp, value) in iteritems(values):
            if isinstance(value, float):
                # collect statistics
                current = self._valuestats.setdefault(devname, [])
                if not current:
                    # first value: record timestamp and value
                    current.extend([0, 0, 0, value, value, timestamp, value])
                else:
                    oldtime, oldvalue = current[-2:]
                    dt = timestamp - oldtime
                    current[0] += dt
                    current[1] += dt * oldvalue
                    current[2] += dt * oldvalue ** 2
                    current[3] = min(current[3], value)
                    current[4] = max(current[4], value)
                    current[5] = timestamp
                    current[6] = value
            self.values[devname] = value

    def _reslist(self, devices, resdict, index=-1):
        ret = []
        for dev in devices:
            val = resdict.get(dev.name, None)
            if val is not None and index > -1:
                val = val[index]
            if isinstance(val, list):
                ret.extend(val)
            else:
                ret.append(val)
        return ret

    @property
    def valuestats(self):
        res = {}
        for devname in self._valuestats:
            t0, t1, t2, mini, maxi, _, lastv = self._valuestats[devname]
            if t0 > 0:
                mean = t1 / t0
                stdev = sqrt(abs(t2 / t0 - t1 ** 2 / t0 ** 2))
            else:
                mean = lastv
                stdev = float('inf')
            res[devname] = mean, stdev, mini, maxi
        return res

    @lazy_property
    def devvaluelist(self):
        return self._reslist(self.devices, self.values)

    @lazy_property
    def envvaluelist(self):
        return self._reslist(self.environment, self.values)

    @lazy_property
    def detvaluelist(self):
        return self._reslist(self.detectors, self.results, 0)

    @lazy_property
    def detarraylist(self):
        return self._reslist(self.detectors, self.results, 1)


class ScanDataset(BaseDataset):
    """Collects data related to a scan (sequence of measurements)."""

    settype = 'scan'
    countertype = 'scan'

    def __init__(self, **kwds):
        # Number of points in the scan, if known.
        self.npoints = None

        BaseDataset.__init__(self, **kwds)

    @property
    def metainfo(self):
        # The metainfo is the same as for the first datapoint / subscan.
        if not self.subsets:
            raise ProgrammingError('metainfo is not available without points')
        return self.subsets[0].metainfo


class SubscanDataset(ScanDataset):
    """Collects data related to a subscan (scan within a scan with results)."""

    settype = 'subscan'
    countertype = 'scan'


class BlockDataset(BaseDataset):
    """Collects data related to a whole (multi-scan) block of an experiment."""

    settype = 'block'
    countertype = 'block'

    def __init__(self, **kwds):
        BaseDataset.__init__(self, **kwds)


class DataSinkHandler(object):
    """Handles sink operations for a single dataset."""

    def __init__(self, sink, dataset, detector):
        """Prepare `DataSinkHandler` for writing this `dataset`."""
        self.log = sink.log
        self.sink = sink
        self.dataset = dataset
        self.detector = detector

    #
    # DataSinkHandler API
    #

    def start(self):
        """Start writing this dataset."""

    def begin(self):
        """Run after sinks are all started."""

    def addMetainfo(self, metainfo):
        """Called when the dataset metainfo is updated.

        Argument *metainfo* contains the new metainfo.  ``dataset.metainfo``
        contains the full metainfo.
        """

    def addValues(self, values):
        """Called when device values are updated.

        XXX: document format of parameter.
        """

    def addResults(self, quality, results):
        """Called when the point dataset main results are updated.

        The *quality* is one of the constants defined in the module:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data that has been read after the counting was
          interrupted by an exception.

        Argument *results* contains the new results.  ``dataset.results``
        contains all results so far.
        """

    def addSubset(self, subset):
        """Called when a new subset of the sink's dataset is finished.
        """

    def finish(self):
        """Finish up writing this dataset."""

    def end(self):
        """Run after sinks are all finished."""

    def addAnalysis(self):
        """Add an after-measure analysis to the dataset.

        XXX: discuss if this is in the right place here.
        """


class DataSink(Device):
    """Class that represents one way of processing incoming data.

    This is a device to be instantiated once per setup so that it can be
    configured easily through NICOS setups.  Actual processing is done by a
    `DataSinkHandler` class, of which one instance is created per dataset.
    """

    parameters = {
        'detectors': Param('List of detector names to activate this sink '
                           '(default is always activated)', type=listof(str)),
        'settypes':  Param('List of dataset types to activate this sink '
                           '(default is for all settypes the sink supports)',
                           type=listof(str))  # XXX oneof(*SETTYPES)
    }

    # Set to true in subclasses that are safe for simulation.
    activeInSimulation = False

    # Set this to the corresponding Handler class.
    handlerclass = None

    def isActive(self, dataset):
        """Return True if the sink can and should process this dataset."""
        if session.mode == SIMULATION and not self.activeInSimulation:
            return False
        if self.settypes and dataset.settype not in self.settypes:
            return False
        if self.detectors and \
           not (set(d.name for d in dataset.detectors) & set(self.detectors)):
            return False
        return True

    def getHandlers(self, dataset):
        """Start processing the given dataset (a BaseDataset).

        Return the DataSinkHandler instances to use for this dataset.
        """
        if self.handlerclass is None:
            raise NotImplementedError('Must set an "handlerclass" attribute '
                                      'on %s' % self.__class__)
        dets = set(d.name for d in dataset.detectors)
        if self.detectors:
            dets &= set(self.detectors)
        # pylint: disable=not-callable
        return [self.handlerclass(self, dataset, session.getDevice(det))
                for det in dets]


class DataFile(file):
    """Represents a Nicos data file."""

    def __init__(self, shortpath, filepath):
        if path.isfile(filepath):
            raise ProgrammingError('Data file named %r already exists! '
                                   'Check filename templates!' % filepath)
        self.shortpath = shortpath
        self.filepath = filepath
        file.__init__(self, filepath, 'wb')


class DataManager(object):
    """Singleton class that manages incoming data.

    It takes all data that is produced by detectors and distributes it to sinks.
    """

    def __init__(self):
        # A stack of currently active datasets.  Maximum 3 depth.
        self._stack = []

    @lazy_property
    def log(self):
        logger = session.getLogger('nicos-data')  # XXX name?
        logger.setLevel(logging.INFO)  # XXX session.log.level)
        return logger

    @property
    def _current(self):
        """Current dataset on top of stack."""
        if self._stack:
            return self._stack[-1]

    def reset(self):
        """Cleanup and reset the current datasets."""
        self._clean()

    #
    # Adding and finishing up datasets
    #

    def beginBlock(self, **kwds):
        self._clean()
        dataset = BlockDataset(**kwds)
        return self._init(dataset)

    def beginScan(self, subscan=False, **kwds):
        if subscan:
            # a subscan can only start when a point is open
            self._clean(('point',))
            dataset = SubscanDataset(**kwds)
        else:
            self._clean(('block',))
            dataset = ScanDataset(**kwds)
        return self._init(dataset)

    def beginPoint(self, **kwds):
        self._clean(('block', 'scan', 'subscan'))
        if self._current:
            if 'devices' not in kwds:
                kwds['devices'] = self._current.devices
            if 'environment' not in kwds:
                kwds['environment'] = self._current.environment
            if 'detectors' not in kwds:
                kwds['detectors'] = self._current.detectors
            if self._current.settype in ('scan', 'subscan'):
                kwds['pointnumber'] = len(self._current.subsets) + 1
        dataset = PointDataset(**kwds)
        return self._init(dataset)

    def finishPoint(self):
        if self._current.settype != 'point':
            raise ProgrammingError('No point to finish')
        point = self._stack.pop()
        self._finish(point)

    def finishScan(self):
        if self._current.settype not in ('scan', 'subscan'):
            raise ProgrammingError('No scan to finish')
        scan = self._stack.pop()
        self._finish(scan)

    def _init(self, dataset):
        """Init dataset and put it on the stack"""
        self.log.debug('Created new dataset %s' % dataset)
        for sink in session.datasinks:
            if sink.isActive(dataset):
                handlers = sink.getHandlers(dataset)
                dataset.handlers.extend(handlers)
        if self._current:
            self._current.subsets.append(dataset)
        self._stack.append(dataset)
        dataset.dispatch('start')
        dataset.dispatch('begin')
        return dataset

    def _clean(self, upto=()):
        """Finish leftover datasets that aren't instances of *upto*."""
        while self._stack and self._stack[-1].settype not in upto:
            last = self._stack.pop()
            self.log.warning('Cleaning up %s from stack?!' % last)
            try:
                self._finish(last)
            except Exception:
                self.log.exception('while cleaning up dataset %s' % last)

    def _finish(self, dataset):
        """Finish up the dataset."""
        if dataset.finished is None:
            dataset.finished = currenttime()
        self.log.debug('Finishing up %s' % dataset)
        dataset.dispatch('finish')
        dataset.dispatch('end')
        if self._stack:
            self._stack[-1].dispatch('addSubset', dataset)

    #
    # Filling datasets with data
    #

    # XXX: consider putting this in the point dataset class itself
    # if the point object is available everywhere

    def putMetainfo(self, metainfo):
        if self._current.settype != 'point':
            self.log.warning('No current point dataset, ignoring metainfo')
            return
        self._current.metainfo.update(metainfo)
        self._current.dispatch('addMetainfo', metainfo)

    def putValues(self, values):
        if self._current.settype != 'point':
            self.log.warning('No current point dataset, ignoring values')
            return
        self._current._addvalues(values)
        self._current.dispatch('addValues', values)

    def putResults(self, quality, results):
        if self._current.settype != 'point':
            self.log.warning('No current point dataset, ignoring results')
            return
        self._current.results.update(results)
        self._current.dispatch('addResults', quality, results)

    def cacheCallback(self, key, value, time):
        if not self._current or self._current.settype != 'point':
            return
        devname = session.device_case_map[key.split('/')[0]]
        #print devname, time, value
        try:
            self.putValues({devname: (time, value)})
        except Exception:
            pass

    def updateMetainfo(self):
        # if updatedict is not empty, only update those devices & positions, else all
        if 0:  # pylint: disable=using-constant-test
            # XXX
            # devices = zip(*sorted(iteritems(updatedict),
            #               key=lambda dev_and_val: dev_and_val[0].name.lower()))[0]
            pass
        else:
            devices = zip(*sorted(iteritems(session.devices),
                                  key=lambda name_and_dev: name_and_dev[0].lower()))[1]
        newinfo = {}
        for device in devices:
            if device.lowlevel:
                continue
            for key, value, strvalue, unit, category in device.info():
                newinfo[device, key] = (value, strvalue, unit, category)
        self.putMetainfo(newinfo)

    #
    # Services for sinks
    #

    def assignCounter(self, dataset):
        """Assign a counter number to the dataset.

        Datasets have no number until one is explicitly assigned.  Assignment
        should only be requested when a file is actually written, so that
        measurements that don't write files don't increment numbers needlessly.

        This can be called multiple times on a dataset; it will return the
        already assigned counter.
        """
        if dataset.counter is not None:
            return dataset.counter
        if session.mode == SIMULATION:
            raise ProgrammingError('assignCounter should not be called in '
                                   'simulation mode')
        exp = session.experiment
        counterpath = path.join(exp.dataroot, exp.counterfile)
        nextnum = readFileCounter(counterpath, dataset.countertype) + 1
        updateFileCounter(counterpath, dataset.countertype, nextnum)
        dataset.counter = nextnum
        self.log.debug('%s now has number %d' % (dataset, nextnum))
        return nextnum

    def expandDataFile(self, dataset, nametemplate):
        """Determine the final data file name(s)."""
        if dataset.counter is None:
            raise ProgrammingError('expandDataFile: a counter number must be '
                                   'assigned to the dataset first')
        if isinstance(nametemplate, string_types):
            nametemplate = [nametemplate]
        # translate entries
        filenames = []
        for nametmpl in nametemplate:
            if '%(' in nametmpl:
                kwds = dict(session.experiment.propinfo)
                # get all parent counters into the keywords
                # i.e. blockcounter, scancounter, pointcounter
                for ds in self._stack:
                    kwds[ds.countertype + 'counter'] = ds.counter
                # XXX add experiment local counter if present
                # point number within the scan
                if hasattr(dataset, 'pointnumber'):
                    kwds['pointnumber'] = dataset.pointnumber
                try:
                    filename = nametmpl % DeviceValueDict(kwds)
                except KeyError as err:
                    raise KeyError('can\'t create datafile, illegal key %s in '
                                   'filename template %r!' % (err, nametmpl))
                except TypeError as err:
                    raise TypeError('error expanding data file name: %s, check '
                                    'filename template %r!' % (err, nametmpl))
            else:
                filename = nametmpl % dataset.counter
            filenames.append(filename)
        return filenames

    def createDataFile(self, dataset, nametemplate, *subdirs):
        """Creates and returns a file named according to the given nametemplate
        in the given subdir of the datapath.

        The nametemplate can be either a string or a list of strings.  In the
        second case, the first listentry is used to create the file and the
        remaining ones will be hardlinked to this file if the os supports this.
        """
        if session.mode == SIMULATION:
            raise ProgrammingError('createDataFile should not be called in '
                                   'simulation mode')
        exp = session.experiment
        filenames = self.expandDataFile(dataset, nametemplate)
        filename = filenames[0]
        linknames = filenames[1:]
        filepath = exp.getDataFilename(filename, *subdirs)

        shortpath = path.join(*subdirs + (filename,))
        dataset.filenames.append(shortpath)

        self.log.debug('creating file %r' % filename)
        datafile = DataFile(shortpath, filepath)
        if exp.managerights:
            os.chmod(filepath,
                     exp.managerights.get('enableFileMode', DEFAULT_FILE_MODE))
            # XXX add chown here?
        linkfunc = os.link if hasattr(os,  'link') else \
            os.symlink if hasattr(os, 'symlink') else None
        if linkfunc:
            for linkname in linknames:
                linkpath = exp.getDataFilename(linkname, *subdirs)
                self.log.debug('linking %r to %r' % (linkpath, filepath))
                try:
                    linkfunc(filepath, linkpath)
                except OSError:
                    self.log.warning('linking %r to %r failed, ignoring' %
                                     (linkpath, filepath))
        else:
            self.log.warning('can\'t link datafiles, no os support!')

        return datafile


# Create the singleton instance right now.
dataman = DataManager()
