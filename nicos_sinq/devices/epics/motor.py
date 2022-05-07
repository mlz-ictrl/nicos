#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <mnichele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos import session
from nicos.core import MAIN, Param, pvname, status, usermethod

from nicos_ess.devices.epics import EpicsMotor as EssEpicsMotor


class EpicsMotor(EssEpicsMotor):
    parameters = {
        'can_disable': Param('Whether the motor can be enabled/disabled using '
                             'a PV or not.', type=pvname, mandatory=False,
                             settable=False, userparam=False),
        'auto_enable': Param('Automatically enable the motor when the setup is'
                             ' loaded', type=bool, default=False,
                             settable=False),
    }

    def doPreinit(self, mode):
        # We need to update the _record_field only if the motor has the PV,
        # else the device will fail to create
        if self.can_disable:
            self._record_fields['enable'] = ':Enable'
            self._record_fields['enable_rbv'] = ':Enable_RBV'
        EssEpicsMotor.doPreinit(self, mode)

    def _get_pv_name(self, pvparam):
        pv_name = EssEpicsMotor._get_pv_name(self, pvparam)
        return pv_name.replace('.:', ':')

    def doInit(self, mode):
        EssEpicsMotor.doInit(self, mode)
        if session.sessiontype == MAIN and self.auto_enable:
            self.enable()

    def doStatus(self, maxage=0):
        if self.can_disable:
            target = self._get_pv('enable')
            if target != self._get_pv('enable_rbv'):
                return status.BUSY, f'{"En" if target else "Dis"}abling motor'
            if not self._get_pv('enable_rbv'):
                return status.DISABLED, 'Motor is disabled'
        return EssEpicsMotor.doStatus(self, maxage)

    def _get_pv_parameters(self):
        pvs = EssEpicsMotor._get_pv_parameters(self)
        if self.can_disable:
            pvs.add('enable')
            pvs.add('enable_rbv')
        return pvs

    def doEnable(self, on):
        if self.can_disable:
            EssEpicsMotor.doEnable(self, on)
            self.status()
            self._cache.put(self, 'status', (status.BUSY,
                            f'{"En" if on else "Dis"}abling'))

    @property
    def isEnabled(self):
        """Shows if the motor is enabled or not"""
        if self.can_disable:
            val = self._get_pv('enable_rbv')
            return bool(val == 1)
        return True

    def doIsAllowed(self, target):
        if not self.isEnabled:
            return False, 'Motor disabled'
        return True, ''
