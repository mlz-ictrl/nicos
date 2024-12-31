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
from numpy import pi, sqrt, tan

pytest.importorskip('epics')

session_setup = "sinq_amor"


class TestSlitDivergence:

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.slit = session.getDevice('slit1')
        # The divergence device is low level, but we want to test the aliased
        # devices
        session.getDevice('divergence')
        session.getDevice('d1l').maw(5)
        session.getDevice('d1r').maw(5)
        session.getDevice('d1b').maw(5)
        session.getDevice('d1t').maw(5)
        self.session = session

    def test_read_div_did(self):
        for top, bottom, div, did in [
            (1, 0, 45, 22.5),
            (tan(pi/8), -tan(pi/8), 0, 22.5),
            (1, -1, 0, 45)
        ]:
            self.slit.maw([5, 5, bottom, top])
            assert self.session.getDevice('did').read(0) == pytest.approx(did)
            assert self.session.getDevice('div').read(0) == pytest.approx(div)

    def test_set_div_did(self):
        for top, bottom, div, did in [
            (1, 0, 45, 22.5),
            (tan(pi/8), tan(pi/8), 45, 0),
            (tan(pi/8), -tan(pi/8), 0, 22.5),
            (1, -1, 0, 45),
        ]:
            self.session.getDevice('div').maw(div)
            self.session.getDevice('did').maw(did)

            _, _, bottom_, top_ = self.slit.read(0)
            assert top_ == pytest.approx(top)
            assert bottom_ == pytest.approx(bottom)

    def test_read_dih(self):
        for left, right, dih in [
            (1, 1, 90.0),
            (.5, .5, 53.13010),
            (sqrt(1./3), sqrt(1./3), 60)
        ]:
            self.slit.maw([left, right, 5, 5])
            assert self.session.getDevice('dih').read(0) == pytest.approx(dih)

    def test_set_dih(self):
        for left, right, dih in [
            (1, 1, 90.0),
            (.5, .5, 53.13010),
            (sqrt(1./3), sqrt(1./3), 60)
        ]:
            self.session.getDevice('dih').maw(dih)
            left_, right_, _, _ = self.slit.read(0)
            assert left_ == pytest.approx(left)
            assert right_ == pytest.approx(right)
