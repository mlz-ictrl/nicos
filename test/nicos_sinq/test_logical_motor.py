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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************
import pytest

from nicos.commands.device import maw

session_setup = 'sinq_logical_motor'


class TestLogicalMotors:

    @pytest.fixture(autouse=True)
    def initialize_device(self, session):
        self.a2 = session.getDevice('a2')
        self.a2w = session.getDevice('a2w')
        self.a2rot = session.getDevice('a2rot')
        self.d2l = session.getDevice('d2l')
        self.d2r = session.getDevice('d2r')

    def test_targets(self):
        # a2, a2w
        logical_targets = [
            (44, 10),
            (55, 10),
            (55, 20),
            (55, 5)]
        # a2rot, d2l, d2r
        motor_positions = [
            (44, -52.5, -42.5),
            (55, -41.5, -53.5),
            (55, -36.5, -48.5),
            (55, -44., -56.)
        ]
        # Sensible start positions
        self.a2rot.maw(40)
        self.d2l.maw(-58.5)
        self.d2r.maw(-40.5)
        assert abs(self.a2.read(0) - 40) < .01
        assert abs(self.a2w.read(0) - 6) < .01

        for log, pos in zip(logical_targets, motor_positions):
            maw(self.a2, log[0], self.a2w, log[1])
            assert abs(self.a2rot.read(0) - pos[0]) < .01
            assert abs(self.d2l.read(0) - pos[1]) < .01
            assert abs(self.d2r.read(0) - pos[2]) < .01
