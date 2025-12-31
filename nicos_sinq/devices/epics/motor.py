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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from time import time

from nicos import session
from nicos.core import Param, status
from nicos.core.errors import UsageError
from nicos.core.params import Override, none_or, oneof, pvname
from nicos.devices.epics.motor import EpicsMotor as CoreEpicsMotor
from nicos_sinq.devices.dynamic_userlimits import DynamicUserlimits

class SinqMotor(DynamicUserlimits, CoreEpicsMotor):

    parameters = {
        'can_disable': Param('Whether the motor can be enabled/disabled using '
                             'a PV or not.', type=bool, mandatory=False,
                             settable=False, userparam=False, volatile=True),
        'encoder_type': Param('Encoder type', default=None, settable=False,
                              type=none_or(oneof('absolute', 'incremental')),
                              userparam=True, volatile=True),
    }

    parameter_overrides = {
        'precision': Override(volatile=True),
        # Necessary since DynamicUserlimits overrides the override in
        # CoreEpicsMotor
        'abslimits': Override(volatile=True, mandatory=False),
        'monitor': Override(default=True),
    }

    # Additional SINQ-specific record names which extend the basic motor record
    # defined in nicos.devices.epics.pyepics.motor.EpicsMotor
    _extension_records = {
        'enable': ':Enable',
        'enable_rbv': ':EnableRBV',
        'can_disable': ':CanDisable',
        'connected_rbv': ':Connected',
        'encoder_type': ':EncoderType',
        'reseterrorpv': ':Reset',
        'errormsgpv': '-MsgTxt',
    }

    # Maximum allowed delay for enabling / disabling a motor before an error
    # message is reported.
    _max_delay_enabling_disabling = 20

    def _get_pv_parameters(self):
        pvs = CoreEpicsMotor._get_pv_parameters(self)
        for param in self._extension_records.keys():
            pvs.add(param)
        return pvs

    def _get_pv_name(self, pvparam):
        if pvext := self._extension_records.get(pvparam):
            return self.motorpv + pvext
        return CoreEpicsMotor._get_pv_name(self, pvparam)

    def _get_status_parameters(self):
        params = CoreEpicsMotor._get_status_parameters(self)
        params.add('enable_rbv')
        params.add('connected_rbv')
        params.add('errormsgpv')
        return params

    def doInit(self, mode):
        DynamicUserlimits.doInit(self, mode)
        CoreEpicsMotor.doInit(self, mode)

    def doStatus(self, maxage=0):
        (stat, msg) = CoreEpicsMotor.doStatus(self, maxage)

        # Ignore errors if the motor is disconnected
        if not self.connected:
            return status.DISABLED, 'Motor is disconnected'

        # If the motor reports an error, report the error rather than the fact
        # that the motor is disabled.
        if not self.enabled:
            if stat == status.ERROR:
                return (stat, 'Motor is disabled - ' + msg)
            return status.DISABLED, 'Motor is disabled'

        return (stat, msg)

    # Overloaded from CoreEpicsMotor to add a hint if the motor is disabled
    # and to skip the log completely if the motor is disconnected
    def _log_status_error(self, stat, msg_txt):
        if not self.connected:
            return
        if not self.enabled:
            if stat == status.WARN:
                self.log.warning('Motor is disabled - %s', msg_txt)
            elif stat == status.ERROR:
                self.log.error('Motor is disabled - %s', msg_txt)
        else:
            if stat == status.WARN:
                self.log.warning(msg_txt)
            elif stat == status.ERROR:
                self.log.error(msg_txt)

    def doReadEncoder_Type(self, maxage=0):
        encoder_type = self._get_pv('encoder_type', as_string=True)
        if encoder_type.lower() in ('none', ''):
            return None
        return encoder_type

    def doReadCan_Disable(self, maxage=0):
        return self._get_pv('can_disable')

    # Provide SINQ-specific default PV names in case no explicit PV name has
    # been given in the setup file
    def doReadErrormsgpv(self):
        if pv := self._config.get('errormsgpv', None):
            return pv
        return pvname(self.motorpv + '-MsgTxt')

    def doReadReseterrorpv(self):
        if pv := self._config.get('reseterrorpv', None):
            return pv
        return pvname(self.motorpv + ':Reset')

    def doEnable(self, on):

        def enable_loop(self, on):
            CoreEpicsMotor.doEnable(self, on)
            enable_time = time()
            while time() < enable_time + self._max_delay_enabling_disabling:
                if self._get_pv('enable_rbv') == on:
                    return
                if self._cache is not None:
                    self._cache.put(self, 'status', (status.BUSY,
                                    f'{"En" if on else "Dis"}abling'))
                session.delay(self._base_loop_delay)
            msg = f'Motor could not be {"en" if on else "dis"}abled within ' \
                  f'{self._max_delay_enabling_disabling} seconds'
            raise TimeoutError(msg)

        if not self.connected:
            raise UsageError('Motor cannot be enabled / disabled because it is '
                             'disconnected from the controller!')

        if self.can_disable:
            done_moving = self._get_pv('donemoving')
            moving = self._get_pv('moving')
            if done_moving == 0 or moving != 0:
                raise UsageError('Motor cannot be disabled during movement!')
            enable_loop(self, on)
        else:
            if on == 0:
                raise UsageError('Motor cannot be disabled!')
            # The motor cannot be disabled, but it still can be enabled!
            enable_loop(self, on)

    @property
    def connected(self):
        """Shows if the motor is connected or not"""
        if not self._sim_intercept:
            return self._get_pv('connected_rbv') != 0
        return True

    @property
    def enabled(self):
        """Shows if the motor is enabled or not"""
        if not self._sim_intercept:
            return self._get_pv('enable_rbv') != 0
        return True

    def doIsAllowed(self, target):
        if not self.enabled:
            return False, 'Motor disabled'
        return True, ''

    def doReadPrecision(self):
        return self._get_pv('resolution')

    def doReference(self):
        if self.encoder_type == 'absolute':
            self.log.warning(
                'This motor does not require homing - command ignored')
            return
        return CoreEpicsMotor.doReference(self)

    def doReadUserlimits(self):
        return DynamicUserlimits.doReadUserlimits(self)

    def doWriteUserlimits(self, value):
        DynamicUserlimits.doWriteUserlimits(self, value)
        return CoreEpicsMotor.doWriteUserlimits(self, value)

    def doPoll(self, n, maxage):
        CoreEpicsMotor.doPoll(self, n, maxage)
        # No need to poll the userlimits - they are adjusted automatically
        # in DynamicUserlimits via a daemon callback mechanism
        self.pollParams('can_disable', 'encoder_type')
