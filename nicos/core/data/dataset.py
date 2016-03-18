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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Dataset classes."""

from math import sqrt
from time import time as currenttime, localtime
from uuid import uuid4

from nicos.core.errors import ProgrammingError
from nicos.pycompat import iteritems
from nicos.utils import lazy_property


SETTYPES = ('point', 'scan', 'subscan', 'block')


class BaseDataset(object):
    """Base class for scan and point datasets."""

    settype = 'unknown'
    countertype = 'unknown'

    def __init__(self, **kwds):
        # Unique id of the scan.
        self.uid = uuid4()

        # Counter number assigned to the dataset.
        self.counter = 0

        # Short and absolute filename(s) assigned to the dataset.
        self.filenames = []
        self.filepaths = []

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

        # Preset for this dataset.
        self.preset = {}

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

    # XXX(dataapi): these are tuples, should they be lists?

    def trimResult(self):
        """Trim objects that are not required to be kept after finish()."""
        del self.handlers[:]

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

    def trimResult(self):
        """Trim objects that are not required to be kept after finish()."""
        BaseDataset.trimResult(self)
        # remove arrays from memory in cached datasets
        for (key, (reads, _)) in iteritems(self.results):
            self.results[key] = (reads, [])

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

        # Index of the X value to plot.
        self.xindex = 0

        # If this is a continuation dataset, the UIDs of the continued ones.
        self.continuation = []
        self.cont_direction = 0

        BaseDataset.__init__(self, **kwds)

    @property
    def metainfo(self):
        # The metainfo is the same as for the first datapoint / subscan.
        if not self.subsets:
            raise ProgrammingError('metainfo is not available without points')
        return self.subsets[0].metainfo

    @property
    def devvaluelists(self):
        return [subset.devvaluelist for subset in self.subsets]

    @property
    def envvaluelists(self):
        return [subset.envvaluelist for subset in self.subsets]

    @property
    def detvaluelists(self):
        return [subset.detvaluelist for subset in self.subsets]


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


class ScanData(object):
    """Simplified object containing scan data for serialized transfer to the
    GUI/ELog.
    """
    # unique id as a string
    uid = ''
    # start time
    started = 0
    # scan info
    scaninfo = ''
    # assigned number
    counter = 0
    # file name(s)
    filepaths = []
    # index of the x value to use for plotting
    xindex = 0
    # number of env. values
    envvalues = 0
    # continuation info
    continuation = ''
    # value info
    xvalueinfo = []
    yvalueinfo = []
    # storage for header info
    # XXX(dataapi): convert to new metainfo format
    headerinfo = {}
    # resulting x and y values
    xresults = []
    yresults = []

    def __init__(self, dataset):
        """Create this simple set from the ScanDataset *dataset*."""
        self.uid = str(dataset.uid)
        self.started = localtime(dataset.started)
        self.scaninfo = dataset.info
        self.counter = dataset.counter
        self.filepaths = dataset.filepaths
        self.xindex = dataset.xindex
        self.envvalues = len(dataset.envvalueinfo)
        self.continuation = ','.join(str(uid) for uid in dataset.continuation)
        self.xvalueinfo = dataset.devvalueinfo + dataset.envvalueinfo
        self.yvalueinfo = dataset.detvalueinfo

        # convert result points to result lists (no arrays)
        self.xresults = [subset.devvaluelist + subset.envvaluelist
                         for subset in dataset.subsets]
        self.yresults = dataset.detvaluelists

        # convert metainfo to headerinfo
        self.headerinfo = {}
        for (devname, key), (_, val, unit, category) in \
                iteritems(dataset.metainfo):
            catlist = self.headerinfo.setdefault(category, [])
            catlist.append((devname, key, (val + ' ' + unit).strip()))

    # info derived from valueinfo
    @lazy_property
    def xnames(self):
        return [v.name for v in self.xvalueinfo]

    @lazy_property
    def xunits(self):
        return [v.unit for v in self.xvalueinfo]

    @lazy_property
    def ynames(self):
        return [v.name for v in self.yvalueinfo]

    @lazy_property
    def yunits(self):
        return [v.unit for v in self.yvalueinfo]
