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

from nicos.core.errors import InvalidValueError, LimitError

session_setup = 'stressi'


class TestTransformedDevices:

    @pytest.fixture
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


def test_two_axis_slit(session):
    slit = session.getDevice('pss')
    assert slit() == [0, 0, 0, 0]
    assert slit.horizontal() == 0
    assert slit.vertical() == 0
    assert slit.x() == 0
    assert slit.y() == 0

    slit.maw((0, 0, 1, 1))

    slit.reset()

    pytest.raises(InvalidValueError, slit.isAllowed, (1, 2, 3, 4, 5))
    assert not slit.isAllowed([0, 0, -1, 1])[0]
    pytest.raises(LimitError, slit.move, [0, 0, -1, 1])

    slit.reference()

    assert slit.width() == 0
    assert slit.height() == 0
    assert slit.centerx() == 0
    assert slit.centery() == 0

    slit.width.maw(1)
    assert slit.width() == 1
    assert slit.horizontal() == 1

    slit.height.maw(1)
    assert slit.height() == 1
    assert slit.vertical() == 1

    assert slit() == [0, 0, 1, 1]

    assert slit.centerx() == 0
    assert slit.centery() == 0

    slit.centerx.maw(1)
    assert slit.centerx() == 1
    slit.centery.maw(1)
    assert slit.centery() == 1
