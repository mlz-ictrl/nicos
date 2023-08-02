# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from time import time as currenttime

from nicos import session
from nicos.core import Attach, Override, Param, none_or, oneof, pvname, status
from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics.pyepics import EpicsDevice
from nicos.devices.generic import Pulse


class S7Switch(EpicsDevice, MappedMoveable):
    """
    This class implements switching something in a Siemens S7 SPS as
    programmed by Roman Bürge. These things are toggled by sending a
    pulse to a digital output.
    """

    attached_devices = {
        'button': Attach('Pulse device to cause toggling the state',
                         Pulse),
    }

    parameters = {
        'readpv': Param('PV to read the current state', type=pvname,
                        mandatory=True, settable=False, userparam=False),
        'lasttarget': Param('Store the last raw target of move', type=bool,
                            settable=True, internal=True, default=None),
        'lasttoggle': Param('Store the time when last toggled', type=int,
                            settable=True, internal=True, default=0),
        'timeout': Param('Timeout when we consider the operation to '
                         'have failed', type=int, mandatory=True,
                         userparam=False),
    }

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)

    def _get_pv_parameters(self):
        return {'readpv'}

    def _readRaw(self, maxage=0):
        return self._get_pv('readpv')

    def _startRaw(self, target):
        if target == self._readRaw(0):
            return
        self.lasttarget = target
        self.lasttoggle = currenttime()
        self._attached_button.start(1)

    def doStatus(self, maxage=0):
        now = currenttime()
        if self.lasttarget is not None and \
                self.lasttarget != self._readRaw(maxage):
            if now > self.lasttoggle+self.timeout:
                return (status.WARN, '%s not reached!'
                        % self._inverse_mapping[self.lasttarget])
            return status.BUSY, ''
        return status.OK, ''


class S7Shutter(S7Switch):
    """
    A shutter as implemented on a SPS S7 programmed by Roman Bürge
    """
    parameters = {
        # The readpv inherited from S7Switch is used to test for shutter open
        'readypv': Param('PV to read if the enclosure is broken', type=pvname,
                         mandatory=True, settable=False, userparam=False),
        'closedpv': Param('PV to read if the shutter is closed', type=pvname,
                          mandatory=True, settable=False, userparam=False),
        'errorpv': Param('PV to read if there is a shutter error',
                         type=none_or(pvname), mandatory=False, settable=False,
                         userparam=False),
    }

    parameter_overrides = {
        'mapping': Override(default={'open': 0, 'closed': 1,
                                     'enclosure broken': 2,
                                     'shutter error': 3},
                            mandatory=False)
    }

    valuetype = oneof('open', 'closed')

    def _get_pv_parameters(self):
        par = {'readpv', 'readypv', 'closedpv'}
        if self.errorpv:
            par.add('errorpv')
        return par

    def _readRaw(self, maxage=0):
        if self._get_pv('readpv'):
            return 0
        if not self._get_pv('readypv'):
            return 2
        if self.errorpv and self._get_pv('errorpv'):
            return 3
        if self._get_pv('closedpv'):
            return 1

    def _startRaw(self, target):
        state = self._readRaw(0)
        if state == target:
            return

        if target in [0, 1] and state < 2:
            self.lasttarget = target
            self.lasttoggle = currenttime()
            self._attached_button.start(1)
        else:
            session.log.error('Cannot set shutter into error states')
            return

        if state == 2:
            session.log.error('Cannot move shutter, enclosure is broken')
            return
        if state == 3:
            session.log.error('Shutter system error, cannot move')
            return

    def doIsAllowed(self, target):
        if target in ['open', 'closed']:
            if not self._get_pv('readypv'):
                return False, 'Enclosure is broken'
            if self.errorpv and self._get_pv('errorpv'):
                return False, 'Shutter system error'
            else:
                return True, ''
