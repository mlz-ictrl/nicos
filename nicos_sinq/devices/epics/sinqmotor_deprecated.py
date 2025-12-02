# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from nicos.core import Param, status
from nicos.core.errors import UsageError
from nicos.core.params import Override, none_or, oneof, pvname
from nicos.devices.epics.pyepics.motor import EpicsMotor as CoreEpicsMotor


class SinqMotor(CoreEpicsMotor):

    parameters = {
        'can_disable': Param('Whether the motor can be enabled/disabled using '
                             'a PV or not.', type=bool, mandatory=False,
                             settable=False, userparam=False, volatile=True),
        'encoder_type': Param('Encoder type', default=None, settable=False,
                              type=none_or(oneof('absolute', 'incremental')),
                              userparam=True, volatile=True),
        'connected': Param('Whether the motor is connected or not.', type=bool,
                           mandatory=False, settable=False, userparam=True,
                           volatile=True),
    }

    parameter_overrides = {
        'precision': Override(volatile=True),
    }

    # Additional SINQ-specific record names which extend the basic motor record
    # defined in nicos.devices.epics.pyepics.motor.EpicsMotor
    _extension_records = {
        'enable': ':Enable',
        'enable_rbv': ':EnableRBV',
        'can_disable': ':CanDisable',
        'connected_rbv': ':Connected',
        'encoder_type': ':EncoderType',
        'errorbitpv': ':StatusProblem',
        'reseterrorpv': ':Reset',
        'errormsgpv': '-MsgTxt',
    }

    def _get_pv_parameters(self):
        pvs = CoreEpicsMotor._get_pv_parameters(self)
        for param in self._extension_records.keys():
            pvs.add(param)
        return pvs

    def _get_pv_name(self, pvparam):
        if pvext := self._extension_records.get(pvparam):
            return self.motorpv + pvext
        return CoreEpicsMotor._get_pv_name(self, pvparam)

    def _register_pv_callbacks(self):
        CoreEpicsMotor._register_pv_callbacks(self)

        def update_position(**kw):
            self.read(0)

        def update_status(**kw):
            self.status(0)

        self._pvs['errormsgpv'].add_callback(update_status)
        self._pvs['enable_rbv'].add_callback(update_status)
        self._pvs['connected_rbv'].add_callback(update_status)
        self._pvs['readpv'].add_callback(update_position)

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

    def doReadEncoder_Type(self):
        encoder_type = self._get_pv('encoder_type', as_string=True)
        if encoder_type.lower() in ('none', ''):
            return None
        return encoder_type

    def doReadCan_Disable(self):
        # This parameter should be reread every time this function is accessed.
        # If monitor=True (default parameter), the value is read from the
        # cache, which is not what we want!
        return self._get_pv('can_disable', use_monitor=False)

    # Provide SINQ-specific default PV names in case no explicit PV name has
    # been given in the setup file
    def doReadErrormsgpv(self):
        if pv := self._config.get('errormsgpv'):
            return pv
        return pvname(self.motorpv + '-MsgTxt')

    def doReadErrorbitpv(self):
        if pv := self._config.get('errorbitpv'):
            return pv
        return pvname(self.motorpv + ':StatusProblem')

    def doReadReseterrorpv(self):
        if pv := self._config.get('reseterrorpv'):
            return pv
        return pvname(self.motorpv + ':Reset')

    def doEnable(self, on):
        if not self.connected:
            raise UsageError('Motor cannot be enabled / disabled because it is '
                             'disconnected from the controller!')

        if self.can_disable:
            done_moving = self._get_pv('donemoving')
            moving = self._get_pv('moving')
            if done_moving == 0 or moving != 0:
                raise UsageError('Motor cannot be disabled during movement!')
            else:
                CoreEpicsMotor.doEnable(self, on)
                self.status()
                self._cache.put(self, 'status', (status.BUSY,
                                f'{"En" if on else "Dis"}abling'))
        else:
            if on:
                # The motor cannot be disabled, but it still can be enabled!
                CoreEpicsMotor.doEnable(self, on)
                self.status()
                self._cache.put(self, 'status', (status.BUSY,
                                f'{"En" if on else "Dis"}abling'))
            else:
                raise UsageError('Motor cannot be disabled!')

    def doReadConnected(self, maxage=0):
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

    def doReset(self):
        self._put_pv_checked('reseterrorpv', 1)

    def doPoll(self, n, maxage):
        CoreEpicsMotor.doPoll(self, n, maxage)
        self.pollParams('can_disable', 'encoder_type')
