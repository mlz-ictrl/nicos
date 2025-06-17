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

"""ANTARES specific devices tests."""

import pytest

from nicos.core import status
from nicos.core.errors import InvalidValueError, PositionError

session_setup = 'antares'


class TestMonochromator:

    @pytest.fixture(scope='function')
    def mono(self, session):
        mono = session.getDevice('mono')
        mono.maw(None)
        mono._attached_inout.maw('in')
        yield mono
        session.destroyDevice(mono)

    def test_mono(self, mono):
        # check if mono is in, but all motors at park positions
        assert mono._attached_inout.read(0) == 'in'
        pytest.raises(PositionError, mono.read, 0)
        assert mono.status(0)[0] == status.NOTREACHED

    def test_allowed_positions(self, mono):
        # check move to positions in the allowed range
        for pos in [x * 0.1 for x in (14, 30, 60)]:
            mono.maw(pos)
            assert mono.read(0) == pytest.approx(pos)

    def test_forbidden_positions(self, mono):
        # check move to positions outside the allowed range
        for pos in [1.3, 6.1]:
            pytest.raises(InvalidValueError, mono.move, pos)

    def test_in_out_position(self, mono):
        # mono is out, must be first moved in
        mono._attached_inout.maw('out')
        mono.maw(4.5)
        assert mono.read(0) == pytest.approx(4.5)
        assert mono._attached_inout.read(0) == 'in'

    def test_read_at_parking_position(self, mono):
        # Move to parking position
        mono.maw(None)
        assert mono.read(0) is None


class TestCollimator:

    @pytest.fixture(scope='function')
    def collimator(self, session):
        colli = session.getDevice('collimator')
        yield colli
        session.destroyDevice(colli)

    @pytest.fixture(scope='function')
    def pinhole(self, collimator):
        yield collimator._attached_d
        collimator._attached_d.maw(2)

    def test_l_over_d(self, collimator):
        assert collimator._attached_d.read(0) == 2
        assert collimator.read(0) == 2500

    @pytest.mark.parametrize('target', [0, 'park'])
    def test_invalid_pinholes(self, collimator, pinhole, target):
        # Test invalid values: 0 injects a division error, 'park' an invalid
        # value error
        pinhole.maw(target)
        assert collimator.read(0) == 0


class TestBlur:

    @pytest.fixture(scope='function')
    def blur(self, session):
        blur = session.getDevice('blur')
        yield blur
        session.destroyDevice(blur)

    @pytest.fixture(scope='function')
    def pinhole(self, blur):
        yield blur._attached_d
        blur._attached_d.maw(2)

    @pytest.fixture(scope='function')
    def length(self, blur):
        old_l = blur._attached_l.read(0)
        yield blur._attached_l
        blur._attached_l.maw(old_l)

    def test_blur(self, blur):
        assert blur.read(0) == pytest.approx(4e-6)
        assert blur.unit == 'um'

    @pytest.mark.parametrize('target', [0])
    def test_invalid_length(self, blur, length, target):
        length.maw(target)
        assert blur.read(0) == 0

    @pytest.mark.parametrize('target', ['park'])
    def test_invalid_pinholes(self, blur, pinhole, target):
        # Test invalid values: 'park' injects an invalid value error
        pinhole.maw(target)
        assert blur.read(0) == 0


class TestSelectorTilt:

    @pytest.fixture(scope='function')
    def tilt(self, session):
        selector = session.getDevice('selector')
        selector.maw(15000)
        tilt = session.getDevice('selector_tilt')
        yield tilt
        session.destroyDevice(tilt)

    def test_selector_tilt(self, tilt):
        assert tilt.read(0) == 0
        tilt.maw(1)


class TestToellner:

    @pytest.fixture(scope='function')
    def toellner(self, session):
        toellner = session.getDevice('toellner_dc')

        yield toellner

        session.destroyDevice(toellner)

    def test_toellner(self, toellner):
        assert toellner.read(0) == 0
        toellner.maw(10)
        assert toellner.read(0) == 10

        toellner.input_range = '5V'
        assert toellner._input_range == 5
        assert toellner.read(0) == 20
