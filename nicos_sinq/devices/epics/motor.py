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
from nicos.core.constants import MASTER
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
    }

    parameter_overrides = {
        'errormsgpv': Override(settable=True),
        'errorbitpv': Override(settable=True),
        'reseterrorpv': Override(settable=True),
    }

    def doInit(self, mode):
        if mode == MASTER:
            # The PVs for the error message, the error bit and the error reset
            # are standardised for SINQ motors. Hence, if no custom PV names
            # have been set, the standard names are used.
            if not self.errormsgpv:
                self.errormsgpv = pvname(self.motorpv + '-MsgTxt')
            if not self.errorbitpv:
                self.errorbitpv = pvname(self.motorpv + ':StatusProblem')
            if not self.reseterrorpv:
                self.reseterrorpv = pvname(self.motorpv + ':Reset')
        return CoreEpicsMotor.doInit(self, mode)

    def _get_pv_parameters(self):
        pvs = CoreEpicsMotor._get_pv_parameters(self)
        pvs.add('can_disable')
        pvs.add('enable')
        pvs.add('enable_rbv')
        pvs.add('encoder_type')
        pvs.add('resolution')

        # Since the doInit function provides default PV names for these
        # parameters, they are added by default (instead of optionally as in
        # the parent EpicsMotor class)
        pvs.add('errormsgpv')
        pvs.add('errorbitpv')
        pvs.add('reseterrorpv')
        return pvs

    def _get_pv_name(self, pvparam):
        if pvparam == 'enable':
            return self.motorpv + ':Enable'
        elif pvparam == 'enable_rbv':
            return self.motorpv + ':EnableRBV'
        elif pvparam == 'can_disable':
            return self.motorpv + ':CanDisable'
        elif pvparam == 'encoder_type':
            return self.motorpv + ':EncoderType'
        elif pvparam == 'resolution':
            return self.motorpv + '.MRES'
        elif pvparam == 'errormsgpv' and not self.errormsgpv:
            return self.motorpv + '-MsgTxt'
        elif pvparam == 'errorbitpv' and not self.errorbitpv:
            return self.motorpv + ':StatusProblem'
        elif pvparam == 'reseterrorpv' and not self.reseterrorpv:
            return self.motorpv + ':Reset'
        else:
            return CoreEpicsMotor._get_pv_name(self, pvparam)

    def _register_pv_callbacks(self):
        CoreEpicsMotor._register_pv_callbacks(self)

        def update_position(**kw):
            self.read(0)

        def update_status(**kw):
            self.status(0)

        self._pvs['errormsgpv'].add_callback(update_status)
        self._pvs['enable_rbv'].add_callback(update_status)
        self._pvs['readpv'].add_callback(update_position)

    def doStatus(self, maxage=0):
        (stat, msg) = CoreEpicsMotor.doStatus(self, maxage)

        # If the motor reports an error, report the error rather than the fact
        # that the motor is disabled.
        if not self.isEnabled:
            if stat == status.ERROR:
                return (stat, 'Motor is disabled - ' + msg)
            return status.DISABLED, 'Motor is disabled'

        return (stat, msg)

    def doReadEncoder_Type(self, maxage=0):
        encoder_type = self._get_pv('encoder_type', as_string=True)
        if encoder_type.lower() in ('none', ''):
            return None
        return encoder_type

    def doReadCan_Disable(self, maxage=0):
        # This parameter should be reread every time this function is accessed.
        # If monitor=True (default parameter), the value is read from the
        # cache, which is not what we want!
        return self._get_pv('can_disable', use_monitor=False)

    def doEnable(self, on):
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
                self.log.warning('This motor cannot be disabled')

    @property
    def isEnabled(self):
        """Shows if the motor is enabled or not"""
        if not self._sim_intercept:
            return self._get_pv('enable_rbv') != 0
        return True

    def doIsAllowed(self, target):
        if not self.isEnabled:
            return False, 'Motor disabled'
        return True, ''

    def doReadPrecision(self):
        return self._get_pv('resolution')

    def doReference(self):
        if self.encoder_type == 'absolute':
            self.log.warning(
                'This motor does not require homing - command ignored')
        else:
            CoreEpicsMotor.doReference(self)

    def doReset(self):
        # Block the session until the error has actually been resetted
        self._put_pv_checked('reseterrorpv', 1)

    def doPoll(self, n, maxage):
        self.pollParams('can_disable', 'encoder_type')
        CoreEpicsMotor.doPoll(self, n, maxage)
