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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

# DEPRECATED VERSION OF THE SINQ EpicsMotor
# This version is currently kept around because the new SinqMotor relies on
# some features of the new generation of EPICS motor drivers. Since the EPICS
# motor drivers are not yet available for all motors used at SINQ, the old
# version of the SINQ EpicsMotor is kept around for the transition period.
# It will be deleted after all EPICS motor drivers are available.

from time import time as currenttime

from nicos.core import MASTER, Device, Param, status, Override
from nicos.core.constants import SIMULATION
from nicos.devices.epics.pyepics import PVMonitor, pvget
from nicos.devices.epics.pyepics.motor import EpicsMotor as EssEpicsMotor


class EpicsMotor(EssEpicsMotor):
    parameters = {
        'can_disable': Param('Whether the motor can be enabled/disabled using '
                             'a PV or not.', type=bool, mandatory=False,
                             settable=False, userparam=False),
        'auto_enable': Param('Automatically enable the motor when the setup is'
                             ' loaded', type=bool, default=False,
                             settable=False),
        'absolute_encoder': Param('Has an absolute encoder that can be reread',
                                  type=bool, default=False,
                                  settable=False),
    }

    parameter_overrides = {
        'precision': Override(settable=False, mandatory=True, volatile=False),
    }

    def doReadPrecision(self):
        pass

    def _get_pv_name(self, pvparam):
        if pvparam == 'enable' and self.can_disable:
            # If it is an ESS EpicsMotor enable points to .CNEN
            return self.motorpv + ':Enable'
        elif pvparam == 'enable_rbv':
            return self.motorpv + ':Enable_RBV'
        elif pvparam == 'reread_encoder':
            return self.motorpv + ':Reread_Encoder'
        else:
            return EssEpicsMotor._get_pv_name(self, pvparam)

    def _setMode(self, mode):
        if mode == MASTER and self.auto_enable:
            self.enable()
        return Device._setMode(self, mode)

    def doStatus(self, maxage=0):
        if self.can_disable:
            if not self._get_pv('enable_rbv'):
                return status.DISABLED, 'Motor is disabled'
        return EssEpicsMotor.doStatus(self, maxage)

    def _get_pv_parameters(self):
        pvs = EssEpicsMotor._get_pv_parameters(self)
        if self.can_disable:
            pvs.add('enable')
            pvs.add('enable_rbv')
        if self.absolute_encoder:
            pvs.add('reread_encoder')
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
        if self._mode != SIMULATION and self.can_disable:
            # I need to read this value also in simulation
            # mode when the PV class has been replaced by a
            # hardware stub. This is why I read directly here
            ename = self._get_pv_name('enable_rbv')
            val = pvget(ename)
            return bool(val == 1)
        return True

    def doIsAllowed(self, target):
        if not self.isEnabled:
            return False, 'Motor disabled'
        return True, ''

    def doIsAtTarget(self, pos, target):
        """
        This function overwrites EssEpicsMotor.doIsAtTarget and removes checking
        the MISS field of the motor record for the following reason:

        At SINQ, this device is only used for legacy motors (EL734 and Phytron).
        These motors are all hardcoded to have a precision of 0.001 in the EPICS
        motor record. This value is often way too small, which means that the
        motor record believes the motor missed its target position and therefore
        sets the MISS field to 1. On the NICOS side, this results in a lot of
        warnings. The proper fix would be to populate the SPDB
        (position_deadband) field of each motor in the EPICS substitution files,
        but this is a lot of work for legacy motors which are due for
        replacement anyway. So we just ignore the MISS field here.
        """
        if self._sim_intercept or target is None:
            return True

        # A motor can have a deadband which is larger than the precision. Hence,
        # the doIsAtTarget method is used in a modified form here
        return abs(target - pos) <= max(self.precision, self.position_deadband)

class AbsoluteEpicsMotor(EpicsMotor):
    """
    The instances of this class cannot be homed.
    """

    def doReference(self):
        self.log.warning('This motor does not require '
                         'homing - command ignored')


class EpicsMonitorMotor(PVMonitor, EpicsMotor):
    def doStart(self, target):
        try:
            self._put_pv_blocking('writepv', target, timeout=5)
        except Exception as e:
            # Use a generic exception to handle any EPICS binding
            self.log.warning(e)
            return
        if target != self.doRead():
            self._wait_for_start()

    def _on_status_change_cb(self, pvparam, value=None, char_value='', **kws):
        self._check_move_state_changed(pvparam, value)
        PVMonitor._on_status_change_cb(self, pvparam, value, char_value, **kws)

    def _check_move_state_changed(self, pvparam, value):
        # If the fields indicating whether the device is moving change then
        # the cache needs to be updated immediately.
        if pvparam in ['donemoving', 'moving']:
            self._cache.put(self._name, pvparam, value, currenttime())
