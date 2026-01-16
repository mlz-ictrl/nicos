# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Michael Wedel <michael.wedel@esss.se>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
"""
This module contains specific EPICS devices.
"""
from nicos import session
from nicos.core import Device, Param, pvname, status, usermethod
from nicos.core.constants import SIMULATION
from nicos.core.errors import AccessError
from nicos.core.params import Override, anytype, dictof, none_or
from nicos.devices.abstract import MappedMoveable
from nicos.devices.epics.pyepics import EpicsAnalogMoveable, EpicsDevice

from nicos_sinq.devices.epics.base import EpicsDigitalMoveableSinq


class EpicsMappedMoveable(MappedMoveable, EpicsDigitalMoveableSinq):
    """
    EPICS based implementation of MappedMoveable. Useful for PVs that contain
    enums or bools.
    """

    parameters = {
        'ignore_stop':
            Param('Whether to do anything when stop is called',
                  type=bool,
                  default=False,
                  userparam=False),
    }

    def doInit(self, mode):
        EpicsDigitalMoveableSinq.doInit(self, mode)
        MappedMoveable.doInit(self, mode)

    def doReadTarget(self):
        target_value = EpicsDigitalMoveableSinq.doReadTarget(self)

        # If this is from EPICS, it needs to be mapped, otherwise not
        if self.targetpv:
            return self._mapReadValue(target_value)

        return target_value

    def _readRaw(self, maxage=0):
        return EpicsDigitalMoveableSinq.doRead(self, maxage)

    def _startRaw(self, target):
        EpicsDigitalMoveableSinq.doStart(self, target)

    def doStop(self):
        if not self.ignore_stop:
            EpicsDigitalMoveableSinq.doStop(self)

    def doRead(self, maxage=0):
        return MappedMoveable.doRead(self, maxage)

    def doStart(self, target):
        MappedMoveable.doStart(self, target)


class EpicsCommandReply(EpicsDevice, Device):
    """
    Device to directly control devices connected to
    the asyn controller via EPICS.

    This device can issue commands to the asyn controller
    which in turn can operate the attached devices to the
    controller. The commands issued should adhere to the
    policies and syntax of the asyn controller.

    To do this via EPICS, two pvs can be provided:

    commandpv - PV that forwards the command to be executed
                to the controller
    replypv - PV that stores the reply generated from
              the execution of the command
    """

    parameters = {
        'commandpv':
            Param('PV to issue commands to the asyn controller',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'replypv':
            Param('PV that stores the reply generated from execution',
                  type=pvname,
                  mandatory=False,
                  settable=False,
                  userparam=False),
        'requires':
            Param('Access requirements for sending commands',
                  type=dictof(str, anytype),
                  userparam=False),
    }

    def _get_pv_parameters(self):
        pvs = {'commandpv'}

        if self.replypv:
            pvs.add('replypv')

        return pvs

    @usermethod
    def execute(self, command):
        """
        Issue and execute the provided command
        Returns the reply if the replypv is set
        """
        if self._mode == SIMULATION:
            return ''

        if self.requires:
            try:
                session.checkAccess(self.requires)
            except AccessError as err:
                raise AccessError(
                    self, 'cannot send command: %s' % err) from None

        # Send the command to the commandpv
        self._put_pv_blocking('commandpv', command)

        # If reply PV is set, return it's output
        return self._get_pv('replypv') if self.replypv else ''


class EpicsControlledAnalogMoveable(EpicsAnalogMoveable):
    '''
    Extends `EpicsAnalogMoveable` with additional PV's to check device
    readyness and to stop it.

    This class extends `EpicsAnalogMoveable` with additional functionality
    via two optional PVs. If none of these PVs are given in the setup file, this
    class is equivalent to its parent class EpicsAnalogMoveable.

    - `readypv`: If this parameter is 0, the device is busy and not able to
    receive a new movement command.

    - `stoppv`: Setting this parameter to 1 should stop the device. If this PV
    is not given, the `doStop` implementation of the base class is used, if
    the device is actually busy (target not equal to current position or
    `readypv == 0`)
    '''
    parameters = {
        'readypv': Param('Optional PV which should be 0 if the device is not ' \
                         'ready to move and 1 otherwise.',
                         type=none_or(pvname), mandatory=False, userparam=False),
        'stoppv': Param('Optional PV which is set to 1 when the device is stopped.',
                         type=none_or(pvname), mandatory=False, userparam=False),
    }

    def _get_pv_parameters(self):
        params = EpicsAnalogMoveable._get_pv_parameters(self)
        if self.readypv:
            params.add('readypv')
        if self.stoppv:
            params.add('stoppv')
        return params

    def doRead(self, maxage=0):
        return self._get_pv('readpv')

    def doIsAllowed(self, target):
        if self.doStatus(0)[0] != status.OK:
            return False, 'device not ready to start a movement'
        return True, ''

    def doStatus(self, maxage=0):
        # First read the status of the underlying device. If it is ok, check
        # the readypv
        (stat, msg) = EpicsAnalogMoveable.doStatus(self, maxage)
        if stat != status.OK:
            return stat, msg
        if self._get_pv('readypv') == 0:
            return status.BUSY, msg
        return status.OK, msg

    def doStop(self):
        if self.stoppv:
            self._put_pv('stoppv', 1)
        else:
            if self.readypv:
                if self.status()[0] == status.BUSY:
                    self.doStart(self.doRead())
            else:
                # Default behaviour of EpicsAnalogMoveable
                self.doStart(self.doRead())


class EpicsControlledDigitalMoveable(EpicsControlledAnalogMoveable):
    """
    `EpicsControlledAnalogMoveable` for integer values.
    """
    valuetype = int

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    def doRead(self, maxage=0):
        return int(EpicsControlledAnalogMoveable.doRead(self, maxage))
