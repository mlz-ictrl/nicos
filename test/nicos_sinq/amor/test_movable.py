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

"""Module to test movable devices at SINQ."""

import pytest

try:
    from nicos_ess.essiip.devices.epics_extensions import HasSwitchPv
except ImportError:
    HasSwitchPv = None

from .utils import unit_value, is_at_target

session_setup = 'sinq_amor_movable'

@pytest.mark.skipif(HasSwitchPv is None, reason='epics not importable')
class TestMovable(object):
    device = None  # Holds the current device object under test

    @pytest.fixture(autouse=True)
    def initialize_device(self, sinq_movable, session):
        """
        Initialize the device, switch it on and move it to 0
        """
        self.device = session.getDevice(sinq_movable)

        # Check if the device is powered on
        if isinstance(self.device, HasSwitchPv):
            if not self.device.isSwitchedOn:
                self.device.switchOn()

        initial = self.device.read(0)  # Original position of the device
        self.device.maw(0.0)  # Move device to 0 for tests
        yield
        self.device.maw(initial)  # Reset the device to its original position
        self.device = None

    @pytest.mark.parametrize("target", [1.0, -1.0])
    def test_successful_drive(self, target):
        """
        Test that after a device is moved to a certain position
        the new position read is the same as the one used with move
        """
        target = unit_value(target, self.device.unit)
        self.device.maw(target)
        assert is_at_target(self.device, target)

    def test_interrupt_driving(self):
        """
        After starting to move a device to a position, it is interrupted.
        The result then should not reach the target
        """
        target = unit_value(1.5, self.device.unit)
        self.device.start(target)
        self.device.stop()
        assert not is_at_target(self.device, target)

    def test_interrupt_restart(self):
        """
        After starting to move a device to a position, it is interrupted.
        The device is then moved again to the position. The device then
        should move successfully and final position should read the target
        """
        target = unit_value(1.5, self.device.unit)
        self.device.start(target)
        self.device.stop()
        self.device.maw(target)
        assert is_at_target(self.device, target)
