#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

""" Implementation of the AMOR virtual/logical motors.
The logical motors are m2t (monochromator 2 theta),
s2t (sample two theta) and ath (analyser theta). These
rotations not only involve rotations but the height of
components along the optical bench has to be changed
as well. The motors that move with the move of these
motors are:
soz, com, cox, coz, d1b, d2b, d3b, d4b, aoz, aom.
"""

import math

from nicos.core import Attach, Param, Override, status, oneof, dictwith
from nicos.core.device import Moveable
from nicos.devices.abstract import Motor
from nicos.core.utils import multiStatus
from nicos.pycompat import iteritems
from nicos_ess.devices.epics.motor import EpicsMotor
from nicos_sinq.amor.devices.component_handler import ComponentHandler

# Possible motor types
M2T = 'm2t'  # m2t - monochromator two theta
S2T = 's2t'  # s2t - sample two theta
ATH = 'ath'  # ath - analyzer theta
motortypes = [M2T, S2T, ATH]


class AmorLogicalMotorHandler(Moveable):
    """ Controller for the logical motors. Adds the possible dependent
    motors and distance devices via attached devices. This class has all the
    equations coded and can be used to read the positions of the logical
    motors or to calculate the positions of the real motors when the logical
    motor is to be moved.
    """

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
        'unit': Override(mandatory=False, default='degree'),
    }

    # The real motors and distance devices required
    attached_devices = {
        'soz': Attach('soz motor', EpicsMotor),
        'com': Attach('com motor', EpicsMotor),
        'cox': Attach('cox motor', EpicsMotor),
        'coz': Attach('coz motor', EpicsMotor),
        'd1b': Attach('d1b motor', EpicsMotor),
        'd2b': Attach('d2b motor', EpicsMotor),
        'd3b': Attach('d3b motor', EpicsMotor),
        'd4b': Attach('d4b motor', EpicsMotor),
        'aoz': Attach('aoz motor', EpicsMotor),
        'aom': Attach('aom motor', EpicsMotor),
        'd1t': Attach('d1t motor (only to read)', EpicsMotor),
        'd2t': Attach('d2t motor (only to read)', EpicsMotor),
        'd3t': Attach('d3t motor (only to read)', EpicsMotor),
        'd4t': Attach('d4t motor (only to read)', EpicsMotor),
        'sample': Attach('Sample position provider', ComponentHandler),
        'polarizer': Attach('Polarizer position provider', ComponentHandler),
        'slit1': Attach('Slit 1 position provider', ComponentHandler),
        'slit2': Attach('Slit 2 position provider', ComponentHandler),
        'slit3': Attach('Slit 3 position provider', ComponentHandler),
        'slit4': Attach('Slit 4 position provider', ComponentHandler),
        'analyzer': Attach('Analyzer position provider', ComponentHandler),
        'detector': Attach('Detector position provider', ComponentHandler),
    }

    valuetype = dictwith(m2t=float, s2t=float, ath=float)

    status_to_msg = {
        status.ERROR: 'Error in %s',
        status.BUSY: 'Moving: %s ...',
        status.WARN: 'Warning in %s',
        status.NOTREACHED: '%s did not reach target!',
        status.UNKNOWN: 'Unknown status in %s!',
        status.OK: 'Ready.'
    }

    def doInit(self, mode):
        # Collect all the logical motors in this variable
        self._logical_motors = {}

    def register(self, motortype, motor):
        self._logical_motors[motortype] = motor

    def doReadFmtstr(self):
        return ', '.join([mt + '=%(' + mt + ').3f' for mt in motortypes])

    def doRead(self, maxage=0):
        soz = self._attached_soz.read(0)
        dist = abs(self._attached_sample.read(0) -
                   self._attached_polarizer.read(0))
        tmp = soz / dist
        if abs(tmp) > 1e-4:
            actualm2t = math.degrees(-1 * math.atan(tmp))
        else:
            actualm2t = 0.0

        if self._attached_analyzer.active:
            aom = self._attached_aom.read(0)
            aoz = self._attached_aoz.read(0)
            sah = abs(self._attached_analyzer.read(0) -
                      self._attached_sample.read(0))
            actuals2t = math.degrees(math.atan((aoz - soz) / sah)) + actualm2t
            actualath = -1 * (actuals2t - actualm2t - aom)
        else:
            com = self._attached_com.read(0)
            actuals2t = com + actualm2t
            val = self._attached_aom.read(0)
            actualath = val - com

        return {
            M2T: actualm2t,
            S2T: actuals2t,
            ATH: actualath
        }

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        st_devs = multiStatus(self._adevs, maxage)
        devs = [dname for dname, d in iteritems(self._adevs)
                if d.status()[0] == st_devs[0]]

        if st_devs[0] in self.status_to_msg:
            msg = self.status_to_msg[st_devs[0]]
            if '%' in msg:
                msg = msg % ', '.join(devs)
            return st_devs[0], msg

        return st_devs

    def doIsAllowed(self, targets):
        # Calculate the possible motor positions using these targets
        motor_targets = self._get_move_list(self._get_targets(targets))

        # Check if these positions are allowed and populate the
        # faults list with the motors that cannot be moved
        faults = []
        for motor, target in motor_targets:
            allowed, _ = motor.isAllowed(target)
            if not allowed:
                faults.append(motor.name)
                self.log.error('%s cant be moved to %s; limits are %s', motor,
                               motor.format(target, motor.unit),
                               motor.abslimits)

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
        for mt in motortypes:
            target = targets.get(mt)
            if target is None:
                # If the target is not valid or not specified, fetch the
                # target from motor itself
                motor = self._logical_motors.get(mt)
                if not motor:
                    self.log.error('Missing the logical motor %s! '
                                   'Using target = %s (current position) ',
                                   mt, motor.format(current[mt]))
                    targets_dict[mt] = current[mt]
                else:
                    targets_dict[mt] = motor.target
            else:
                targets_dict[mt] = target

        # Return the dictionary of motortype mapped to their targets
        return targets_dict

    def _get_move_list(self, targets):
        # Equations to calculate the positions of the real motors to be moved
        # are implemented in this function

        self.log.debug('Recalculating with targets: %s', targets)
        positions = []

        # soz
        dist = abs(self._attached_sample.read(0) -
                   self._attached_polarizer.read(0))
        soz = dist * math.tan(math.radians(-1 * targets[M2T]))
        positions.append((self._attached_soz, soz))

        # slit 1 is before the monochromator and does not need to be
        # driven when m2t changes. This is here to make sure that d1b
        # is in a feasible position.
        if self._attached_slit1.active:
            mot = self._attached_d1t.read(0)
            val = -.5 * mot
            positions.append((self._attached_d1b, val))

        # slit 2
        if self._attached_slit2.active:
            dist = abs(self._attached_slit2.read(0) -
                       self._attached_polarizer.read(0))
            mot = self._attached_d2t.read(0)
            val = dist * math.tan(
                math.radians(-1 * targets[M2T])) - 0.5 * mot
            positions.append((self._attached_d2b, val))

        # slit 3
        if self._attached_slit3.active:
            dist = abs(self._attached_slit3.read(0) -
                       self._attached_polarizer.read(0))
            mot = self._attached_d3t.read(0)
            val = dist * math.tan(
                math.radians(-1 * targets[M2T])) - 0.5 * mot
            positions.append((self._attached_d3b, val))

        # Analyzer
        if self._attached_analyzer.active:
            com = targets[S2T] - targets[M2T] + 2 * targets[ATH]
            sah = abs(self._attached_analyzer.read(0) -
                      self._attached_sample.read(0))
            aoz = soz + sah * math.tan(
                math.radians(targets[S2T] - targets[M2T]))
            aom = targets[S2T] - targets[M2T] + targets[ATH]
            positions.append((self._attached_aoz, aoz))
            positions.append((self._attached_aom, aom))

            # Detector when analyzer present
            if self._attached_detector.active:
                sdh = abs(self._attached_detector.read(0) -
                          self._attached_sample.read(0))
                positions.append((self._attached_com, com))
                tmp = soz - aoz
                sqsum = sah * sah + tmp * tmp
                val = sah - math.sqrt(sqsum) + (sdh - math.sqrt(sqsum)) * (
                        math.cos(math.radians(com)) - 1.0)
                positions.append((self._attached_cox, -1 * val))
                val = aoz + (sdh - math.sqrt(sqsum)) * math.sin(
                    math.radians(com))
                positions.append((self._attached_coz, val))
        else:
            # Detector when no analyzer present
            com = targets[S2T] - targets[M2T]
            if self._attached_detector.active:
                positions.append((self._attached_com, com))
                dist = abs(self._attached_detector.read(0) -
                           self._attached_sample.read(0))
                val = -1 * dist * (math.cos(math.radians(com)) - 1.0)
                positions.append((self._attached_cox, val))
                val = dist * math.sin(math.radians(com)) + soz
                positions.append((self._attached_coz, val))

        # slit 4
        if self._attached_slit4.active:
            dist = abs(self._attached_slit4.read(0) -
                       self._attached_sample.read(0))
            mot = self._attached_d4t.read(0)
            if self._attached_analyzer.active:
                val = (soz + dist * math.tan(
                    math.radians(targets[S2T] - targets[M2T])) - 0.5 * mot)
            else:
                val = soz + dist * math.tan(math.radians(com)) - 0.5 * mot
            positions.append((self._attached_d4b, val))

        return positions


class AmorLogicalMotor(Motor):
    """ Class to represent the logical motor in AMOR. This motor has a
    type which can be one of the ath(analyzer theta), m2t(monochormator
    two theta) or s2t(sample two theta).
    """
    parameters = {
        'motortype': Param('Type of motor ath/m2t/s2t',
                           type=oneof(*motortypes), mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='degree'),
        'target': Override(volatile=True),
        'abslimits': Override(mandatory=False, default=(-3.0, 3.0)),
        'userlimits': Override(mandatory=False, default=(-3.0, 3.0))
    }

    attached_devices = {
        'controller': Attach('Controller for the logical motors',
                             AmorLogicalMotorHandler)
    }

    def doInit(self, mode):
        self._attached_controller.register(self.motortype, self)

    def doRead(self, maxage=0):
        return self._attached_controller.doRead(maxage)[self.motortype]

    def doReadTarget(self):
        return self._getFromCache('target', self.doRead)

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        return self._attached_controller.doStatus(maxage)

    def doIsAllowed(self, pos):
        return self._attached_controller.doIsAllowed({self.motortype: pos})

    def doStart(self, pos):
        self._attached_controller.doStart({self.motortype: pos})

    def doStop(self):
        if self.status(0)[0] == status.BUSY:
            self._attached_controller.stop()
            # Reset the target for this motor
            self._setROParam('target', self.doRead(0))
