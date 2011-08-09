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

"""Class for THM 1176 magnetic field probe."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os, fcntl, time
import sys, struct, math

from nicos import status
from nicos.device import Measurable, Param, Value
from nicos.errors import CommunicationError, ConfigurationError, NicosError

USBTMC_IOCTL_CLEAR = 23298
USBTMC_IOCTL_RESET_CONF = 23298 + 9


class THM(Measurable):

    parameters = {
        'device': Param('USB device name', type=str, mandatory=True),
        'measurements': Param('Number of measurements to average over',
                              type=int, default=80, settable=True),
    }
    # timeout is 5 seconds by kernel default
    
    def doInit(self):
        self._io = None
        if self._mode != 'simulation':
            self.doReset()

    def doReadFmtstr(self):
        return '%.1f [%.0f +- %.1f, %.0f +- %.1f, %.0f +- %.1f] uT'

    def doReset(self):
        if self._io is not None:
            try:
                os.close(self._io)
            except OSError:
                pass
        self._io = os.open(self.device, os.O_RDWR)
        #fcntl.ioctl(self._io, USBTMC_IOCTL_RESET_CONF)
        ident = self._query('*IDN?')
        self._execute('FORMAT INTEGER')

    def doShutdown(self):
        if self._io is not None:
            os.close(self._io)
            self._io = None

    def doStatus(self):
        #self._query('*IDN?')
        return status.OK, 'idle'

    def _query(self, q, t=5):
        try:
            os.write(self._io, q + '\n')
            return os.read(self._io, 2000).rstrip()
        except OSError, err:
            if t == 0:
                raise CommunicationError(self, 'error querying: %s' % err)
            self.doReset()
            return self._query(q, t-1)
        self._check_status()

    def _execute(self, q, t=5, wait=0):
        try:
            os.write(self._io, q + '\n')
        except OSError, err:
            if t == 0:
                raise CommunicationError(self, 'error executing: %s' % err)
            self.doReset()
            self._execute(q, t-1)
        time.sleep(wait)
        self._check_status()

    def _check_status(self):
        try:
            os.write(self._io, '*STB?\n')
            status = os.read(self._io, 100).rstrip()
        except OSError, err:
            raise CommunicationError(self, 'error getting status: %s' % err)
        if status != '0':
            raise CommunicationError(self, 'error in command!')

    def zero(self):
        """Zero the probe in zero-gauss chamber."""
        self.log.info('Zeroing sensor, please wait a few seconds...')
        try:
            self._execute('CAL', wait=5)
        except OSError, err:
            if err.errno == 110:
                return
            raise

    def valueInfo(self):
        return Value('B', unit='uT'), \
               Value('Bx', unit='uT', errors='next'), \
               Value('dBx', unit='uT', type='error'), \
               Value('By', unit='uT', errors='next'), \
               Value('dBy', unit='uT', type='error'), \
               Value('Bz', unit='uT', errors='next'), \
               Value('dBz', unit='uT', type='error')

    def _average(self, nvalues, output):
        # format: #6nnnnnnbbbbbbbb...
        assert output.startswith('#6')
        if not len(output) == 8 + nvalues * 4:
            self.log.warning('shortened response, padding')
            output += '\x00' * (8 + nvalues * 4 - len(output))
        values = struct.unpack('>%di' % nvalues, output[8:])
        average = sum(values) / nvalues
        stdev = 0
        for val in values:
            stdev += (val - average)**2
        stdev = (stdev / (nvalues - 1))**0.5
        return average, stdev

    def doRead(self):
        n = self.measurements
        xs = self._query('MEASURE:ARRAY:X? %d,,5' % n)
        ys = self._query('FETCH:ARRAY:Y? %d,5' % n)
        zs = self._query('FETCH:ARRAY:Z? %d,5' % n)
        (x, dx), (y, dy), (z, dz) = \
            self._average(n, xs), self._average(n, ys), self._average(n, zs)
        mod = math.sqrt(x*x + y*y + z*z)
        return mod, x, dx, y, dy, z, dz

    def doStart(self, **preset):
        pass

    def doStop(self):
        pass

    def doIsCompleted(self):
        return True
