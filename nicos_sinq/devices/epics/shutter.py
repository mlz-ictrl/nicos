# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

"""
This module contains the interface to the Sinq Shutter Control.
"""
from nicos.core import SIMULATION, Moveable, Override, Param, oneof, pvname, \
    status
from nicos.devices.epics import EpicsDevice
from nicos.devices.epics.status import EPICS_TIMEOUT_MSG

class Shutter(EpicsDevice, Moveable):
    """
    Interface to Epics Based Sinq Shutter Control
    """

    parameters = {
        'pvprefix':
            Param('Prefix for Shutter PV Interface',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=False,
                ),
        'preparing':
            Param('Internal: set when shutter movement triggered',
                  type=bool,
                  default=False,
                  mandatory=False,
                  settable=True,
                  volatile=False,
                  unit='',
                  fmtstr='%s',
                  userparam=False,
                  internal=True,
                  ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'unit': Override(default='', internal=True, settable=False,
                         userparam=False, mandatory=False),
        'monitor': Override(default=True, prefercache=False),
    }

    _shutterpvs = {
        'readpv': 'OPEN',
        'writepv': 'SHUTTER',
        'statuspv': 'STATUS',
        'statusmsgpv': 'STATUS-Msg.SVAL',
        'resetpv': 'RESET',
    }

    _cache_relations = {
        'readpv': 'value',
    }

    _STATUS_CODES = {0: status.OK, 1: status.BUSY, 2: status.WARN, 3: status.ERROR}

    def _get_pv_parameters(self):
        return self._shutterpvs.keys()

    def _get_status_parameters(self):
        return {'readpv', 'statuspv', 'statusmsgpv'}

    def _subscribe(self, change_callback, pvname, pvparam):
        return self._epics_wrapper.subscribe(pvname, pvparam, change_callback,
                                             self.connection_change_callback,
                                             as_string=True)

    def _get_pv_name(self, pvparam):
        if pvparam in self._shutterpvs.keys():
            return f'{self.pvprefix}:{self._shutterpvs[pvparam]}'
        return EpicsDevice._get_pv_name(self, pvparam)

    def doInit(self, mode):
        if mode == SIMULATION:
            self.valuetype = oneof('Open', 'Closed')
            return

        EpicsDevice.doInit(self, mode)

        # Get the meaning of False and True if specified in Epics Database
        choices = self._epics_wrapper.get_value_choices(self._get_pv_name('readpv'))
        self._mapping = dict(zip(
            choices, range(len(choices))
        ))

        self.valuetype = oneof(*self._mapping)

        # Sets the target to the current shutter readback state during
        # initialisation, instead of using what was in the Cache, so that Nicos
        # doesn't potentially think that the shutter is moving.
        self._setROParam(
            'target',
            self._get_pv('readpv', as_string=True)
        )

    def doRead(self, maxage=0):
        return self._get_pv('readpv', as_string=True)

    def doStart(self, value):
        if value != self.read(0):
            self.preparing = True
            self.status(0)
            self._put_pv('writepv', value)

    def doStop(self):
        # We are unable to stop a change when it is already in motion, so we
        # don't even try
        self.log.warning("Shutter can't be stopped once a movement is started!")

    def doReset(self):
        self.preparing = False
        # I have seen, that sometimes the SPS doesn't actually execute the
        # command and then we end up in a slightly weird state. The user should
        # have an escape hatch.
        self._put_pv('resetpv', 1)

    def doStatus(self, maxage=0):
        try:

            status_code = self._get_pv('statuspv')
            status_msg = self._get_pv('statusmsgpv', as_string=True)

            if self.preparing and status_code != 0:
                self._setROParam('preparing', False)

            if self.preparing and status_code == 0:
                return status.BUSY, 'Movement requested'
            else:
                return self._STATUS_CODES.get(status_code, status.UNKNOWN), status_msg

        except TimeoutError:
            return status.ERROR, EPICS_TIMEOUT_MSG

    def doIsAllowed(self, pos):
        (status_code, msg) = self.status(0)
        if status_code != status.OK:
            if msg:
                return (False, msg)
            elif status_code == status.BUSY:
                return (False, 'Shutter is already moving')
            else:
                return (False, 'Open/Closing the shutter is not possible')
        return (True, '')

    # Disable Poller
    def doReadPollinterval(self):
        return None
