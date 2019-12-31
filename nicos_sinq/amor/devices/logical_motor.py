#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import math

from nicos import session
from nicos.core import Attach, Override, Param, dictwith, oneof, status
from nicos.core.device import Moveable
from nicos.core.errors import PositionError
from nicos.core.utils import multiStatus
from nicos.devices.abstract import Motor
from nicos.pycompat import iteritems, number_types

from nicos_ess.devices.epics.motor import EpicsMotor
from nicos_sinq.amor.devices.component_handler import DistancesHandler

# Possible motor types
M2T = 'm2t'  # m2t - monochromator two theta
S2T = 's2t'  # s2t - sample two theta
ATH = 'ath'  # ath - analyzer theta
motortypes = [M2T, S2T, ATH]


class AmorLogicalMotorHandler(Moveable):
    """ Controller for the logical motors. This class has all the
    equations coded and can be used to read the positions of the logical
    motors or to calculate the positions of the real motors when the logical
    motor is to be moved.
    """

    parameter_overrides = {
        'fmtstr': Override(volatile=True),
        'unit': Override(mandatory=False, default='degree'),
    }

    # The real motors
    attached_devices = {
        'soz': Attach('soz motor', EpicsMotor, missingok=True),
        'com': Attach('com motor', EpicsMotor, missingok=True),
        'cox': Attach('cox motor', EpicsMotor, missingok=True),
        'coz': Attach('coz motor', EpicsMotor, missingok=True),
        'd1b': Attach('d1b motor', EpicsMotor, missingok=True),
        'd2b': Attach('d2b motor', EpicsMotor, missingok=True),
        'd3b': Attach('d3b motor', EpicsMotor, missingok=True),
        'd4b': Attach('d4b motor', EpicsMotor, missingok=True),
        'aoz': Attach('aoz motor', EpicsMotor, missingok=True),
        'aom': Attach('aom motor', EpicsMotor, missingok=True),
        'd1t': Attach('d1t motor (only to read)', EpicsMotor, missingok=True),
        'd2t': Attach('d2t motor (only to read)', EpicsMotor, missingok=True),
        'd3t': Attach('d3t motor (only to read)', EpicsMotor, missingok=True),
        'd4t': Attach('d4t motor (only to read)', EpicsMotor, missingok=True),
        'distances': Attach('Device that stores the distances',
                            DistancesHandler)
    }

    valuetype = dictwith(m2t=float, s2t=float, ath=float)

    status_devs = ['soz', 'com', 'cox', 'coz', 'd1b', 'd2b', 'd3b', 'd4b',
                   'aoz', 'aom']

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

    def _get_dev(self, dev):
        return getattr(self, '_attached_%s' % dev, None)

    def _read_dev(self, dev):
        dev = self._get_dev(dev)
        return dev.read(0) if dev else 0.0

    def _is_active(self, component):
        distances = self._attached_distances
        return component in session.loaded_setups and \
            isinstance(getattr(distances, component), number_types)

    def doRead(self, maxage=0):
        distances = self._attached_distances

        # Check if the sample and polariser distances are available
        if not isinstance(distances.sample, number_types):
            raise PositionError('Distances for sample and polariser unknown')

        soz = self._read_dev('soz')

        if not self._is_active('polariser'):
            actm2t = 0.0
        else:
            dist = abs(distances.sample - distances.polariser)
            tmp = soz / dist if dist else 0
            actm2t = math.degrees(-1 * math.atan(tmp)) if abs(tmp) > 1e-4 else 0.0

        if self._is_active('analyser'):
            aom = self._read_dev('aom')
            aoz = self._read_dev('aoz')
            sah = abs(distances.analyser - distances.sample)
            acts2t = math.degrees(math.atan((aoz - soz) / sah)) + actm2t
            actath = -1 * (acts2t - actm2t - aom)
        else:
            com = self._read_dev('com')
            acts2t = com + actm2t
            aom = self._read_dev('aom')
            actath = aom - com

        return {
            M2T: round(actm2t, 3),
            S2T: round(acts2t, 3),
            ATH: round(actath, 3)
        }

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        devs = {dev: self._get_dev(dev) for dev in self.status_devs
                if self._get_dev(dev)}
        st_devs = multiStatus(devs, 0)
        devs = [n for n, d in iteritems(devs) if d.status()[0] == st_devs[0]]

        if st_devs[0] in self.status_to_msg:
            msg = self.status_to_msg[st_devs[0]]
            if '%' in msg:
                msg = msg % ', '.join(devs)
            return st_devs[0], msg

        return st_devs

    def doIsCompleted(self):
        # No attached devices, so have to manually check the doIsCompleted
        for dev in self.status_devs:
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
        # Equations to calculate the positions of the real motors to be moved
        # are implemented in this function

        self.log.debug('Recalculating with targets: %s', targets)
        positions = []

        distances = self._attached_distances

        # soz
        dist = abs(distances.sample - distances.polariser)
        soz = dist * math.tan(math.radians(-1 * targets[M2T]))
        positions.append((self._get_dev('soz'), soz))

        # slit 1 is before the monochromator and does not need to be
        # driven when m2t changes. This is here to make sure that d1b
        # is in a feasible position.
        if self._is_active('slit1'):
            mot = self._read_dev('d1t')
            val = -.5 * mot
            positions.append((self._get_dev('d1b'), val))

        # slit 2
        if self._is_active('slit2'):
            dist = abs(distances.slit2 - distances.polariser)
            mot = self._read_dev('d2t')
            val = dist * math.tan(
                math.radians(-1 * targets[M2T])) - 0.5 * mot
            positions.append((self._get_dev('d2b'), val))

        # slit 3
        if self._is_active('slit3'):
            dist = abs(distances.slit3 - distances.polariser)
            mot = self._read_dev('d3t')
            val = dist * math.tan(
                math.radians(-1 * targets[M2T])) - 0.5 * mot
            positions.append((self._get_dev('d3b'), val))

        # Analyzer
        if self._is_active('analyser'):
            com = targets[S2T] - targets[M2T] + 2 * targets[ATH]
            sah = abs(distances.analyser - distances.sample)
            aoz = soz + sah * math.tan(
                math.radians(targets[S2T] - targets[M2T]))
            aom = targets[S2T] - targets[M2T] + targets[ATH]
            positions.append((self._get_dev('aoz'), aoz))
            positions.append((self._get_dev('aom'), aom))

            # Detector when analyzer present
            if self._is_active('detector'):
                sdh = abs(distances.detector - distances.sample)
                positions.append((self._get_dev('com'), com))
                tmp = soz - aoz
                sqrtsqsum = math.sqrt(sah * sah + tmp * tmp)
                val = sah - sqrtsqsum + (sdh - sqrtsqsum) * (
                        math.cos(math.radians(com)) - 1.0)
                positions.append((self._get_dev('cox'), -1 * val))
                val = aoz + (sdh - sqrtsqsum) * math.sin(math.radians(com))
                positions.append((self._get_dev('coz'), val))
        else:
            # Detector when no analyzer present
            com = targets[S2T] - targets[M2T]
            if self._is_active('detector'):
                positions.append((self._get_dev('com'), com))
                dist = abs(distances.detector - distances.sample)
                val = -1 * dist * (math.cos(math.radians(com)) - 1.0)
                positions.append((self._get_dev('cox'), val))
                val = dist * math.sin(math.radians(com)) + soz
                positions.append((self._get_dev('coz'), val))

        # slit 4
        if self._is_active('slit4'):
            dist = abs(distances.slit4 - distances.sample)
            mot = self._read_dev('d4t')
            if self._is_active('analyser'):
                val = (soz + dist * math.tan(
                    math.radians(targets[S2T] - targets[M2T])) - 0.5 * mot)
            else:
                val = soz + dist * math.tan(math.radians(com)) - 0.5 * mot
            positions.append((self._get_dev('d4b'), val))

        # Return rounded targets and remove unwanted positions
        return [(dev, round(targ, 3)) for dev, targ in positions if dev]


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

    def doIsCompleted(self):
        return self._attached_controller.doIsCompleted()

    def doStart(self, pos):
        self._attached_controller.doStart({self.motortype: pos})

    def doStop(self):
        if self.status(0)[0] == status.BUSY:
            self._attached_controller.stop()
            # Reset the target for this motor
            self._setROParam('target', self.doRead(0))
