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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Dataset classes."""

from collections import namedtuple
from math import sqrt
from threading import Lock
from time import localtime, time as currenttime
from uuid import uuid4

from nicos.core.acquire import DevStatistics
from nicos.core.constants import BLOCK, POINT, SCAN, SUBSCAN, UNKNOWN
from nicos.core.errors import ProgrammingError
from nicos.utils import lazy_property, number_types

SETTYPES = (POINT, SCAN, SUBSCAN, BLOCK)


Statistics = namedtuple('Statistics', ['mean', 'stddev', 'min', 'max'])


class finish_property(lazy_property):
    """A property which will not change after its owner's trigger flag
    has been set"""

    def __get__(self, obj, obj_class):
        if obj is None:
            return obj

        result = self._func(obj)

        if obj.finished:
            obj.__dict__[self.__name__] = result
        return result


class BaseDataset:
    """Base class for scan and point datasets."""

    settype = UNKNOWN
    countertype = UNKNOWN

    def __init__(self, **kwds):
        # Unique id of the scan.
        self.uid = uuid4()

        # Counter numbers assigned to the dataset, starting at 1.
        # This is set only when assignCounter() is called, i.e. when a file is
        # actually about to be written.
        self.counter = 0
        self.propcounter = 0
        self.samplecounter = 0

        # Counter relative to the parent dataset, starting at 1.  This is
        # always set by the data manager (if there is a parent).
        self.number = 0

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

        # Latest values of "interesting" devices.
        self.values = {}
        # More stats about "interesting" devices (to allow statistics).
        self._valuestats = {}
        # Values of "interesting" devices taken at a "canonical time".
        # Used as *the* position for scanned over devices.
        self.canonical_values = {}

        # Subsets of this dataset.  (Empty for point datasets.)
        self.subsets = []

        # Sink handlers involved in this dataset.
        self.handlers = []

        # A user-defined "info string" for this dataset.
        self.info = ''

        # A lock to suppress updates to valuestats from the cacheCallback in
        # the datamanager
        self._statslock = Lock()

        self.__dict__.update(kwds)

    def _addvalues(self, values):
        with self._statslock:
            for devname, (timestamp, value) in values.items():
                self.values[devname] = value
                if timestamp is None:
                    self.canonical_values[devname] = value
                    continue
                elif isinstance(value, number_types):
                    # collect statistics
                    current = self._valuestats.setdefault(devname, [])
                    if not current:
                        # first value: record timestamp and value
                        current.extend([0, 0, 0, value, value, timestamp, value])
                    else:
                        oldtime, oldvalue = current[-2:]
                        dt = timestamp - oldtime
                        if dt >= 0:
                            current[0] += dt  # t0
                            current[1] += dt * oldvalue  # t1
                            current[2] += dt * oldvalue ** 2  # t2
                            current[3] = min(current[3], value)  # mini
                            current[4] = max(current[4], value)  # maxi
                            current[5] = timestamp  # _
                            current[6] = value  # lastv

                    # mean = t1 / t0
                    # stdev = sqrt(abs(t2 / t0 - t1 ** 2 / t0 ** 2))

    @property
    def valuestats(self):
        """Value statistics.

        The value statistics is a dictionary where the key is the device name
        and the value is a tuple of mean value, standard deviation, minimum
        value and maximum value.
        """
        res = {}
        with self._statslock:
            for devname, (t0, t1, t2,
                          mini, maxi, _, lastv) in self._valuestats.items():
                if t0 > 0:
                    mean = t1 / t0
                    stdev = sqrt(abs(t2 / t0 - t1 ** 2 / t0 ** 2))
                else:
                    mean = lastv
                    stdev = float('inf')
                res[devname] = Statistics(mean, stdev, mini, maxi)
        return res

    def __str__(self):
        return '<%s dataset %s..%s>' % (self.settype, str(self.uid)[:3],
                                        str(self.uid)[-3:])

    def __getstate__(self):
        # Pickling support: remove sink handler instances that likely contain
        # data that cannot be pickled, such as file objects.
        state = self.__dict__.copy()
        state.pop('handlers', None)
        state.pop('_statslock', None)
        return state

    def dispatch(self, method, *args):
        """Dispatch calling 'method' to all sink handlers."""
        for handler in self.handlers:
            getattr(handler, method)(*args)

    def trimResult(self):
        """Trim objects that are not required to be kept after finish()."""
        del self.handlers[:]

    @lazy_property
    def devvalueinfo(self):
        """Device value info list."""
        return sum((dev.valueInfo() for dev in self.devices), ())

    @lazy_property
    def envvalueinfo(self):
        """Environment value info list."""
        return sum((dev.valueInfo() for dev in self.environment), ())

    @lazy_property
    def detvalueinfo(self):
        """Detector value info."""
        return sum((dev.valueInfo() for dev in self.detectors), ())


class PointDataset(BaseDataset):
    """Collects data related to a single count/measurement."""

    settype = POINT
    countertype = POINT

    def __init__(self, **kwds):
        # Point results: values of detectors.
        self.results = {}

        #: Instrument metainfo ("header data").
        #: A dictionary of (devname, key) -> (value, str_value, unit, category).
        #: Keys are usually parameters or 'value', 'status'.
        self.metainfo = {}

        BaseDataset.__init__(self, **kwds)

    def _reslist(self, devices, resdict, index=-1):
        ret = []
        stats = None
        for dev in devices:
            if isinstance(dev, DevStatistics):
                if stats is None:
                    stats = self.valuestats
                val = dev.retrieve(stats)
            else:
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
        for (key, value) in self.results.items():
            if value is not None:
                self.results[key] = (value[0], [])

    @finish_property
    def devvaluelist(self):
        """List of all device values.

        The order of the values is the same as in the ``devvalueinfo`` list, so
        a mapping between device and value can be made.
        """
        return self._reslist(self.devices, self.canonical_values)

    @finish_property
    def envvaluelist(self):
        """List of values of all devices in the ``session.experiment.envlist`` list.

        The order of the values is the same as in the ``envvalueinfo`` list, so
        a mapping between environment device and value can be made.
        """
        return self._reslist(self.environment, self.values)

    @finish_property
    def detvaluelist(self):
        """List of values of all devices in the ``session.experiment.detectors`` list.

        The order of the values is the same as in the ``detvalueinfo`` list, so
        a mapping between detector device and value can be made.
        """
        return self._reslist(self.detectors, self.results, 0)


class ScanDataset(BaseDataset):
    """Collects data related to a scan (sequence of measurements)."""

    settype = SCAN
    countertype = SCAN

    def __init__(self, **kwds):
        # Number of points in the scan, if known.
        self.npoints = None

        # Index of the X value to plot.
        self.xindex = 0

        # If this is a chained dataset, the UIDs of the continued ones.
        self.chain = []
        self.chain_direction = 0

        BaseDataset.__init__(self, **kwds)

    def trimResult(self):
        """Trim objects that are not required to be kept after finish()."""
        BaseDataset.trimResult(self)
        # keep only valuelists in all points but the first (which serves as
        # metadata for the scan)
        for subset in self.subsets[1:]:
            if isinstance(subset, PointDataset):
                # create the lazy properties if not yet done
                # pylint: disable=pointless-statement
                (subset.devvaluelist, subset.envvaluelist, subset.detvaluelist)
                # clear all other data
                for d in (subset.metainfo, subset.values, subset._valuestats,
                          subset.canonical_values, subset.results):
                    d.clear()

    @property
    def metainfo(self):
        """The metainfo is the same as for the first datapoint or subscan."""
        if not self.subsets:
            raise ProgrammingError('metainfo is not available without points')
        return self.subsets[0].metainfo

    @property
    def devvaluelists(self):
        """List of all subset devvaluelist. """
        return [subset.devvaluelist for subset in self.subsets
                if subset.finished]

    @property
    def envvaluelists(self):
        """List of all subset envvaluelist. """
        return [subset.envvaluelist for subset in self.subsets
                if subset.finished]

    @property
    def detvaluelists(self):
        """List of all subset detvaluelist. """
        return [subset.detvaluelist for subset in self.subsets
                if subset.finished]


class SubscanDataset(ScanDataset):
    """Collects data related to a subscan (scan within a scan with results)."""

    settype = SUBSCAN
    countertype = SCAN


class BlockDataset(BaseDataset):
    """Collects data related to a whole (multi-scan) block of an experiment."""

    settype = BLOCK
    countertype = BLOCK

    def __init__(self, **kwds):
        BaseDataset.__init__(self, **kwds)


class ScanData:
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
    # chaining info
    chain = ''
    # value info
    xvalueinfo = []
    yvalueinfo = []
    # storage for header info
    # XXX(dataapi): convert to new metainfo format
    headerinfo = {}
    # resulting x and y values
    xresults = []
    yresults = []

    def __init__(self, dataset=None):
        """Create this simple set from the ScanDataset *dataset*."""
        if dataset is None:
            self.uid = str(uuid4())
            self.started = localtime()
            self.filepaths = []
            self.xvalueinfo = []
            self.yvalueinfo = []
            self.headerinfo = {}
            self.xresults = []
            self.yresults = []
        else:
            self.uid = str(dataset.uid)
            self.started = localtime(dataset.started)
            self.scaninfo = dataset.info
            self.counter = dataset.counter
            self.filepaths = dataset.filepaths
            self.xindex = dataset.xindex
            self.envvalues = len(dataset.envvalueinfo)
            self.chain = ','.join(str(uid) for uid in dataset.chain)
            self.xvalueinfo = dataset.devvalueinfo + dataset.envvalueinfo
            self.yvalueinfo = dataset.detvalueinfo

            # convert result points to result lists (no arrays)
            self.xresults = [subset.devvaluelist + subset.envvaluelist
                             for subset in dataset.subsets]
            self.yresults = dataset.detvaluelists

            # convert metainfo to headerinfo
            self.headerinfo = {}
            if dataset.subsets:
                for (devname, key), info in \
                        dataset.metainfo.items():
                    if len(info.strvalue) > 100:  # omit large values
                        continue
                    catlist = self.headerinfo.setdefault(info.category, [])
                    catlist.append(
                        (devname, key, (info.strvalue + ' ' + info.unit).strip()))

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
