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
#
# *****************************************************************************

import pytest

session_setup = 'hrpt'


class TestEpicsMotor:
    session = None

    @pytest.fixture(autouse=True)
    def initialize_device(self, session):
        """
        Initialize the motor, and move it to 0
        """
        self.session = session
        self.session.getDevice('d1l').curvalue = 0
        self.session.getDevice('d1r').curvalue = 0
        self.opening_to_motor_position =  self.session.getDevice(
            'slit1').conversion_factor /2
        self.motor_position_to_opening = 2 / self.session.getDevice(
            'slit1').conversion_factor

    def test_set_width(self):
        slit = self.session.getDevice('slit1')
        d1l = self.session.getDevice('d1l')
        d1r = self.session.getDevice('d1r')
        target = 5
        slit.width.maw(target)
        assert d1l.read() == target * self.opening_to_motor_position
        assert d1r.read() == target * self.opening_to_motor_position

    def test_read_width(self):
        slit = self.session.getDevice('slit1')
        d1l = self.session.getDevice('d1l')
        d1r = self.session.getDevice('d1r')
        target = 50
        d1l.maw(target)
        d1r.maw(target)
        assert slit.width.read() == target * self.motor_position_to_opening
