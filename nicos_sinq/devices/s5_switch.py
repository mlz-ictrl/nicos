#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from time import monotonic

from nicos.core import Override, Param, pvname, status
from nicos.core.errors import ConfigurationError
from nicos.devices.abstract import MappedMoveable

from nicos_ess.devices.epics.base import EpicsDeviceEss, EpicsReadable


class S5Switch(EpicsDeviceEss, MappedMoveable):
    """AMOR has a Siemens programmable logic unit for controlling the shutter
    and a switch for the alignment laser and the spin flipper. This is SPS
    which is connected to the world as such via a custom RS232 interface and a
    terminal server. *readpv* returns a waveform record with 16 bytes giving
    the state of the SPS digital inputs. *commandpv* sends the commands to
    toggle SPS buttons.
    """

    parameters = {
        'byte': Param('Byte number representing the state of this unit',
                      type=int, mandatory=True, userparam=False,
                      settable=False),
        'bit': Param('Bit number from the byte representing the state',
                     type=int, mandatory=True, userparam=False,
                     settable=False),
        'readpv': Param('PV to read the digital input waveform', type=pvname,
                        mandatory=True, settable=False, userparam=False),
        'commandpv': Param('PV to send the command to toggle state',
                           type=pvname, mandatory=True, settable=False,
                           userparam=False),
        'commandstr': Param('Command string to issue on commandpv', type=str,
                            mandatory=True, settable=False, userparam=False),
        'lasttoggle': Param('Store the time when last toggled', type=int,
                            settable=True, internal=True, default=0),
        'lasttarget': Param('Store the last raw target of move', type=bool,
                            settable=True, internal=True, default=None)
    }

    parameter_overrides = {
        'mapping': Override(userparam=False, settable=False),
        'fallback': Override(userparam=False),
        'unit': Override(mandatory=False, userparam=False, settable=False),
        'fmtstr': Override(userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False)
    }

    def doInit(self, mode):
        EpicsDeviceEss.doInit(self, mode)
        MappedMoveable.doInit(self, mode)
        raw = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                      count=self.byte+1)
        if self.byte > len(raw):
            raise ConfigurationError('Byte specified is out of bounds')

    def _get_pv_parameters(self):
        return {'readpv', 'commandpv'}

    def doStatus(self, maxage=0):
        epics_status = EpicsDeviceEss.doStatus(self, maxage)
        if epics_status[0] != status.OK:
            return epics_status

        now = monotonic()
        if self.lasttarget is not None and \
                self.lasttarget != self._readRaw(maxage):
            if now > self.lasttoggle+10:
                return (status.WARN, '%s not reached!'
                        % self._inverse_mapping[self.lasttarget])
            return status.BUSY, ''
        return status.OK, ''

    def doIsAtTarget(self, pos, target):
        # Don't check if it reached the target
        return True

    def _readBit(self, byte, bit):
        raw = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                      count=self.byte+1)
        powered = 1 << bit
        return raw[byte] & powered == powered

    def _readRaw(self, maxage=0):
        return self._readBit(self.byte, self.bit)

    def _startRaw(self, target):
        if self._readRaw() != target:
            self.lasttoggle = monotonic()
            self.lasttarget = target
            self._put_pv('commandpv', self.commandstr)


class AmorShutter(S5Switch):
    """Class to represent AMOR shutter.

    Two bits from PLC are important in determing the shutter state:

     - byte: 4, bit 0 (bit40) - parameters: byte, bit
     - byte: 4, bit 3 (bit43) - parameters: brokenbyte, brokenbit

    Following is the logic to get the current state of the shutter::

      if bit40 is true or is equal to 1
          state is "OPEN"
      else:
          if bit43 is true or is equal to 1:
              state is "CLOSED"
          else:
              state is "BROKEN" (shutter is not enabled)
    """

    parameters = {
        'brokenbyte': Param('Byte representing the broken state', type=int,
                            mandatory=True, userparam=False, settable=False),
        'brokenbit': Param('Bit representing the broken state', type=int,
                           mandatory=True, userparam=False, settable=False),
    }

    def _isBroken(self):
        return not self._readRaw() and not self._readBit(self.brokenbyte,
                                                         self.brokenbit)

    def doIsAllowed(self, target):
        if self._isBroken():
            return False, 'Enclosure is broken! Cannot change state!'
        return True, ''

    def doStatus(self, maxage=0):
        if self._isBroken():
            return status.WARN, 'BROKEN'

        super_status = S5Switch.doStatus(self, maxage)
        if super_status[0] != status.OK:
            return super_status

        return status.OK, 'Enabled'


class S5Bit(EpicsReadable):
    """
    A class for reading a single bit from a SINQ SPS S5
    """

    parameters = {
        'byte': Param('Byte number representing the state of this unit',
                      type=int, mandatory=True, userparam=False,
                      settable=False),
        'bit': Param('Bit number from the byte representing the state',
                     type=int, mandatory=True, userparam=False,
                     settable=False),
    }

    def doInit(self, mode):
        EpicsReadable.doInit(self, mode)
        raw = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                      count=self.byte+1)
        if self.byte > len(raw):
            raise ConfigurationError('Byte specified is out of bounds')

    def doRead(self, maxage=0):
        raw = self._pvs['readpv'].get(timeout=self.epicstimeout,
                                      count=self.byte+1)

        powered = 1 << self.bit
        return raw[self.byte] & powered == powered
