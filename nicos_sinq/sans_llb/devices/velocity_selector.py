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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************
from enum import IntEnum

from nicos.core import Override, Param, listof, pvname, status, tupleof
from nicos.devices.epics.base import EpicsDigitalMoveable, EpicsMoveable
from nicos_sinq.devices.velocity_selector import VSForbiddenMoveable

class IocStates(IntEnum):
    # needs to be updated, if IOC changes state enum
    STARTUP = 0
    READY = 1
    MOVING = 2
    DISCONNECTED = 3
    CANNOT_CONNECT = 4
    CONNECTING = 5
    BRAKING = 6

class VelocitySelectorLLB(VSForbiddenMoveable):
    """
    SANS-LLB Velocity Selector from Airbus. Device contains maintenance readback values (vacuum etc.) as attributes.

    Shows/changes the VS rotation speed. Setting a speed of 0 will stop the VS entirely.
    When moving the target value has a window size that can be set via velocity_selector.target_window
    """
    parameters = {
        'vspv':
            Param('Name of the velocity selector record PV basis',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'forbidden_regions':
            Param('List of forbidden regions',
                  category='precisions',
                  unit='rpm',
                  type=listof(tupleof(int, int)),
                  mandatory=True),
        'vacuum':
            Param('Vacuum Level',
                  category='status',
                  type=float,
                  unit='mbar',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=True,
                  volatile=True),
        'rotor_temp':
            Param('Rotor Temperature',
                  category='status',
                  type=float,
                  unit='C',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=True,
                  volatile=True),
        'water_temp':
            Param('Water Temperature',
                  category='status',
                  type=float,
                  unit='C',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=True,
                  volatile=True),
        'vibration':
            Param('Vibration',
                  category='status',
                  type=float,
                  unit='mm/s',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=True,
                  volatile=True),
        'water_flow':
            Param('Water Flow',
                  category='status',
                  type=float,
                  unit='l/s',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=True,
                  volatile=True),

        'state':
            Param('State enum reported by IOC',
                  type=int,
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=False,
                  volatile=True),
        'target_rb': # TODO: rename rbv
            Param('Readback value of the target location from the VS',
                  type=int,
                  unit='rpm',
                  settable=False,
                  mandatory=False,
                  internal=True,
                  userparam=False,
                  volatile=True),

        'target_window':
            Param('Velocity window considered for target reached status',
                  type=int,
                  unit='rpm',
                  settable=True,
                  mandatory=False,
                  userparam=True,
                  volatile=True),
        }

    parameter_overrides = {
        # readpv and writepv are determined automatically from the base PV
        'readpv': Override(mandatory=False, userparam=False, settable=False),
        'writepv': Override(mandatory=False, userparam=False, settable=False),
    }

    _record_fields = {
        'readpv': 'ASPEED_RBV',
        'target_rb': 'RSPEED_RBV',
        'writepv': 'SPEED',
        'vacuum': 'VACUUM_RBV',
        'state': 'STATE_RBV',
        'rotor_temp': 'RTEMP_RBV',
        'water_temp': 'WOUTT_RBV',
        'vibration': 'VIBRT_RBV',
        'water_flow': 'WFLOW_RBV',
        'target_window': 'SPWND',
        }

    _cache_relations = {
        'readpv': 'value',
        'writepv': 'target'
    }

    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the motorpv parameter.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        motor_record_prefix = getattr(self, 'vspv')
        motor_field = self._record_fields.get(pvparam)

        if motor_field is not None:
            return ':'.join((motor_record_prefix, motor_field))

        return getattr(self, pvparam)

    def _get_status_parameters(self):
        params = EpicsDigitalMoveable._get_status_parameters(self)
        params.add('state')
        params.add('target_rb')
        return params

    def doIsAllowed(self, value):
        if value==0:
            return True, ''
        else:
            return VSForbiddenMoveable.doIsAllowed(self, value)

    def doReadTarget_Rb(self):
        return self._get_pv('target_rb')

    def doReadVacuum(self):
        return self._get_pv('vacuum')

    def doReadState(self):
        return self._get_pv('state')

    def doReadRotor_Temp(self):
        return self._get_pv('rotor_temp')

    def doReadWater_Temp(self):
        return self._get_pv('water_temp')

    def doReadVibration(self):
        return self._get_pv('vibration')

    def doReadWater_Flow(self):
        return self._get_pv('water_flow')

    def doReadTarget_Window(self):
        return self._get_pv('target_window')

    def doWriteTarget_Window(self, window):
        self._put_pv('target_window', window)

    def doStatus(self, maxage=0):
        current_state = IocStates(self.state)
        if current_state==IocStates.BRAKING:
            ioc_status = (status.BUSY, 'braking the velocity selector, wait until finished')
        elif self.target!=self.target_rb and self.target>0:
            ioc_status = (status.BUSY, 'destination send')
        elif current_state==IocStates.MOVING:
            ioc_status = (status.BUSY, 'changing velocity')
        elif current_state in [IocStates.STARTUP, IocStates.READY]:
            ioc_status = (status.OK, '')
        else:
            ioc_status = (status.ERROR, f'IOC reprts error status: {current_state}')
        return max(ioc_status, EpicsMoveable.doStatus(self, maxage))

    def doPoll(self, n, maxage):
        self.pollParams('vacuum', 'state', 'target_rb', 'rotor_temp', 'vibration', 'water_flow')
