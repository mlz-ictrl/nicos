# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2026-present by the NICOS contributors (see AUTHORS)
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
This module contains a devices for interfacing with the SPS Controlled Beamstop
Changer and a device for ensuring that the Beamstop motors aren't sent move
commands while the currently in position beamstop is being changed by the SPS.
"""

from nicos.core import SIMULATION, Attach, Device, IsController, Moveable, \
    Override, Param, multiStatus, oneof, pvname, status
from nicos.devices.epics import EpicsDevice


class Beamstop(EpicsDevice, Moveable):
    """
    EPICS device for changing Beamstop at SANS-LLB
    """

    parameters = {
        'pvprefix':
            Param('Prefix for Beamstop PV Interface',
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
            Param('Internal: set when beamstop change triggered',
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
        # MBBI, BI, etc. do not have units
        'unit': Override(mandatory=False, settable=False, volatile=False),
        'fmtstr': Override(default='%d'),
        'monitor': Override(default=True, prefercache=False),
    }

    _beamstoppvs = {
        'readpv': 'BEAMSTOP_RBV',
        'writepv': 'BEAMSTOP',
        'statuspv': 'STATUS',
        'statusmsgpv': 'STATUS-Msg.SVAL',
        'resetpv': 'BEAMSTOP-INIT',
    }

    _cache_relations = {
        'readpv': 'value',
    }

    _STATUS_CODES = {0: status.OK, 1: status.BUSY, 2: status.WARN, 3: status.ERROR}

    valuetype = int

    def _get_pv_parameters(self):
        return self._beamstoppvs.keys()

    def _get_status_parameters(self):
        return {'readpv', 'statuspv'}

    def _get_pv_name(self, pvparam):
        if pvparam in self._beamstoppvs.keys():
            return ':'.join([self.pvprefix, self._beamstoppvs[pvparam]])
        return EpicsDevice._get_pv_name(self, pvparam)

    def doInit(self, mode):
        EpicsDevice.doInit(self, mode)

        if mode == SIMULATION:
            return

        absmin, absmax = self._get_limits('writepv')

        self.valuetype = oneof(*range(absmin, absmax + 1))

        # Sets the target to the current beamstop readback state during
        # initialisation, instead of using what was in the Cache, so that Nicos
        # doesn't potentially think that the beamstop is being changed.
        self._setROParam(
            'target',
            int(self._get_pv('readpv', as_string=False))
        )

    def doRead(self, maxage=0):
        return int(self._get_pv('readpv', as_string=False))

    def doStart(self, value):
        if not self.isAtTarget(target=value):
            self.preparing = True
            self.status(0)
            self._put_pv('writepv', value)

    def doStop(self):
        # We are unable to stop a change when it is already in motion, so we
        # don't even try
        self.log.warning("Beamstop changer can't be stopped once a movement is started!")

    def doReset(self):
        self.preparing = False
        # I have seen, that sometimes the SPS doesn't actually execute the
        # command and then we end up in a slightly weird state. The user should
        # have an escape hatch.
        self._put_pv('resetpv', 1)

        self._setROParam(
            'target',
            int(self._get_pv('readpv', as_string=False))
        )

    def doStatus(self, maxage=0):
        try:
            status_code = self._get_pv('statuspv')
            status_msg = self._get_pv('statusmsgpv', as_string=True)

        except TimeoutError:
            return status.ERROR, 'timeout reading beamstop status'

        else:
            if self.preparing and status_code > 0:
                self._setROParam('preparing', False)

            if self.preparing and status_code == 0:
                return status.BUSY, 'Change requested'
            elif status_code == 0:
                return status.OK, ''
            return self._STATUS_CODES.get(status_code, status.UNKNOWN), status_msg

    def doIsAllowed(self, pos):
        (status_code, msg) = self.status(0)
        if status_code != status.OK:
            if msg:
                return (False, msg)
            if status_code == status.BUSY:
                return (False, 'Beamstop is already being changed')
            return (False, 'Changing the beamstop is not possible')
        return (True, '')

    # Disable Poller
    def doReadPollinterval(self):
        return None


class BeamstopMotorController(IsController, Device):
    """
    The motors `bsx` and `bsy` are used both to change the beamstop and to
    position it, once one of the beamstops is in position. Therefore, both
    changing of the beamstop, and moving either `bsx` or `bsy` should not
    happen simultaneously, as it could cause the change to fail. Unfortunately,
    this wasn't prohibited on the Electronic side, so the logic has been added
    here.
    """

    attached_devices = {
        'beamstop': Attach('Beamstop Changer Device', Beamstop),
        'bsx': Attach('Beamstop X-Axis Motor', Moveable),
        'bsy': Attach('Beamstop Y-Axis Motor', Moveable),
    }

    def isAdevTargetAllowed(self, adev, adevtarget):

        if adev == self._attached_beamstop:
            if multiStatus([self._attached_bsx, self._attached_bsy], 0)[0] != status.OK:
                return False, (f'{self._attached_bsx.name} or '
                               f'{self._attached_bsy.name} '
                                'is moving or has an error state.')

        elif adev == self._attached_bsx or adev == self._attached_bsy:
            beamstop_status = self._attached_beamstop.status(0)

            if beamstop_status[0] != status.OK:
                return False, (f'{self._attached_beamstop.name} '
                                'is currently changing the beamstop '
                                'or is in service mode.')

        return True, ''
