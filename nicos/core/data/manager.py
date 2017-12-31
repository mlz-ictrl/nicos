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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""The global data manager class."""

import os
import logging
from os import path
from time import time as currenttime

from nicos import session
from nicos.core.constants import BLOCK, POINT, SCAN, SUBSCAN, SIMULATION
from nicos.core.errors import ProgrammingError
from nicos.core.utils import DeviceValueDict
from nicos.core.data.dataset import PointDataset, ScanDataset, \
    SubscanDataset, BlockDataset
from nicos.core.data.sink import DataFile
from nicos.pycompat import iteritems, string_types
from nicos.utils import DEFAULT_FILE_MODE, lazy_property, readFileCounter, \
    updateFileCounter


class DataManager(object):
    """Singleton device class that manages incoming data.

    It takes all data that is produced by detectors, as well as device values
    and metadata, and distributes it to data sinks.
    """

    def __init__(self):
        # A stack of currently active datasets.  Maximum 3 depth.
        self._stack = []

        # Last finished scans.  Stored for analysis purposes.
        self._last_scans = []

    @lazy_property
    def log(self):
        logger = session.getLogger('nicos-data')
        logger.setLevel(logging.INFO)
        return logger

    @property
    def _current(self):
        """Current dataset on top of stack."""
        if self._stack:
            return self._stack[-1]

    def reset(self):
        """Cleanup and reset the current datasets."""
        self._clean()

    def reset_all(self):
        """Cleanup and reset the current datasets as well as stored scans."""
        self.reset()
        self._last_scans = []

    #
    # Adding and finishing up datasets
    #

    def beginBlock(self, **kwds):
        self._clean()
        dataset = BlockDataset(**kwds)
        return self._init(dataset)

    def beginScan(self, subscan=False, **kwds):
        """Create and begin a new scan dataset."""
        if subscan:
            # a subscan can only start when a point is open
            self._clean((POINT,))
            dataset = SubscanDataset(**kwds)
        else:
            self._clean((BLOCK,))
            dataset = ScanDataset(**kwds)
        dataset = self._init(dataset)
        # XXX: when to clean these up?
        self._last_scans.append(dataset)
        return dataset

    def _updatePointKeywords(self, kwds):
        """If a scan is currently on the stack, apply the relevant devices
        from the scan to the keywords for creating a point dataset.
        """
        if self._current:
            if 'devices' not in kwds:
                kwds['devices'] = self._current.devices
            if 'environment' not in kwds:
                kwds['environment'] = self._current.environment
            if 'detectors' not in kwds:
                kwds['detectors'] = self._current.detectors

    def beginPoint(self, **kwds):
        """Create and begin a new point dataset."""
        self._clean((BLOCK, SCAN, SUBSCAN))
        self._updatePointKeywords(kwds)
        dataset = PointDataset(**kwds)
        return self._init(dataset)

    def beginTemporaryPoint(self, **kwds):
        """Create and begin a point dataset that does not use datasinks."""
        self._clean((BLOCK, SCAN, SUBSCAN))
        self._updatePointKeywords(kwds)
        dataset = PointDataset(**kwds)
        return self._init(dataset, skip_handlers=True)

    def finishPoint(self):
        """Finish the current point dataset."""
        if self._current.settype != POINT:
            self.log.warning('no data point to finish here')
            return
        point = self._stack.pop()
        self._finish(point)

    def finishScan(self):
        """Finish the current scan dataset."""
        if self._current.settype not in (SCAN, SUBSCAN):
            self.log.warning('no scan to finish here')
            return
        scan = self._stack.pop()
        self._finish(scan)

    def finishBlock(self):
        """Finish the current block dataset."""
        if self._current.settype != BLOCK:
            self.log.warning('no block to finish here')
            return
        block = self._stack.pop()
        self._finish(block)

    def _init(self, dataset, skip_handlers=False):
        """Initialize the dataset and put it on the stack.

        Finally dispatches corresponding sink handlers.
        """
        self.log.debug('Created new dataset %s', dataset)
        if not skip_handlers:
            for sink in session.datasinks:
                if sink.isActive(dataset):
                    handlers = sink.createHandlers(dataset)
                    dataset.handlers.extend(handlers)
        if self._current:
            self._current.subsets.append(dataset)
            dataset.number = len(self._current.subsets)
        self._stack.append(dataset)
        dataset.dispatch('prepare')
        dataset.dispatch('begin')
        return dataset

    def _clean(self, upto=()):
        """Finish leftover datasets that aren't instances of *upto*."""
        while self._stack and self._stack[-1].settype not in upto:
            last = self._stack.pop()
            self.log.warning('Cleaning up %s from stack?!', last)
            try:
                self._finish(last)
            except Exception:
                self.log.exception('while cleaning up dataset %s', last)

    def _finish(self, dataset):
        """Finish up the dataset."""
        if dataset.finished is None:
            dataset.finished = currenttime()
        self.log.debug('Finishing up %s', dataset)
        dataset.dispatch('end')
        if self._stack:
            self._stack[-1].dispatch('addSubset', dataset)
        dataset.trimResult()

    #
    # Filling datasets with data
    #

    def putMetainfo(self, metainfo):
        """Put some metainfo into the topmost (point) dataset.

        *metainfo* is a dictionary of the form ``{(devname, param):
        (rawvalue, strvalue, unit, category)}``.
        """
        if self._current.settype != POINT:
            self.log.warning('No current point dataset, ignoring metainfo')
            return
        self._current.metainfo.update(metainfo)
        self._current.dispatch('putMetainfo', metainfo)

    def putValues(self, values):
        """Put some values into the topmost (point) dataset.

        *values* is a dictionary of the form ``{devname: (timestamp, value)}``.

        If *timestamp* is None, this value is the "canonical" position of the
        device for the point.
        """
        if self._current.settype != POINT:
            self.log.warning('No current point dataset, ignoring values')
            return
        self._current._addvalues(values)
        self._current.dispatch('putValues', values)

    def putResults(self, quality, results):
        """Put some detector results into the topmost (point) dataset.

        *quality* is one of the data quality constants from
        :mod:`nicos.core.constants`, i.e. `LIVE`, `INTERMEDIATE`, `FINAL`,
        `INTERRUPTED`.

        *results* is a dictionary with the form
        ``{devname: (readvalue, arrays)}``.
        """
        if self._current.settype != POINT:
            self.log.warning('No current point dataset, ignoring results')
            return
        self._current.results.update(results)
        self._current.dispatch('putResults', quality, results)

    def updateMetainfo(self):
        """Utility function to gather metainfo from all relevant devices and
        write it to the current dataset with `putMetainfo`.

        Relevant devices are (currently) those that are not lowlevel.
        """
        devices = [dev for (_, dev) in
                   sorted(iteritems(session.devices),
                          key=lambda name_dev: name_dev[0].lower())]
        newinfo = {}
        for device in devices:
            if device.lowlevel:
                continue
            for key, value, strvalue, unit, category in device.info():
                newinfo[device.name, key] = (value, strvalue, unit, category)
        self.putMetainfo(newinfo)

    def cacheCallback(self, key, value, time):
        if (not self._current or self._current.settype != POINT
            or self._current.finished is not None):
            return
        devname = session.device_case_map.get(key.split('/')[0])
        if devname is not None:
            try:
                self.putValues({devname: (time, value)})
            except Exception:
                pass

    #
    # Services for sinks
    #

    def assignCounter(self, dataset):
        """Assign counter numbers to the dataset.

        Datasets have no numbers until one is explicitly assigned.  Assignment
        should only be requested when a file is actually written, so that
        measurements that don't write files don't increment numbers needlessly.

        This can be called multiple times on a dataset; the counter will only
        be increased and assigned once.
        """
        if dataset.counter != 0:
            return

        exp = session.experiment
        if not path.isfile(path.join(exp.dataroot, exp.counterfile)):
            session.log.warning('creating new empty file counter file at %s',
                                path.join(exp.dataroot, exp.counterfile))
        if session.mode == SIMULATION:
            raise ProgrammingError('assignCounter should not be called in '
                                   'simulation mode')

        # Keep track of which files we have already updated, since the proposal
        # and the sample specific counter might be the same file.
        seen = set()
        for directory, attr in [(exp.dataroot, 'counter'),
                                (exp.proposalpath, 'propcounter'),
                                (exp.samplepath, 'samplecounter')]:
            counterpath = path.normpath(path.join(directory, exp.counterfile))
            nextnum = readFileCounter(counterpath, dataset.countertype) + 1
            if counterpath not in seen:
                updateFileCounter(counterpath, dataset.countertype, nextnum)
                seen.add(counterpath)
            else:
                nextnum -= 1
            setattr(dataset, attr, nextnum)

        # push special counters into parameters for display
        if dataset.settype == SCAN:
            session.experiment._setROParam('lastscan', dataset.counter)
        elif dataset.settype == POINT:
            session.experiment._setROParam('lastpoint', dataset.counter)

    def getCounters(self):
        """Return a dictionary with the current values of all relevant file
        counters.

        Counters are relevant if there is a dataset of their type on the stack.
        Counter names are as follows:

        * (type)counter: global counters (unique in dataroot)
        * (type)propcounter: proposal local counters (unique in proposalpath)
        * (type)samplecounter: sample local counters (unique in samplepath)
        * (type)number: counter within the parent dataset (1-based)
        """
        result = {}
        # get all parent counters into the keywords
        for ds in self._stack:
            result[ds.countertype + 'counter'] = ds.counter
            result[ds.countertype + 'propcounter'] = ds.propcounter
            result[ds.countertype + 'samplecounter'] = ds.samplecounter
            result[ds.countertype + 'number'] = ds.number
        return result

    def expandNameTemplates(self, nametemplates):
        """Expand the given *nametemplates* with the current counter values."""
        if isinstance(nametemplates, string_types):
            nametemplates = [nametemplates]
        exc = None  # stores first exception if any
        # translate entries
        filenames = []
        for nametmpl in nametemplates:
            kwds = dict(session.experiment.propinfo)
            kwds.update(self.getCounters())
            try:
                filename = nametmpl % DeviceValueDict(kwds)
            except KeyError as err:
                if not exc:
                    exc = KeyError('can\'t create datafile, illegal key %s in '
                                   'filename template %r!' % (err, nametmpl))
                continue
            except TypeError as err:
                if not exc:
                    exc = TypeError('error expanding data file name: %s, check '
                                    'filename template %r!' % (err, nametmpl))
                continue
            filenames.append(filename)
        if exc and not filenames:
            # pylint: disable=raising-bad-type
            raise exc
        return filenames

    def getFilenames(self, dataset, nametemplates, *subdirs, **kwargs):
        """Determines dataset filenames from filename templates.

        Call this instead of `createDataFile` if you want to resolve the
        templates and make the filenames known in the dataset, but create (or
        copy from external) the files on your own.

        Registers the first filename in the dataset as 'the' filename.  Returns
        a short path of the first filename and a list of the absolute paths of
        all filenames.  After the counting is finished, you should create the
        datafile(s) and then call `linkFiles` to create the hardlinks.

        Keyword argument `nomeasdata` can be set to true in order to not record
        this as a measurement data file in the dataset.  (Useful for either
        temporary files or auxiliary data files.)
        """
        if dataset.counter == 0:
            raise ProgrammingError('a counter number must be assigned to the '
                                   'dataset first')
        filenames = self.expandNameTemplates(nametemplates)
        filename = filenames[0]
        filepaths = [session.experiment.getDataFilename(ln, *subdirs)
                     for ln in filenames]

        if not kwargs.get('nomeasdata'):
            shortpath = path.join(*subdirs + (filename,))
            dataset.filenames.append(shortpath)
            dataset.filepaths.append(filepaths[0])

        return filename, filepaths

    def linkFiles(self, filepath, linkpaths):
        """Creates hardlinks in *linkpaths*, pointing to *filepath*."""
        linkfunc = os.link if hasattr(os,  'link') else \
            os.symlink if hasattr(os, 'symlink') else None
        if linkfunc:
            for linkpath in linkpaths:
                self.log.debug('linking %r to %r', linkpath, filepath)
                try:
                    linkfunc(filepath, linkpath)
                except OSError:
                    self.log.warning('linking %r to %r failed, ignoring',
                                     linkpath, filepath)
        else:
            self.log.warning('can\'t link datafiles, no os support!')

    def createDataFile(self, dataset, nametemplates, *subdirs, **kwargs):
        """Creates and returns a file named according to the given nametemplate
        in the given subdir of the datapath.

        The nametemplate can be either a string or a list of strings.  In the
        second case, the first listentry is used to create the file and the
        remaining ones will be hardlinked to this file if the os supports this.

        Filename templates should contain placeholders in ``%(key)s`` format.
        Possible placeholder keys are all counters (see `getCounters`), the
        experiment's proposal info keys (e.g. ``proposal``) as well as all
        devices and parameters as accepted by `DeviceValueDict`.

        Setting `fileclass` as keyword argument a DataFile class can be
        specified used for creating the data file (descriptor).
        If no `fileclass` has been specified this defaults to
        `nicos.core.data.DataFile`.

        Keyword argument `nomeasdata` can be set to true in order to not record
        this as a measurement data file in the dataset.  (Useful for either
        temporary files or auxiliary data files.)
        """
        fileclass = kwargs.get('fileclass', DataFile)
        if session.mode == SIMULATION:
            raise ProgrammingError('createDataFile should not be called in '
                                   'simulation mode')
        filename, filepaths = self.getFilenames(dataset, nametemplates,
                                                *subdirs, **kwargs)
        filepath = filepaths[0]
        shortpath = path.join(*subdirs + (filename,))

        self.log.debug('creating file %r using fileclass %r', filename,
                       fileclass)
        datafile = fileclass(shortpath, filepath)
        exp = session.experiment
        if exp.managerights:
            os.chmod(filepath,
                     exp.managerights.get('enableFileMode', DEFAULT_FILE_MODE))
            # XXX add chown here?

        self.linkFiles(filepath, filepaths[1:])

        return datafile
