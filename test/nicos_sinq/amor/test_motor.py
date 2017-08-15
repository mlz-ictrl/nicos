#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""
Module to test motor type devices at SINQ.

Every motor must also fulfill the demands of the Drivable feature.
The regression driver allows to simulate certain error behaviours
of a motor. The real, hardware,  position of a  motor is
hpos = sign*(val +zero)
"""

import pytest

from nicos.core import status
from nicos.core.errors import LimitError, PositionError
from test.utils import raises
from .utils import unit_value, is_at_target

session_setup = 'sinq_amor_movable'


class TestEpicsMotor(object):
    device = None

    asyn_dev_slot_mapping = {
        'com': 1, 'coz': 2, 'c3z': 3, 'cox': 4, 'eoz': 5, 'xlz': 6, 'eom': 7,
        'som': 9, 'soz': 10, 'stz': 11, 'sch': 12,
        'aom': 1, 'aoz': 2, 'atz': 3, 'mom': 5, 'moz': 6, 'mtz': 7, 'mty': 8,
        'fom': 9, 'ftz': 11,
        'd5v': 1, 'd5h': 2, 'd1l': 3, 'd1r': 4, 'd3t': 5, 'd3b': 6, 'd4t': 7,
        'd4b': 8, 'd1t': 9, 'd1b': 10, 'd2t': 11, 'd2b': 12,
    }

    def asyn_dev_controller(self):
        dev = self.device.name
        if dev.startswith('c') or dev.startswith('e') or dev.startswith(
                'x') or dev.startswith('s'):
            return 'serial1'
        elif dev.startswith('a') or dev.startswith('m') or dev.startswith('f'):
            return 'serial2'
        elif dev.startswith('d'):
            return 'serial3'

    @pytest.fixture(autouse=True)
    def initialize_device(self, sinq_motor, session):
        """
        Initialize the motor, and move it to 0
        """
        self.device = session.getDevice(sinq_motor)
        initial_pos = self.device.read(0)  # Original position of the device
        initial_offset = self.device.offset  # Original offset
        self.device.offset = 0.0
        self.device.maw(0.0)
        yield
        self.device.offset = initial_offset
        self.device.maw(initial_pos)
        self.device = None

    @pytest.mark.parametrize("offset", [0.1, -0.1])
    @pytest.mark.parametrize("target", [1, -1])
    def test_motor_operations(self, offset, target):
        """
        Test that after a device is moved to a certain position
        the new position read is the same as the one used with move
        """
        assert self.device.read(0) == 0

        # Set the offset
        offset = unit_value(offset, self.device.unit)
        self.device.offset = offset

        # Check the change in limits
        (usermin, usermax) = self.device.userlimits
        (absmin, absmax) = self.device.abslimits
        assert usermin == absmin + offset
        assert usermax == absmax + offset

        # Move to the new target
        target = unit_value(target, self.device.unit)
        self.device.maw(target)
        assert is_at_target(self.device, target)

    def test_limit_violations(self):
        """
        Test the limit violations after moving a motor beyond limits
        """
        (usrmin, usrmax) = self.device.userlimits
        assert raises(LimitError, self.device.maw, usrmin - 0.1)
        assert raises(LimitError, self.device.maw, usrmax + 0.1)

    def test_running_status(self):
        """
        Checks if the motor status equals "BUSY" when moving a motor
        """
        self.device.move(unit_value(1.0, self.device.unit))
        assert self.device.status(0)[0] == status.BUSY
        self.device.finish()

    def test_idle_status(self):
        """
        Tests if a motor moves to status "OK" after finishing a move.
        """
        self.device.maw(unit_value(1.0, self.device.unit))
        assert self.device.status()[0] == status.OK

    @pytest.mark.parametrize('fail_type', ['XS', 'XP', 'XH'])
    def test_failures(self, session, fail_type):
        """
        Check the motor start failure conditions.

        If motor is not set to recoverable, the target position
        should not be reached and if set to recoverable, the
        motor should reach the desired target

        Failures tested here:
        XS: Start fail,
        XP: Position fail and
        XH: Hardware fail
        """
        serial_controller = session.getDevice(self.asyn_dev_controller())
        slot = self.asyn_dev_slot_mapping[self.device.name]

        # Add a failure to device error list
        serial_controller.execute(fail_type + ' ' + str(slot))

        # Assert that the initial position of the device does not
        # change even after the move
        with pytest.raises(PositionError):
            target = unit_value(1.0, self.device.unit)
            self.device.maw(target)
            assert self.device.read(0) != target
            assert self.device.status()[0] == status.NOTREACHED

        # Set the device to be recoverable
        serial_controller.execute('RC ' + str(slot))

        # Assert that the device reaches it's final position
        target = unit_value(1.2, self.device.unit)
        self.device.maw(target)
        assert is_at_target(self.device, target)
