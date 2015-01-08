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

"""Class for THM 1176 magnetic field probe."""

import os
import re
import math
import time
import fcntl
import struct

from nicos.core import status, Measurable, Param, Value, usermethod, \
     CommunicationError, ModeError
from nicos.core import SIMULATION, SLAVE

usbbus_pat = re.compile(r'Bus=(\s*\d+)')
usbdev_pat = re.compile(r'Dev#=(\s*\d+)')

USBDEVFS_RESET = 21780


class THM(Measurable):

    parameters = {
        'device':       Param('USB device name', type=str, mandatory=True),
        'measurements': Param('Number of measurements to average over',
                              type=int, default=80, settable=True),
    }
    # timeout is 5 seconds by kernel default

    def doInit(self, mode):
        self._io = None
        if mode != SIMULATION:
            self.doReset()

    def doReadFmtstr(self):
        return '%.1f [%.0f +- %.1f, %.0f +- %.1f, %.0f +- %.1f] uT'

    def doReset(self, t=3):
        # get usbdevfs file name
        self.log.debug('resetting...')
        devline = os.popen('grep -B3 Metrolab /proc/bus/usb/devices | '
                           'head -n1', 'r').read().strip()
        if devline:
            busno = int(usbbus_pat.search(devline).group(1))
            devno = int(usbdev_pat.search(devline).group(1))
            usbdevfsfile = '/proc/bus/usb/%03d/%03d' % (busno, devno)
            self.log.debug('usbdevfs file is %s' % usbdevfsfile)
            dfile = os.open(usbdevfsfile, os.O_RDWR)
            fcntl.ioctl(dfile, USBDEVFS_RESET)
            self.log.debug('USBDEVFS_RESET ioctl done')
            os.close(dfile)
            time.sleep(2.5)
        if self._io is not None:
            try:
                os.close(self._io)
            except OSError:
                pass
        self._io = os.open(self.device, os.O_RDWR)
        try:
            ident = self._query('*IDN?', t=0)
            self.log.debug('sensor identification: %s' % ident)
            self._execute('FORMAT INTEGER')
            self.doRead()
        except CommunicationError:
            if t == 0:
                raise
            self.doReset(t-1)
            return

    def doShutdown(self):
        if self._io is not None:
            os.close(self._io)
            self._io = None

    def doStatus(self, maxage=0):
        #self._query('*IDN?')
        return status.OK, 'idle'

    def _query(self, q, t=5):
        try:
            os.write(self._io, q.encode() + b'\n')
            ret = os.read(self._io, 2000).rstrip().decode()
        except OSError as err:
            self.log.debug('exception in query: %s' % err)
            if t == 0:
                raise CommunicationError(self, 'error querying: %s' % err)
            time.sleep(0.5)
            self.doReset()
            return self._query(q, t-1)
        self._check_status()
        return ret

    def _execute(self, q, t=5, wait=0):
        try:
            os.write(self._io, q.encode() + b'\n')
        except OSError as err:
            if t == 0:
                raise CommunicationError(self, 'error executing: %s' % err)
            time.sleep(0.5)
            self.doReset()
            self._execute(q, t-1)
        time.sleep(wait)
        self._check_status()

    def _check_status(self, t=3):
        try:
            os.write(self._io, b'*STB?\n')
            status = os.read(self._io, 100).rstrip().decode()
        except OSError as err:
            if t == 0:
                raise CommunicationError(self, 'error getting status: %s' % err)
            time.sleep(0.5)
            self.doReset()
            return self._check_status(t-1)
        if status != '0':
            self.log.warning('status byte = %s, clearing' % status)
            os.write(self._io, b'*CLS\n')

    @usermethod
    def zero(self):
        """Zero the probe in zero-gauss chamber."""
        if self._mode == SLAVE:
            raise ModeError(self, 'cannot zero probe in slave mode')
        elif self._sim_active:
            return
        self.log.info('Zeroing sensor, please wait a few seconds...')
        try:
            self._execute('CAL', wait=5)
        except OSError as err:
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

    def doRead(self, maxage=0):
        n = self.measurements
        xs = self._query('MEASURE:ARRAY:X? %d,,5' % n)
        ys = self._query('FETCH:ARRAY:Y? %d,5' % n)
        zs = self._query('FETCH:ARRAY:Z? %d,5' % n)
        (x, dx), (y, dy), (z, dz) = \
            self._average(n, xs), self._average(n, ys), self._average(n, zs)
        mod = math.sqrt(x*x + y*y + z*z)
        return [mod, x, dx, y, dy, z, dz]

    def doSetPreset(self, **preset):
        if 'n' in preset:
            self.measurements = preset['n']

    def presetInfo(self):
        return ('n',)

    def doStart(self):
        pass

    def doStop(self):
        pass

    def doIsCompleted(self):
        return True
