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

"""The global data manager class."""

import os
import logging
from os import path
from time import time as currenttime

from nicos import session
from nicos.core.constants import SIMULATION
from nicos.core.errors import ProgrammingError
from nicos.core.utils import DeviceValueDict
from nicos.core.data.dataset import PointDataset, ScanDataset, \
    SubscanDataset, BlockDataset
from nicos.core.data.sink import DataFile
from nicos.pycompat import iteritems, string_types
from nicos.utils import DEFAULT_FILE_MODE, lazy_property, readFileCounter, \
    updateFileCounter


class DataManager(object):
    """Singleton class that manages incoming data.

    It takes all data that is produced by detectors and distributes it to sinks.
    """

    def __init__(self):
        # A stack of currently active datasets.  Maximum 3 depth.
        self._stack = []

        # Last finished scans.  Stored for analysis purposes.
        self._last_scans = []

    @lazy_property
    def log(self):
        logger = session.getLogger('nicos-data')  # XXX name?
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
        self._last_scans = []

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
        # XXX: when to clean these up?
        self._last_scans.append(scan)

    def _init(self, dataset):
        """Initialises the dataset and puts it on the stack.
        Finally dispatches corresponding sink handlers."""
        self.log.debug('Created new dataset %s' % dataset)
        for sink in session.datasinks:
            if sink.isActive(dataset):
                handlers = sink.createHandlers(dataset)
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
        dataset.trimResult()

    #
    # Filling datasets with data
    #

    def putMetainfo(self, metainfo):
        # metainfo is {(devname, param): (rawvalue, strvalue, unit, category)}
        if self._current.settype != 'point':
            self.log.warning('No current point dataset, ignoring metainfo')
            return
        self._current.metainfo.update(metainfo)
        self._current.dispatch('putMetainfo', metainfo)

    def putValues(self, values):
        # values is {devname: (timestamp, value)}
        if self._current.settype != 'point':
            self.log.warning('No current point dataset, ignoring values')
            return
        self._current._addvalues(values)
        self._current.dispatch('putValues', values)

    def putResults(self, quality, results):
        # results is {devname: (readvalue, arrays)}
        if self._current.settype != 'point':
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
        if not self._current or self._current.settype != 'point':
            return
        devname = session.device_case_map[key.split('/')[0]]
        try:
            self.putValues({devname: (time, value)})
        except Exception:
            pass

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
        if dataset.counter != 0:
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

    def expandDataFile(self, dataset, nametemplates):
        """Determine the final data file name(s)."""
        if dataset.counter is None:
            raise ProgrammingError('expandDataFile: a counter number must be '
                                   'assigned to the dataset first')
        if isinstance(nametemplates, string_types):
            nametemplates = [nametemplates]
        # translate entries
        filenames = []
        for nametmpl in nametemplates:
            kwds = dict(session.experiment.propinfo)
            # get all parent counters into the keywords
            # i.e. blockcounter, scancounter, pointcounter
            for ds in self._stack:
                kwds[ds.countertype + 'counter'] = ds.counter
            # XXX(dataapi): add experiment local counter
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
            filenames.append(filename)
        return filenames

    def getFilenames(self, dataset, nametemplates, *subdirs):
        """Determines filenames from filename templates.

        Registers the first filename in the dataset as 'the' filename.  Returns
        a short path of the first filename and a list of the absolute paths of
        all filenames.
        After the counting is finished, you should create the datafile(s)
        and then call `linkFiles` to create the hardlinks.
        """
        exp = session.experiment
        filenames = self.expandDataFile(dataset, nametemplates)
        filename = filenames[0]
        filepaths = [exp.getDataFilename(ln, *subdirs) for ln in filenames]

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
                self.log.debug('linking %r to %r' % (linkpath, filepath))
                try:
                    linkfunc(filepath, linkpath)
                except OSError:
                    self.log.warning('linking %r to %r failed, ignoring' %
                                     (linkpath, filepath))
        else:
            self.log.warning('can\'t link datafiles, no os support!')

    def createDataFile(self, dataset, nametemplates, *subdirs, **kwargs):
        """Creates and returns a file named according to the given nametemplate
        in the given subdir of the datapath.

        The nametemplate can be either a string or a list of strings.  In the
        second case, the first listentry is used to create the file and the
        remaining ones will be hardlinked to this file if the os supports this.

        Setting `fileclass` as keyword argument a DataFile class can be
        specified used for creating the data file (descriptor).
        If no `fileclass` has been specified this defaults to
        `nicos.core.data.DataFile`.
        """
        fileclass = kwargs.get("fileclass", DataFile)
        if session.mode == SIMULATION:
            raise ProgrammingError('createDataFile should not be called in '
                                   'simulation mode')
        exp = session.experiment
        filename, filepaths = self.getFilenames(dataset, nametemplates, *subdirs)
        filepath = filepaths[0]
        shortpath = path.join(*subdirs + (filename,))

        self.log.debug('creating file %r using fileclass %r' % (filename,
                                                                fileclass))
        datafile = fileclass(shortpath, filepath)
        if exp.managerights:
            os.chmod(filepath,
                     exp.managerights.get('enableFileMode', DEFAULT_FILE_MODE))
            # XXX add chown here?

        self.linkFiles(filepath, filepaths[1:])

        return datafile


# Create the singleton instance right now.
dataman = DataManager()
