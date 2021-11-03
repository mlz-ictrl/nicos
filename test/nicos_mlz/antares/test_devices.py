#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

from test.utils import approx, raises

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
        assert raises(PositionError, mono.read, 0)
        assert mono.status(0)[0] == status.NOTREACHED

    def test_allowed_positions(self, mono):
        # check move to positions in the allowed range
        for pos in [x * 0.1 for x in (14, 30, 60)]:
            mono.maw(pos)
            assert mono.read(0) == approx(pos)

    def test_forbidden_positions(self, mono):
        # check move to positions outside the allowed range
        for pos in [1.3, 6.1]:
            assert raises(InvalidValueError, mono.move, pos)

    def test_in_out_position(self, mono):
        # mono is out, must be first moved in
        mono._attached_inout.maw('out')
        mono.maw(4.5)
        assert mono.read(0) == approx(4.5)
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

    def test_l_over_d(self, collimator):
        assert collimator._attached_d.read(0) == 2
        assert collimator.read(0) == 2500


class TestBlur:

    @pytest.fixture(scope='function')
    def blur(self, session):
        blur = session.getDevice('blur')
        yield blur
        session.destroyDevice(blur)

    def test_blur(self, blur):
        assert blur.read(0) == approx(4e-6)
        assert blur.unit == 'um'


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
