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

"""Module to test custom specific modules."""

import pytest

from nicos.core.errors import LimitError, PositionError

from test.utils import raises, approx

session_setup = 'puma'


class TestCombAxis:

    @pytest.fixture(scope='function')
    def combaxis(self, session):
        phi = session.getDevice('phi')
        assert phi.iscomb is False

        yield phi

        phi.maw(0)
        phi.iscomb = False
        session.destroyDevice(phi)

    def test_normal(self, combaxis):
        # test in normal operation mode
        assert combaxis.read(0) == 0
        for t in [10, 0]:
            combaxis.maw(t)
            assert combaxis.read(0) == t

        assert combaxis._attached_fix_ax.read(0) == 0

    def test_combined_mode(self, combaxis, session, log):
        # test in combined mode
        assert combaxis._fixpos is None

        combaxis.iscomb = True
        assert combaxis.iscomb is True
        assert combaxis._fixpos == 0

        combaxis.maw(10)
        assert combaxis.read(0) == 10
        assert combaxis._attached_fix_ax.read(0) == -10

        with log.allow_errors():
            assert raises(LimitError, combaxis.move, 20)


class TestFocusAxis:

    @pytest.fixture(scope='function')
    def af(self, session):
        af = session.getDevice('af')
        af.maw(0)

        yield af

        session.destroyDevice(af)

    def test_move(self, af):
        for t in [-1, 1, 4.5]:
            af.maw(t)
            assert af.read(0) == approx(t, abs=af.precision)

    def test_flatpos(self, af):
        # Check for the flat position target move
        af.maw(0)
        assert af.read(0) == approx(af.flatpos, abs=af.precision)

    def test_target_outside_limit_move(self, af):
        # Check the target changing if target outside [lowlimit, uplimit]
        for t, c in zip(af.abslimits, [af.lowlimit, af.uplimit]):
            af.maw(t)
            assert af.read(0) == approx(c, abs=af.precision)


class TestMttAxis:

    @pytest.fixture(scope='function', autouse=True)
    def mtt(self, session):
        mtt = session.getDevice('mtt')
        assert mtt.read(0) == 0
        mtt.maw(0)
        assert mtt.read(0) == 0

        yield mtt

    def test_moves(self, mtt):
        for t in [-10, 0, mtt.polypos + 1]:
            mtt.maw(t)
            assert mtt.read(0) == t

        # The sequence [ax.polypos - 1, ax.polypos + 1] could only be tested if
        # a simulation of a switch depending on a position of an other device
        # is available
        #
        # This test will check the fail due to this missing device
        # with log.allow_errors():
        #     assert raises(MoveError, ax.maw, (ax.polypos - 1))


class TestCad:
    """Test class for the PUMA coupled axis device."""

    @pytest.fixture(scope='function')
    def cad(self, session):
        cad = session.getDevice('cad')
        assert cad.read(0) == 0

        yield cad

        cad.maw(0)
        assert cad.read(0) == 0

    def test_reset(self, cad):
        cad.reset()

        # test reset if there is a small mismatch between both axes
        cad.tt.move(-2)
        cad.reset()
        assert cad.read(0) == 0

    def test_internals(self, cad):
        assert cad._checkReachedPosition(None) is False

    def test_move(self, cad):
        # test move in both directions and smaller than single step
        for p in [-10, -2, 0]:
            cad.maw(p)
            assert cad.read(0) == p

    def test_fails(self, cad, session):
        th = session.getDevice('ath')
        th.maw(10)

        assert raises(PositionError, cad.reset)

        assert raises(LimitError, cad.maw, -2)

        th.maw(0)
        th.userlimits = 0, 50
        assert raises(LimitError, cad.maw, -60)
        th.userlimits = th.abslimits
