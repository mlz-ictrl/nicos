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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos import session
from nicos.core import multiStatus, status
from nicos.core.device import Attach, Moveable, Override
from nicos.devices.abstract import Motor


class InterfaceLogicalMotorHandler(Moveable):
    """
    This is the interface for a generic logical motor handler.
    Subclasses have to implement doRead() and _get_move_list()
    doRead() is different in that it returns a dictionary of
    motortype: position entries.

    Another thing a subclass has to define is  self._status_devs which is
    a list of those devices whose status needs to be queried in doStatus().
    This may be different from the list of attached devices when logical
    motors operate on conditional components.
    """
    hardware_access = False

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
        'unit': Override(mandatory=False, default='degree'),
    }

    valuetype = dict

    status_to_msg = {
        status.ERROR: 'Error in %s',
        status.BUSY: 'Moving: %s ...',
        status.WARN: 'Warning in %s',
        status.NOTREACHED: '%s did not reach target!',
        status.UNKNOWN: 'Unknown status in %s!',
        status.OK: 'Ready.'
    }

    def doPreinit(self, mode):
        self._logical_motors = {}
        self._motortypes = []

    def register(self, motortype, motor):
        self._motortypes.append(motortype)
        self._logical_motors[motortype] = motor

    def format(self, value, unit=False):
        try:
            fmtstr = ', '.join(f'{mt}=%({mt}).3f' for mt in value)
            ret = fmtstr % value
        except (TypeError, ValueError):
            ret = str(value)
        if unit and self.unit:
            return ret + ' ' + self.unit
        return ret

    def doReadFmtstr(self):
        return ', '.join(mt + '=%(' + mt + ').3f' for mt in self._motortypes)

    def _get_dev(self, dev):
        return getattr(self, '_attached_%s' % dev, None)

    def _read_dev(self, dev):
        dev = self._get_dev(dev)
        return dev.read(0) if dev else 0.0

    def _is_active(self, component):
        return component in session.loaded_setups

    def _getWaiters(self):
        devs = {dev: self._get_dev(dev) for dev in self._status_devs
                if self._get_dev(dev)}
        return devs

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        devs = self._getWaiters()
        st_devs = multiStatus(devs, 0)
        devs = [n for n, d in devs.items() if d.status()[0] == st_devs[0]]

        if st_devs[0] in self.status_to_msg:
            msg = self.status_to_msg[st_devs[0]]
            if '%' in msg:
                msg = msg % ', '.join(devs)
            return st_devs[0], msg

        return st_devs

    def doIsCompleted(self):
        # No attached devices, so have to manually check the doIsCompleted
        for dev in self._status_devs:
            dev = self._get_dev(dev)
            if dev and not dev.isCompleted():
                return False

        return True

    def doIsAllowed(self, targets):
        # Calculate the possible motor positions using these targets
        motor_targets = self._get_move_list(self._get_targets(targets))
        # Check if these positions are allowed and populate the
        # faults list with the motors that cannot be moved
        faults = []
        for motor, target in motor_targets:
            allowed, msg = motor.isAllowed(target)
            if not allowed:
                faults.append(motor.name)
                self.log.error('%s cannot be moved to %s, reason %s',
                               motor.name,
                               motor.format(target, motor.unit), msg)

        # Return false if some motors cannot reach their new target
        if faults:
            return False, '%s not movable!' % ', '.join(faults)

        # Return True if everything ok
        return True, ''

    def doStart(self, targets):
        for motor, target in self._get_move_list(self._get_targets(targets)):
            self.log.debug('New target for %s: %s', motor,
                           motor.format(target, motor.unit))
            motor.move(target)

    def _get_targets(self, targets):
        targets_dict = {}
        current = self.read(0)
        for mt in self._motortypes:
            target = targets.get(mt)
            if target is None:
                # If the target is not valid or not specified, fetch the
                # target from motor itself
                motor = self._logical_motors.get(mt)
                if not motor:
                    self.log.debug('Missing the logical motor %s! '
                                   'Using target = %s (current position) ',
                                   mt, current[mt])
                    targets_dict[mt] = current[mt]
                elif motor.target is not None:
                    targets_dict[mt] = round(motor.target or current[mt], 3)
                else:
                    targets_dict[mt] = current[mt]
            else:
                targets_dict[mt] = round(target, 3)

        # Return the dictionary of motortype mapped to their targets
        return targets_dict

    def _get_move_list(self, targets):
        # This is the method to override in order to make something happen
        return []


class LogicalMotor(Motor):
    """
    Class to represent a general logical motor. The motor type is
    always the name of the logical device
    """

    hardware_access = False

    parameter_overrides = {
        'unit': Override(mandatory=False, default='degree'),
        'target': Override(volatile=True),
        'abslimits': Override(mandatory=False, default=(-3.0, 3.0)),
        'userlimits': Override(mandatory=False, default=(-3.0, 3.0))
    }

    attached_devices = {
        'controller': Attach('Controller for the logical motors',
                             InterfaceLogicalMotorHandler)
    }

    def doInit(self, mode):
        self._attached_controller.register(self.name, self)

    def doRead(self, maxage=0):
        return self._attached_controller.read(maxage)[self.name]

    def doReadTarget(self):
        return self._getFromCache('target', self.doRead)

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        return self._attached_controller.status(maxage)

    def doIsAllowed(self, pos):
        return self._attached_controller.isAllowed({self.name: pos})

    def doIsCompleted(self):
        return self._attached_controller.isCompleted()

    def doStart(self, pos):
        self._attached_controller.start({self.name: pos})

    def doStop(self):
        if self.status(0)[0] == status.BUSY:
            self._attached_controller.stop()
            # Reset the target for this motor
            self._setROParam('target', self.doRead(0))
