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

from nicos.core import Moveable, HasPrecision, Override, oneof, status, \
    SIMULATION, HasTimeout
from nicos.core.params import Param, Attach
from nicos.devices.tango import AnalogOutput


class Toellner(HasTimeout, HasPrecision, AnalogOutput):

    attached_devices = {
        'polchange': Attach('TANGO digital input device ', Moveable),
    }

    parameters = {
        'channel': Param('Channel of the device', type=oneof(1, 2),
                         mandatory=True),
        'voltage': Param('Maximal voltage ', type=float,
                         unit='V', volatile=True, settable=True),
    }

    parameter_overrides = {
        'precision':  Override(default=0.1),
        'timeout':    Override(default=4),
    }

    def doInit(self, mode):
        self.log.debug('Initialize Current')
        if mode != SIMULATION:
            self._dev.write('syst:rem')
            current = self._dev.Query('mc%d?' % self.channel)
            self._setval = float(current.strip())

    def doReadAbslimits(self):
        # there are no properties absmin,absmax in server
        return self._config.get('abslimits')

    def doReadVoltage(self):
        self.log.debug('Read Voltage')
        vol = self._dev.Query('mv%d?' % self.channel)
        self.log.debug('vol: %s' % vol)
        volfl = float(vol.strip())
        return volfl

    def doWriteVoltage(self, value):
        self.log.debug('Write Voltage')
        self._dev.write('syst:rem')
        self._dev.write('v%d %f' % (self.channel, value))
        self._dev.write('ex 1')
        return value

    def doStop(self):
        pass

    def doStatus(self, maxage=0, mapping=None):
        return status.OK, ''  # timeout and target are checked elsewhere now

    def _getsign(self):
        return -1 if self._adevs['polchange'].read() == '-' else 1

    def _set_field_polarity(self, value):
        polval = self._adevs['polchange'].read()
        return (value < 0 and polval == '+') or (value >= 0 and polval == '-')

    def doStart(self, value):
        polval = self._adevs['polchange'].read()
        target = self.target
        if self._set_field_polarity(value):
            polval = 1 if value < 0 else 0
            self._setROParam("target", 0)
            self._write_value(0, fromvarcheck=False)
            self._adevs['polchange'].start(polval)
        self._setROParam("target", target)
        self._write_value(value, fromvarcheck=False)

    def _write_value(self, value, fromvarcheck):
        raise NotImplementedError


class CurrentToellner(Toellner):

    parameter_overrides = {
        'unit': Override(mandatory=False, default='A')
    }

    def doRead(self, maxage=0):
        self.log.debug('In doRead() Current %s', self._name)
        cur = self._dev.Query('mc%d?' % self.channel)
        curfl = float(cur.strip())
        return curfl * self._getsign()

    def _write_value(self, value, fromvarcheck):
        self._dev.write('c%d %f' % (self.channel, abs(value)))
