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

from time import sleep

from nicos.core import Param, oneof, status

from nicos_sinq.devices.epics.motor import EpicsMotor


class ChangerMotor(EpicsMotor):
    """adds a feature to force reading the encoder"""

    def _get_pv_name(self, pvparam):
        if pvparam == 'forceread':
            return 'SQ:DMC:mcu2:READCH'
        return EpicsMotor._get_pv_name(self, pvparam)

    def _get_pv_parameters(self):
        pvs = EpicsMotor._get_pv_parameters(self)
        pvs.add('forceread')
        return pvs

    def doReset(self):
        """force reading the encoder once"""
        self._put_pv('forceread', 0)
        self._put_pv('forceread', 1)
        sleep(1)
        self.read(0)


class StickMotor(EpicsMotor):
    """
    This motor has two modes: normal and continuous. This class handles
    this speciality. In continuous mode, speed handling is different to.
    """

    parameters = {
        'opmode': Param('Operation mode of this motor',
                        type=oneof('normal', 'continuous'), userparam=True,
                        settable=True, volatile=True),
    }

    def _get_pv_name(self, pvparam):
        if pvparam == 'setmode':
            return 'SQ:DMC:mcu2:STICKMODE'
        elif pvparam == 'getmode':
            return 'SQ:DMC:mcu2:STICKMODE_RBV'
        elif pvparam == 'setspeed':
            return 'SQ:DMC:mcu2:STICKSPEED'
        elif pvparam == 'getspeed':
            return 'SQ:DMC:mcu2:STICKSPEED_RBV'
        return EpicsMotor._get_pv_name(self, pvparam)

    def _get_pv_parameters(self):
        pvs = EpicsMotor._get_pv_parameters(self)
        pvs.add('setmode')
        pvs.add('getmode')
        pvs.add('setspeed')
        pvs.add('getspeed')
        return pvs

    def doReadOpmode(self):
        val = self._get_pv('getmode')
        if val == 0:
            return 'normal'
        else:
            return 'continuous'

    def doSetOpmode(self, target):
        if target == 'normal':
            self._put_pv('setmode', 0)
        elif target == 'continuous':
            self._put_pv('setmode', 1)

    def doReadSpeed(self):
        if self.mode == 'continuous':
            return self._get_pv('getspeed')
        return EpicsMotor.doReadSpeed(self)

    def doWriteSpeed(self, newValue):
        if self.mode == 'continuous':
            self._put_pv('setspeed', newValue)
            return
        EpicsMotor.doWriteSpeed(self, newValue)

    def doIsAllowed(self, target):
        if self.mode == 'continuous':
            return False, 'Cannot set positions in continuous operation'
        return EpicsMotor.doIsAllowed(self, target)

    def doStatus(self, maxage=0):
        if self.mode == 'continuous':
            return status.OK, 'Running continuous'
        return EpicsMotor.doStatus(self, maxage)
