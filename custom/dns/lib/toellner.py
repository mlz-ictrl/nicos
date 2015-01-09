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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

from time import time as currenttime

from PyTango import CommunicationFailed

from nicos.core import Moveable, HasPrecision, Override, oneof, status, \
    SIMULATION
from nicos.core.errors import CommunicationError, MoveError
from nicos.core.params import Param, Attach
from nicos.devices.tango import AnalogOutput


class Toellner(AnalogOutput, HasPrecision):

    attached_devices = {
        'polchange': Attach('TANGO digital input device ', Moveable),
    }

    parameters = {
        'channel' : Param('Channel of the device', type=oneof(1, 2),
                          mandatory=True),
        'voltage' : Param('Maximal voltage ', type=float,
                          unit='V', volatile=True, settable=True),
    }

    parameter_overrides = {
        'precision':  Override(default=0.1),
    }

    def doInit(self, mode):
        self.log.debug('Initialize Current')
        self._starttime = currenttime()
        if mode != SIMULATION:
            try:
                self._dev.write('syst:rem')
                current = self._dev.Query('mc%d?' % self.channel)
                self._setval = float(current.strip())
            except CommunicationFailed:
                raise CommunicationError(self, 'Device %s is not reachable'
                                          % self._name)

    def doReadAbslimits(self):
        #there are no properties absmin,absmax in server
        return self._config.get('abslimits')

    def doReadVoltage(self):
        self.log.debug('Read Voltage')
        try:
            vol = self._dev.Query('mv%d?' % self.channel)
            self.log.debug('vol: %s' % vol)
            volfl = float(vol.strip())
            return volfl
        except CommunicationFailed:
            raise CommunicationError(self, 'Device %s is not reachable'
                                      % self._name)

    def doWriteVoltage(self,value):
        self.log.debug('Write Voltage')
        try:
            self._dev.write('syst:rem')
            self._dev.write('v%d %f' % (self.channel, value))
            self._dev.write('ex 1')
        except CommunicationFailed:
            raise CommunicationError(self, 'Device %s is not reachable'
                                      % self._name)
        return value

    def doStop(self):
        pass

    def doStatus(self, maxage=0, mapping=None):
        val = self.read()
        if abs(self._setval - val) > self.precision and \
                  currenttime() - self._starttime < 4:  #wait max 4 sec
            return status.BUSY, ''
        return status.OK, ''

    def _getsign(self):
        polval = self._adevs['polchange'].read()
        return -1 if polval == '-' else 1

    def _set_field_polarity(self,value):
        polval = self._adevs['polchange'].read()
        return (value < 0 and polval == '+') or (value >= 0 and polval == '-')

    def doStart(self, value):
        try:
            polval = self._adevs['polchange'].read()
            if self._set_field_polarity(value):
                polval = 1 if value < 0 else 0
                self._write_value(0, fromvarcheck=False)
                self._adevs['polchange'].start(polval)
            self._write_value(value, fromvarcheck=False)
        except CommunicationFailed:
            raise CommunicationError(self, 'Device %s cannot set current'
                                      % self._name)

class CurrentToellner(Toellner):

    parameter_overrides = {
        'unit': Override(mandatory=False, default='A')
    }

    def doRead(self, maxage=0):
        self.log.debug('In doRead() Current %d', self._name)
        try:
            cur = self._dev.Query('mc%d?' % self.channel)
            curfl = float(cur.strip())
            return curfl * self._getsign()
        except CommunicationFailed:
            raise CommunicationError(self, 'Device %s cannot read current'
                                      % self._name)

    def _write_value(self,value,fromvarcheck):
        self._setval = value
        self._starttime = currenttime()
        self._dev.write('c%d %f' % (self.channel, abs(value)))
        newvalue = self.wait()
        if abs(newvalue - value) > self.precision:
            if not fromvarcheck:
                self.log.warning('value %s instead of %s exceeds precision'
                                     % (newvalue, value))
                self._write_value(value, fromvarcheck=True)
            else:
                raise MoveError(self,
                                'power supply failed to set correct value')

