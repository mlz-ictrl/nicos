#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Data handling classes for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
import errno
from os import path

from nicm import nicos
from nicm.utils import listof, readFile, writeFile
from nicm.device import Device, Param
from nicm.errors import ConfigurationError, ProgrammingError
from nicm.commands.output import printinfo


TIMEFMT = '%Y-%m-%d %H:%M:%S'


class DataSink(Device):
    """
    A DataSink is a configurable object that receives measurement data.  All
    data handling is done by sinks; e.g. displaying it on the console or saving
    to a data file.
    """

    parameters = {
        'scantypes': Param('Scan types for which the sink is active',
                           type=listof(str), default=[]),
    }

    # Set to false in subclasses that e.g. write to the filesystem.
    activeInSimulation = True

    def prepareDataset(self):
        """Prepare for a new dataset.

        Returns a list of info about the new dataset as ``(key, value)`` pairs.
        A list of all these pairs is then passed to all sinks' `beginDataset()`
        as the *sinkinfo* parameter.  This is meant for sinks that write files
        to communicate the file name to sinks that write the info to the console
        or display them otherwise.
        """
        return []

    def beginDataset(self, devices, positions, detlist, preset,
                     userinfo, sinkinfo):
        """Begin a new dataset.

        The dataset will contain x-values for all *devices* (a list of `Device`
        objects), measured at *positions* (a list of lists, or None if the
        positions are not yet known).

        The dataset will contain y-values measured by the *detlist* using the
        given *preset* (a dictionary).

        *userinfo* is an arbitrary string.  *sinkinfo* is a list of ``(key,
        value)`` pairs as explained in `prepareDataset()`.
        """
        pass

    def addInfo(self, category, valuelist):
        """Add additional information to the dataset.

        This is meant to record e.g. device values at scan startup.  *valuelist*
        is a sequence of tuples ``(device, key, value)``.
        """
        pass

    def addPoint(self, num, xvalues, yvalues):
        """Add a point to the dataset.

        *num* is the number of the point in the scan
        *xvalues* is a list of values with the same length as the initial
        *devices* list given to `beginDataset()`, and *yvalues* is a list of
        values with the same length as the all of detlist's value lists.
        """
        pass

    def endDataset(self):
        """End the current dataset."""
        pass

    def setDatapath(self, value):
        # XXX needed?
        pass


class ConsoleSink(DataSink):

    def beginDataset(self, devices, positions, detlist, preset,
                     userinfo, sinkinfo):
        printinfo('=' * 80)
        printinfo('Starting scan:      ' + (userinfo or ''))
        for name, value in sinkinfo:
            printinfo('%-20s%s' % (name+':', value))
        printinfo('Started at:         ' + time.strftime(TIMEFMT))
        printinfo('-' * 80)
        detnames = []
        detunits = []
        for det in detlist:
            names, units = det.valueInfo()
            detnames.extend(names)
            detunits.extend(units)
        printinfo('\t'.join(map(str, ['#'] + devices + detnames))
                  .expandtabs())
        printinfo('\t'.join([''] + [dev.unit for dev in devices] +
                            detunits).expandtabs())
        printinfo('-' * 80)
        if positions:
            self._npoints = len(positions)
        else:
            self._npoints = 0

    def addPoint(self, num, xvalues, yvalues):
        if self._npoints:
            point = '%s/%s' % (num, self._npoints)
        else:
            point = num
        printinfo('\t'.join(map(str, [point] + xvalues + yvalues))
                  .expandtabs())

    def endDataset(self):
        printinfo('-' * 80)
        printinfo('Finished at:        ' + time.strftime(TIMEFMT))
        printinfo('=' * 80)


class DatafileSink(DataSink):

    activeInSimulation = False



class AsciiDatafileSink(DatafileSink):
    parameters = {
        'commentchar': Param('Comment character', type=str, default='#',
                             settable=True),
        'semicolon': Param('Whether to add a semicolon between X and Y values',
                           type=bool, default=True),
        'lastfilenumber': Param('The number of the last written data file',
                                type=int),
    }

    def doPreinit(self):
        self._counter = 0

    def doInit(self):
        self._path = None
        self._file = None
        self._fname = ''
        self._scomment = self.commentchar
        self._tcomment = self.commentchar * 3

    def doWriteCommentchar(self, value):
        if len(value) > 1:
            raise ConfigurationError('comment character should only be '
                                     'one character')
        self._scomment = value
        self._tcomment = value * 3

    def doReadLastfilenumber(self):
        return self._counter

    def setDatapath(self, value):
        self._path = value
        # determine current file counter value
        counterpath = path.join(self._path, 'filecounter')
        try:
            currentcounter = int(readFile(counterpath)[0])
        except IOError, err:
            # if the file doesn't exist yet, this is ok, but reraise all other
            # exceptions
            if err.errno == errno.ENOENT:
                currentcounter = 0
            else:
                raise
        self._counter = currentcounter
        self._setROParam('lastfilenumber', self._counter)

    def nextFileName(self):
        """Return the file name for the next data file.  Can be overwritten in
        instrument-specific subclasses.
        """
        pnr = nicos.system.experiment.proposalnumber
        return '%04d_%08d.dat' % (pnr, self._counter)

    def prepareDataset(self):
        if self._path is None:
            self.setDatapath(nicos.system.datapath)
        self._wrote_columninfo = False
        self._counter += 1
        writeFile(path.join(self._path, 'filecounter'), [str(self._counter)])
        self._setROParam('lastfilenumber', self._counter)
        self._fname = self.nextFileName()
        self._fullfname = path.join(self._path, self._fname)
        return [('filename', self._fname)]

    def beginDataset(self, devices, positions, detlist, preset,
                     userinfo, sinkinfo):
        if path.isfile(self._fullfname):
            # XXX for now, prevent from ever overwriting data files
            raise ProgrammingError('Data file named %r already exists!' %
                                   self._fullfname)
        self._file = open(self._fullfname, 'w')
        self._userinfo = userinfo
        self._file.write('%s NICOS data file, created at %s\n' %
                         (self._tcomment, time.strftime(TIMEFMT)))
        for name, value in sinkinfo + [('info', userinfo)]:
            self._file.write('%s %25s : %s\n' % (self._scomment, name, value))
        self._file.flush()
        # to be written later (after info)
        devnames = map(str, devices)
        devunits = [dev.unit for dev in devices]
        detnames = []
        detunits = []
        for det in detlist:
            names, units = det.valueInfo()
            detnames.extend(names)
            detunits.extend(units)
        if self.semicolon:
            self._colnames = devnames + [';'] + detnames
            self._colunits = devunits + [';'] + detunits
        else:
            self._colnames = devnames + detnames
            self._colunits = devunits + detunits

    def addInfo(self, category, valuelist):
        self._file.write('%s %s\n' % (self._tcomment, category))
        for device, key, value in valuelist:
            self._file.write('%s %25s : %s\n' %
                             (self._scomment, device.name + '_' + key, value))
        self._file.flush()

    def addPoint(self, num, xvalues, yvalues):
        if not self._wrote_columninfo:
            self._file.write('%s Scan data\n' % self._tcomment)
            self._file.write('%s %s\n' % (self._scomment,
                                          '\t'.join(self._colnames)))
            self._file.write('%s %s\n' % (self._scomment,
                                          '\t'.join(self._colunits)))
            self._wrote_columninfo = True
        if self.semicolon:
            values = xvalues + [';'] + yvalues
        else:
            values = xvalues + yvalues
        self._file.write('\t'.join(map(str, values)) + '\n')
        self._file.flush()

    def endDataset(self):
        self._file.write('%s End of NICOS data file %s\n' %
                         (self._tcomment, self._fname))
        self._file.close()
        self._file = None
