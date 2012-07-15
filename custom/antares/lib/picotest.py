#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for Picotest function generator."""

__version__ = "$Revision$"

import os
import time

from nicos.core import status, Moveable, Param, CommunicationError, \
     floatrange, oneof


class G5100A(Moveable):

    parameters = {
        'device':    Param('USB device name', type=str, mandatory=True),
        'amplitude': Param('Amplitude of signal', type=floatrange(20, 1000),
                           unit='mV', settable=True),
        'shape':     Param('Signal shape', settable=True,
                           type=oneof(str, 'sine', 'square', 'ramp')),
    }
    # timeout is 5 seconds by kernel default

    def doPreinit(self, mode):
        self._io = None
        if mode != 'simulation':
            self.doReset()

    def doReset(self):
        if self._io is not None:
            try:
                os.close(self._io)
            except OSError:
                pass
        self._io = os.open(self.device, os.O_RDWR)
        #fcntl.ioctl(self._io, USBTMC_IOCTL_RESET_CONF)
        ident = self._query('*IDN?')
        self.log.debug('ident: %s' % ident)

    def doShutdown(self):
        if self._io is not None:
            os.close(self._io)
            self._io = None

    def doStatus(self, maxage=0):
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
        #self._check_status()

    def _execute(self, q, t=5, wait=0):
        try:
            os.write(self._io, q + '\n')
        except OSError, err:
            if t == 0:
                raise CommunicationError(self, 'error executing: %s' % err)
            self.doReset()
            self._execute(q, t-1)
        time.sleep(wait)
        #self._check_status()

    def _check_status(self):
        try:
            os.write(self._io, '*STB?\n')
            status = os.read(self._io, 100).rstrip()
        except OSError, err:
            raise CommunicationError(self, 'error getting status: %s' % err)
        if status != '0':
            raise CommunicationError(self, 'error in command!')

    def doRead(self, maxage=0):
        return float(self._query('FREQ?'))

    def doStart(self, value):
        self._execute('FREQ %f' % value)

    def doStop(self):
        pass

    def doPoll(self, n):
        self._pollParam('amplitude')

    def doReadAmplitude(self):
        return float(self._query('VOLT?')) * 1000.

    def doWriteAmplitude(self, value):
        self._execute('VOLT %f' % (value / 1000.))

    def doReadShape(self):
        shape = self._query('FUNC?')
        return {'SIN': 'sine', 'SQU': 'square', 'RAMP': 'ramp'}[shape]

    def doWriteShape(self, value):
        shape = {'sine': 'SIN', 'square': 'SQU', 'ramp': 'RAMP'}[value]
        self._execute('FUNC %s' % shape)
