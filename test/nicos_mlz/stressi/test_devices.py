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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""STRESS-SPEC specific device tests."""

import pytest

session_setup = 'stressi'


class TestTransformedDevices:

    @pytest.fixture(scope='function')
    def device(self, session):
        tthm = session.getDevice('tthm_r')
        tthm._attached_dev.maw(50)
        yield tthm
        session.destroyDevice(tthm)

    def test_move(self, device, session):
        # rest initial read
        assert device._attached_dev.read(0) == 50
        assert device.read(0) == pytest.approx(77)

        # test read after moving of attached device
        device._attached_dev.maw(51)
        assert device.read(0) == pytest.approx(79)

        # test position of attached device after move
        device.maw(80)
        assert device._attached_dev.read(0) == pytest.approx(51.5)
