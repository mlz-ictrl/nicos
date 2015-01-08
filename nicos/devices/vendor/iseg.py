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

"""Iseg high voltage power supply device classes."""

from IO import StringIO

from nicos.core import status, intrange, Moveable, HasLimits, Param, Override, \
     NicosError, CommunicationError, ConfigurationError
from nicos.devices.taco.core import TacoDevice
from nicos.core import SIMULATION


class IsegHV(TacoDevice, HasLimits, Moveable):
    """Device class for an iseg HVPS.

    The channel parameter must be 1 for a HVS with only one output.
    """

    taco_class = StringIO

    parameters = {
        'channel':  Param('Channel of the Iseg HV (1 = A, 2 = B)',
                          type=intrange(1, 2), mandatory=True),
        'ramp':     Param('Voltage ramp', unit='main/min',
                          # Iseg ramps are set in V/s from 1 to 255
                          type=intrange(60, 15300), settable=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='V'),
    }

    states = {'ON ': (status.OK,    'on'),
              'OFF': (status.ERROR, 'switched off'),
              'MAN': (status.ERROR, 'switched to manual control'),
              'ERR': (status.ERROR, 'maximum voltage or current exceeded'),
              'INH': (status.ERROR, 'inhibit signal active'),
              'QUA': (status.ERROR, 'quality of voltage not guaranteed'),
              'L2H': (status.BUSY,  'ramping up'),
              'H2L': (status.BUSY,  'ramping down'),
              'LAS': (status.BUSY,  'look at status (?)'),
              'TRP': (status.ERROR, 'current trip reached')}

    def doInit(self, mode):
        if mode == SIMULATION:
            self._polarity = +1
            return
        resp = self._taco_guard(self._dev.communicate, '#')
        if resp.count(';') != 3:
            # hash is "info" command; it returns a string in the form
            # "deviceid;version;Umax;Imax"
            raise CommunicationError(self, 'communication problem with HV '
                                     'supply: ident response %r' % resp)
        # set write delay to minimum (1ms)
        self._taco_guard(self._dev.communicate, 'W=001')
        # find out polarity
        st = self._taco_guard(self._dev.communicate, 'T%d' % self.channel)
        if int(st) & 4:
            self._polarity = +1
        else:
            self._polarity = -1

    def doIsAllowed(self, target):
        if target > 0 and self._polarity == -1:
            return False, 'wrong polarity'
        elif target < 0 and self._polarity == +1:
            return False, 'wrong polarity'
        return True, ''

    def doStart(self, value):
        value = abs(value)
        self._taco_guard(self._dev.communicate,
                         'D%d=%04d' % (self.channel, value))
        resp = self._taco_guard(self._dev.communicate, 'G%d' % self.channel)
        # return message is the status
        if resp[:3] != ('S%d=' % self.channel):
            raise NicosError(self, 'could not set voltage: %r' % resp)
        if resp[3:] not in self.states or \
               self.states[resp[3:]][0] not in (status.OK, status.BUSY):
            if resp[3:] == 'MAN':
                raise NicosError(self, 'could not set voltage, voltage control '
                                'switched to manual')
            elif resp[3:] == 'OFF':
                raise NicosError(self, 'could not set voltage, device off')
            raise NicosError(self, 'could not set voltage: error %r' % resp[3:])

    def doRead(self, maxage=0):
        resp = self._taco_guard(self._dev.communicate, 'U%d' % self.channel)
        if not resp or resp[0] not in '+-':
            raise NicosError(self, 'invalid voltage readout %r' % resp)
        return int(resp)

    def doStatus(self, maxage=0):
        resp = self._taco_guard(self._dev.communicate, 'S%d' % self.channel)
        if resp[:3] != ('S%d=' % self.channel):
            raise NicosError(self, 'invalid status readout %r' % resp)
        return self.states[resp[3:]]

    def doWait(self):
        while 1:
            resp = self._taco_guard(self._dev.communicate, 'S%d' % self.channel)
            if resp[3:] == 'ON ':
                return
            elif resp[3:] not in ('L2H', 'H2L'):
                raise NicosError(self, 'device in error status: %s' % resp[3:])

    def _current(self):
        # return the current in Amperes
        resp = self._taco_guard(self._dev.communicate, 'I%d' % self.channel)
        # format is MMMM-E (mantissa/exponent)
        if len(resp) != 6:
            raise CommunicationError(self, 'invalid current readout %r' % resp)
        return float(resp[:4] + 'e' + resp[4:])

    def doReadRamp(self):
        resp = self._taco_guard(self._dev.communicate, 'V%d' % self.channel)
        return int(resp) * 60

    def doWriteRamp(self, ramp):
        ramp = int(ramp / 60.)
        if ramp == 0:
            raise ConfigurationError(self, 'ramp is too small; must be at '
                                     'least 60 V/min')
        resp = self._taco_guard(self._dev.communicate,
                                'V%d=%03d' % (self.channel, ramp))
        if resp:
            raise CommunicationError(self, 'could not write ramp, reply from '
                                     'device: %r' % resp)
        resp = self._taco_guard(self._dev.communicate, 'A%d=01' % self.channel)
        if resp:
            raise CommunicationError(self, 'could not save ramp, reply from '
                                     'device: %r' % resp)
        self.log.info('ramp set to %d V/min and stored in EEPROM' % (ramp*60))
