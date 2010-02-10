#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Data handling classes for NICOS
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Data handling classes for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from os import path

from nicm import nicos
from nicm.device import Device
from nicm.commands.output import printinfo


class DataSink(Device):
    parameters = {
        'scantypes': ([], False, 'Scan types for which the sink is active.'),
    }

    def beginDataset(self, devices, detector, preset):
        pass

    def addPoint(self, position, counts):
        pass

    def endDataset(self):
        pass


class ConsoleSink(DataSink):

    def beginDataset(self, devices, detector, preset):
        printinfo('-' * 80)
        printinfo('New Scan')
        printinfo('\t'.join(map(str, devices + [detector])))

    def addPoint(self, position, counts):
        printinfo('\t'.join(map(str, position + [counts])))

    def endDataset(self):
        printinfo('-' * 80)


class DatafileSink(DataSink):
    parameters = {
        'prefix': ('', False, 'Data file name prefix.'),
    }

    def doInit(self):
        self._path = nicos.getSystem().getStorage().getDatapath()
        self._file = None
        self._counter = 0
        self.doSetPrefix(self._params['prefix'])

    def doSetPrefix(self, value):
        self._prefix = self._params['prefix']
        if self._prefix:
            self._prefix += '_'

    def beginDataset(self, devices, detector, preset):
        self._counter += 1
        fname = path.join(self._path, self._prefix + '%s.dat' % self._counter)
        self._file = open(fname, 'w')
        self._file.write('MEASUREMENT DATA\n')
        self._file.write('\t'.join(map(str, devices)) + '\n')
        self._file.flush()
        printinfo('Scan datafile: ' + fname)

    def endDataset(self):
        self._file.close()
        self._file = None

    def addPoint(self, position, counts):
        self._file.write('\t'.join(map(str, position)) + '\n')
        self._file.flush()


class Storage(Device):
    parameters = {
        'datapath': ('', True, 'Path for data files.'),
    }
    attached_devices = {
        'sinks': [DataSink],
    }

    def addSink(self):
        pass

    def getSinks(self, scantype=None):
        if scantype is None:
            return self._adevs['sinks']
        else:
            return [sink for sink in self._adevs['sinks']
                    if not sink.getScantypes() or
                       scantype in sink.getScantypes()]
