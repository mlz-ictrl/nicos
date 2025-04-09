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
#   Edward Wall <edward.wall@psi.ch>
#
# *****************************************************************************

from time import sleep, time

from nicos.core import MASTER, Attach, Override, Param, intrange, oneof, \
    pvname, status
from nicos.core.device import Moveable
from nicos.core.errors import HardwareError, ModeError, UsageError
from nicos.core.mixins import CanDisable
from nicos.devices.epics.pyepics.motor import EpicsMotor as CoreEpicsMotor
from nicos.devices.epics.pyepics.pyepics import EpicsDevice
from nicos.devices.generic.switcher import Switcher

from nicos_sinq.devices.epics.motor import SinqMotor


class CHSwitcher(Switcher):

    def doStatus(self, maxage=0):
        state, _ = self._attached_moveable.status(maxage)
        if state == status.DISABLED:
            return status.DISABLED, f"{self._attached_moveable.name} is disabled"
        return Switcher.doStatus(self, maxage)


class StickMotorVelo(EpicsDevice, Moveable):
    """
    With this Epics device, the velocity of the motor during its velocity mode
    can be modified. This velocity is different from the speed parameter that
    can be modified when the motor is in its normal positioning mode. This
    parameter can't be set when the motor is not in its velocity mode.
    """

    parameters = {
        'motorpv':
            Param('Name of the motor record PV.',
                  type=pvname,
                  mandatory=True,
                  settable=False,
                  userparam=False),
        'enabled':
            Param('Whether or not this device is currently enabled.',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  userparam=False,
                  internal=True,
                  volatile=True),
    }

    parameter_overrides = {
        'unit': Override(default='%', internal=True, settable=False,
                         userparam=True, mandatory=False, volatile=True),
        'target': Override(default='20', volatile=True),
    }

    valuetype = intrange(0, 100)

    def _get_pv_parameters(self):
        return {
            'setmode',
            'getmode',
            'velomodespeed',
            'velomodespeedrbv',
            'enable_rbv',
            'maxspeed',
            'speed',
        }

    def _get_pv_name(self, pvparam):
        if pvparam == 'setmode':
            return self.motorpv + ':MODE'
        elif pvparam == 'getmode':
            return self.motorpv + ':MODE_RBV'
        elif pvparam == 'velomodespeed':
            return self.motorpv + ':SPEED'
        elif pvparam == 'velomodespeedrbv':
            return self.motorpv + ':SPEED_RBV'
        elif pvparam == 'enable_rbv':
            return self.motorpv + ':EnableRBV'
        elif pvparam == 'maxspeed':
            return self.motorpv + '.VMAX'
        elif pvparam == 'speed':
            return self.motorpv + '.VELO'
        return EpicsDevice._get_pv_name(self, pvparam)

    def _register_pv_callbacks(self):
        EpicsDevice._register_pv_callbacks(self)

        def update_position(**kw):
            self.read(0)

        def update_status(**kw):
            self.status(0)

        self._pvs['velomodespeedrbv'].add_callback(update_position)
        self._pvs['getmode'].add_callback(update_status)
        self._pvs['enable_rbv'].add_callback(update_status)

    def doRead(self, maxage=0):
        return self._get_pv('velomodespeedrbv')

    def doStart(self, value):
        self._put_pv('velomodespeed', value)

    def doReadTarget(self):
        self._get_pv('velomodespeed')

    def doStatus(self, maxage=0):
        if not self.enabled:
            return status.DISABLED, ''
        return status.BUSY, 'In Velocity Mode'

    def doReadUnit(self):
        maxspeed = self._get_pv('maxspeed', use_monitor=False)
        baseunit = self._get_pvctrl('speed', 'units', '')
        return f'% of {maxspeed} {baseunit}s'

    def doIsAllowed(self, pos):
        if not self.enabled:
            return False, 'Can only change when in Velocity Mode'
        return True

    def doReadEnabled(self):
        return self._get_pv('enable_rbv') and self._get_pv('getmode')

    def doWriteEnabled(self, on):
        self._put_pv('setmode', on)


class _StickModeSwitcher(CanDisable, Moveable):
    """
    Due to the cyclic dependency, this empty class is used to check that the
    Switcher device that is attached to StickMotor via the
    `_register_switcher_device` method is of the correct type.
    """

    attached_devices = {
        'velocity': Attach('Same Motor in Velocity Mode', StickMotorVelo),
    }


class StickMotor(SinqMotor):
    """
    This is a modified version of SinqMotor, which forbids the use of many of
    the typical motor methods in the case that the motor has been switched to
    its velocity mode.
    """

    parameters = {
        'enabled':
            Param('Whether or not this device is currently enabled.',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  userparam=False,
                  internal=True,
                  volatile=True),
    }

    attached_devices = {
        'switcher': Attach('Controls whether in Positioning or Velocity Mode', _StickModeSwitcher),
    }

    def doStatus(self, maxage=0):
        sw_state, sw_msg = self._attached_switcher.status(maxage)
        velo_state, velo_msg = self._attached_switcher._attached_velocity.status(maxage)

        if sw_state == status.BUSY:
            return (sw_state, sw_msg)

        if velo_state == status.BUSY:
            return (velo_state, velo_msg)

        return SinqMotor.doStatus(self, maxage)

    def doEnable(self, on):
        raise ModeError(f"Device must be en/disabled via device '{self._attached_switcher.name}'.")

    def doReadEnabled(self):
        velo_state, _ = self._attached_switcher._attached_velocity.status(0)
        return self._get_pv('enable_rbv') and velo_state == status.DISABLED

    def doWriteEnabled(self, on):
        done_moving = self._get_pv('donemoving')
        moving = self._get_pv('moving')
        if done_moving == 0 or moving != 0:
            raise UsageError(f"'{self.name}' cannot be disabled during movement!")
        CoreEpicsMotor.doEnable(self, on)

    def _throw_mode_error(self, msg):
        raise ModeError(('Enable motor and switch to positioning mode via '
                         f'\'{self._attached_switcher.name}\' to {msg}.'))

    # The following methods are overwritten to make sure that they cannot be
    # used when the motor is in velocity mode. (this device will appear "busy"
    # when velocity mode is activated)
    def doStart(self, target):
        if not self.enabled:
            self._throw_mode_error('move the motor')
        SinqMotor.doStart(self, target)

    def doWriteOffset(self, value):
        if not self.enabled:
            self._throw_mode_error('adjust offset')
        SinqMotor.doWriteOffset(self, value)

    def doStop(self):
        if not self.enabled:
            self._throw_mode_error('send Stop command')
        SinqMotor.doStop(self)

    def doReference(self):
        if not self.enabled:
            self._throw_mode_error('run Reference Run')
        SinqMotor.doReference(self)

    def doSetPosition(self, pos):
        if not self.enabled:
            self._throw_mode_error('Set Position')
        SinqMotor.doSetPosition(self, pos)


class StickModeSwitcher(_StickModeSwitcher):
    """
    This motor has two modes: position and velocity. This class handles the
    switching between these two modes and provides enabling/disabling
    functionality for the motor.
    """

    parameters = {
        'changing_mode':
            Param('Whether or not a mode change was started',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  internal=True,
                  userparam=False),
        'enabling':
            Param('Whether or not the motor is being enabled/disabled',
                  type=bool,
                  mandatory=False,
                  settable=True,
                  internal=True,
                  userparam=False),
        'enabled':
            Param('Whether or not this device is currently enabled',
                  type=bool,
                  mandatory=False,
                  settable=False,
                  userparam=False,
                  internal=True,
                  volatile=True),
    }

    parameter_overrides = {
        'unit': Override(default='', internal=True, settable=False,
                         userparam=False, mandatory=False),
    }

    attached_devices = {
        'position': Attach('Normal Motor', StickMotor),
    }

    valuetype = oneof('position', 'velocity')

    def doInit(self, mode):
        if mode == MASTER:
            self.changing_mode = False
            self.enabling = False

    def doRead(self, maxage=0):
        if self._attached_position.enabled:
            return 'position'
        elif self._attached_velocity.enabled:
            return 'velocity'
        return None

    def _disable_velo_mode(self):
        pos = self._attached_position
        vel = self._attached_velocity

        vel.enabled = False

        # Unfortunately, the way the motor works, there is no
        # other way to check that velocity mode has been disabled
        # except to wait until it stops moving.
        p1 = pos.read()
        t = time()
        while True:
            sleep(1)
            p2 = pos.read()
            if p2 == p1:
                break
            if time() - t > 20: # Wait at most 20 seconds
                raise HardwareError('Failed to disable Velocity Mode')
            p1 = p2

        # The firmware requires that the motor is disabled
        # after the mode is changed back to position mode.
        self._enable_pos_mode(False)

    def _enable_pos_mode(self, on):
        pos = self._attached_position

        pos.enabled = on

        t = time()
        while True:
            sleep(1)
            if pos.enabled == on:
                break
            if time() - t > 20: # Wait at most 20 seconds
                msg = 'en' if on else 'dis'
                raise HardwareError(f"Failed to {msg}able '{pos.name}'")

    def doStart(self, value):
        if not self.enabled or self.read() == value:
            return

        self.changing_mode = True
        self.status()

        try:

            if value == 'velocity':
                self._attached_velocity.enabled = True
            else:
                self._disable_velo_mode()
                self._enable_pos_mode(True)

            self.changing_mode = False
            self.status()

        except HardwareError as exc:
            self.changing_mode = False
            self.status()
            raise exc

    def doStatus(self, maxage=0):
        if self.changing_mode:
            return status.BUSY, 'Switching Mode'
        if self.enabling:
            return status.BUSY, 'Enabling/Disabling Motor'
        if not self.enabled:
            return status.DISABLED, ''
        return status.OK, ''

    def doEnable(self, on):
        self.enabling = True
        self.status()

        try:

            if self.target == 'position':
                self._enable_pos_mode(on)

            else:
                if on:
                    self._attached_velocity.enabled = True
                else:
                    self._disable_velo_mode()

            self.enabling = False
            self.status()

        except (UsageError, HardwareError) as exc:
            self.enabling = False
            self.status()
            raise exc

    def doReadEnabled(self):
        return self._attached_position.enabled or self._attached_velocity.enabled
