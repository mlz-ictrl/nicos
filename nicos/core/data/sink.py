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

"""Base classes for NICOS data sinks."""

from gzip import GzipFile as StdGzipFile
from io import TextIOWrapper
from os import path

from nicos import session
from nicos.core.constants import POINT, SIMULATION
from nicos.core.data.dataset import SETTYPES
from nicos.core.device import Device
from nicos.core.errors import ProgrammingError
from nicos.core.params import INFO_CATEGORIES, Override, Param, listof, setof
from nicos.core.status import statuses
from nicos.utils import File, enableDisableFileItem


class DataFileBase:
    """Base class for Nicos data files."""

    def __init__(self, shortpath, filepath):
        if path.isfile(filepath):
            raise ProgrammingError('Data file named %r already exists! '
                                   'Check filename templates!' % filepath)
        self.shortpath = shortpath
        self.filepath = filepath


class DataFile(DataFileBase, File):
    """Represents a Nicos data file."""

    def __init__(self, shortpath, filepath, filemode=None, logger=None):
        DataFileBase.__init__(self, shortpath, filepath)
        File.__init__(self, filepath, 'wb')
        self._log = logger
        self._filemode = filemode

    def close(self):
        File.close(self)
        if self._filemode is not None:
            enableDisableFileItem(self.filepath, self._filemode,
                                  logger=self._log)


class GzipFile(DataFileBase, StdGzipFile):

    def __init__(self, shortpath, filepath):
        DataFileBase.__init__(self, shortpath, filepath)
        StdGzipFile.__init__(self, filepath, 'wb')


class DataSinkHandler:
    """Handles sink operations for a single dataset, and in the case of point
    datasets, a single detector.

    The individual methods are called by the data manager, for each active
    handler in turn.  The default implementation does nothing, and does not
    need to be called in derived classes.

    The constructor saves the datasink device as ``self.sink``, the dataset as
    ``self.dataset``, and the detector (or ``None``) as ``self.detector``.
    There is also a logger present as ``self.log``.
    """

    ordering: int = 50
    """Used when calling all handlers from a dataset. This is used to be able
    to call certain handlers before/after others. A lower value means that the
    handler comes sooner than handlers with higher numbers.
    Conventional range: 1 - 100
    Default: 50"""

    def __init__(self, sink, dataset, detector):
        """Prepare `DataSinkHandler` for writing this `dataset`."""
        self.log = sink.log
        self.sink = sink
        self.dataset = dataset
        self.detector = detector
        self.manager = session.experiment.data

    def getParent(self, settype):
        """Get the parent dataset handler of the given settype, if one
        exists, or None.
        """
        res = (handler
               for subset in self.manager.iterParents(self.dataset, settype)
               for handler in subset.handlers
               if handler.sink is self.sink
               and handler.detector is self.detector)
        return next(res, None)

    def prepare(self):
        """Prepare writing this dataset.

        This is usually the place to assign the file counter with the data
        manager's `assignCounter()` and request a file with `createDataFile()`.
        If a file should only be created when actual data to save is present,
        you can defer this to `putResults` or `putMetainfo`.
        """

    def begin(self):
        """Begin writing this dataset.

        This is called immediately after `prepare`, but after *all* sink
        handlers have been prepared.  Therefore, the method can use the
        filenames requested from all sinks on ``self.dataset.filenames``.
        """

    def putMetainfo(self, metainfo):
        """Called for point datasets when the dataset metainfo is updated.

        Argument *metainfo* contains the new metainfo.
        ``self.dataset.metainfo`` contains the full metainfo.

        The *metainfo* is a dictionary in this form:

        * key: ``(devname, paramname)``
        * value: ``(value, stringified value, unit, category)``

        where the category is one of the keys defined in
        `nicos.core.params.INFO_CATEGORIES`.
        """

    def putValues(self, values):
        """Called for datasets when device values are updated.

        The *values* parameter is a dictionary with device names as keys and
        ``(timestamp, value)`` as values.

        ``self.dataset.values`` contains all values collected so far.  You can
        also use ``self.dataset.valuestats`` which is a dictionary with more
        statistics of the values over the whole duration of the dataset in the
        form ``(average, stdev, minimum, maximum)``.
        """

    def putResults(self, quality, results):
        """Called for point datasets when measurement results are updated.

        The *quality* is one of the constants defined in `nicos.core`:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data that has been read after the counting was
          interrupted by an exception.

        Argument *results* contains the new results.  ``self.dataset.results``
        contains all results so far.

        The *results* parameter is a dictionary with device names as keys and
        ``(scalarvalues, arrays)`` as values.
        """

    def addSubset(self, subset):
        """Called when a new subset of the sink's dataset is finished.

        This is the usual place in a scan handler to react to points measured
        during the scan.
        """

    def end(self):
        """Finish up the dataset (close files etc.).

        This method is called on all sinks participating in a dataset, even if
        an error occurred during data collection or even initialization.

        Therefore, the method cannot expect that even its own `prepare()` has
        been called successfully.
        """


class NicosMetaWriterMixin:

    update_headerinfo = False

    def _collectMetaInformation(self, update_headerinfo=None):
        bycategory = {}
        metainfo = self.dataset.metainfo
        for (device, key), info in metainfo.items():
            if info.category:
                bycategory.setdefault(info.category, []).append(
                    ('%s_%s' % (device, key),
                     (info.strvalue + ' ' + info.unit).strip()))
        if update_headerinfo is None:
            update_headerinfo = getattr(self.sink, 'update_headerinfo',
                                        self.update_headerinfo)
        if update_headerinfo:
            # put count result in its own category: 'result'
            # note: status may need to be updated manually as it is not
            #       collected in the values :(
            # note2: as we may be called during counting, some devices
            #        may be busy: this may irritate users :(
            bycategory['result'] = results = []
            for devname, val in list(self.dataset.values.items()):
                device = session.getDevice(devname)
                if (devname, 'value') in metainfo:
                    # re-use the category
                    category = metainfo[(devname, 'value')].category
                else:
                    category = 'result'
                bycategory.setdefault(category, []).append(
                    ('%s_value' % devname, device.format(val, True).strip()))
                # refresh status as well
                stat = device.status()
                # also map stat[0] to a string
                if stat[1]:
                    stat = ('%s_status' % devname, ('%s: %s' % (
                        statuses[stat[0]].lower(), stat[1].strip())))
                else:
                    stat = ('%s_status' % devname, statuses[stat[0]].lower())
                bycategory[category].append(stat)
        # collect countresults (if already existing)
        if self.dataset.results:
            bycategory['result'] = results = []
            for detname, detvalue in zip(self.dataset.detvalueinfo,
                                         self.dataset.detvaluelist):
                results.append((detname.name, str(detvalue)))
        return bycategory

    def writeMetaInformation(self, fp, title='Device snapshot',
                             update_headerinfo=None):
        """utility method for writing a standard nicos header

        to be used by derived sinks"""
        bycategory = self._collectMetaInformation(update_headerinfo)
        wrapper = TextIOWrapper(fp, encoding='utf-8')
        wrapper.write('### NICOS %s V2.0\n' % title)
        for category, catname in INFO_CATEGORIES:
            if category not in bycategory:
                continue
            wrapper.write('### %s\n' % catname)
            for key, value in sorted(bycategory[category]):
                wrapper.write('%25s : %s\n' % (key, value))
        # to ease interpreting the data...
        # note: arraydesc exists only for ImageSinks
        if hasattr(self, '_arraydesc'):
            wrapper.write('\n%r' % self._arraydesc)
        wrapper.write('\n')
        wrapper.detach()


class DataSink(Device):
    """The base class for data sinks.

    Each sink represents one way of processing incoming data.

    This is a device to be instantiated once per setup so that it can be
    configured easily through NICOS setups.  Actual processing is done by a
    `DataSinkHandler` class, of which one or more instances are created for
    each dataset that is processed with this sink.

    Usually, sinks are specific to a certain type of dataset (e.g. points or
    scans) and therefore override the `settypes` parameter with a default value
    that reflects this.

    .. attribute:: handlerclass

       This class attribute must be set by subclasses.  It selects the subclass
       of `.DataSinkHandler` that is to be used for handling datasets with this
       sink.

    .. attribute:: activeInSimulation

       This is a class attribute that selects whether this sink can be used in
       simulation mode.  This should only be true for sinks that write no data,
       such as a "write scan data to the console" sink.

    .. automethod:: isActive
    """

    parameters = {
        'detectors': Param('List of detector names to activate this sink '
                           '(default is always activated)', type=listof(str)),
        'settypes':  Param('List of dataset types to activate this sink '
                           '(default is for all settypes the sink supports)',
                           type=setof(*SETTYPES)),
    }

    parameter_overrides = {
        'visibility': Override(default=()),
    }

    # Set to true in subclasses that are safe for simulation.
    activeInSimulation = False

    # Set this to the corresponding Handler class.
    handlerclass = None

    def isActive(self, dataset):
        """Should return True if the sink can and should process this dataset.

        The default implementation, which should always be called in overrides,
        checks for simulation mode and for a match with the settypes and the
        detectors selected by the respective parameters.

        Derived classes can add additional checks, such as the dataset
        producing an array that can be written to an image file.
        """
        if session.mode == SIMULATION and not self.activeInSimulation:
            return False
        if self.settypes and dataset.settype not in self.settypes:
            return False
        if self.detectors and \
           not ({d.name for d in dataset.detectors} & set(self.detectors)):
            return False
        return True

    def createHandlers(self, dataset):
        """Start processing the given dataset (a BaseDataset).

        Creates the corresponding DataSinkHandler instances to use for this
        dataset determined via `handlerclass` and returns them.
        """
        if self.handlerclass is None:
            raise NotImplementedError('Must set an "handlerclass" attribute '
                                      'on %s' % self.__class__)
        # pylint: disable=not-callable
        if dataset.settype == POINT:
            dets = {d.name for d in dataset.detectors}
            if self.detectors:
                dets &= set(self.detectors)
            return [self.handlerclass(self, dataset, session.getDevice(det))
                    for det in dets]
        else:
            return [self.handlerclass(self, dataset, None)]
