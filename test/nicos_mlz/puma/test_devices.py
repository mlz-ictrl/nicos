#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from test.utils import raises
from nicos.core.errors import LimitError, PositionError  # , MoveError

import pytest

session_setup = 'puma'


def test_comb_axis(session, log):
    phi = session.getDevice('phi')
    assert phi.iscomb is False

    # test in normal operation mode
    assert phi.read(0) == 0
    for t in [10, 0]:
        phi.maw(t)
        assert phi.read(0) == t

    assert phi._attached_fix_ax.read(0) == 0

    # test in combined mode
    assert phi._fixpos is None

    phi.iscomb = True
    assert phi.iscomb is True
    assert phi._fixpos == 0

    phi.maw(10)
    assert phi.read(0) == 10
    assert phi._attached_fix_ax.read(0) == -10

    with log.allow_errors():
        assert raises(LimitError, phi.move, 20)


def test_focus_axis(session):
    ax = session.getDevice('afpg')

    assert ax.read(0) == 0

    for t in [1, -1]:
        ax.maw(t)
        assert ax.read(0) == t

    # Check for the flat position target move
    ax.maw(0)
    assert ax.read(0) == ax.flatpos

    # Check the target changing if target outside [lowlimit, uplimit]
    ax.maw(ax.abslimits[0])
    assert ax.read(0) == ax.lowlimit
    ax.maw(ax.abslimits[1])
    assert ax.read(0) == ax.uplimit


def test_mtt_axis(session, log):
    ax = session.getDevice('mtt')

    assert ax.read(0) == 0

    ax.maw(0)
    assert ax.read(0) == 0
    for t in [-10, 0, ax.polypos + 1]:
        ax.maw(t)
        assert ax.read(0) == t

    # The sequence [ax.polypos - 1, ax.polypos + 1] could only be tested if
    # a simulation of a switch depending on a position of an other device is
    # available
    #
    # This test will check the fail due to this missing device
    # with log.allow_errors():
    #     assert raises(MoveError, ax.maw, (ax.polypos - 1))


class TestCad(object):
    """Test class for the PUMA coupled axis device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        cad = session.getDevice('cad')
        assert cad.read(0) == 0

        yield

        cad.maw(0)
        assert cad.read(0) == 0

    def test_reset(self, session):
        cad = session.getDevice('cad')
        cad.reset()

        # test reset if there is a small mismatch between both axes
        cad.tt.move(-2)
        cad.reset()
        assert cad.read(0) == 0

    def test_internals(self, session):
        cad = session.getDevice('cad')
        assert cad._checkReachedPosition(None) is False

    def test_move(self, session):
        cad = session.getDevice('cad')
        # test move in both directions and smaller than single step
        for p in [-10, -2, 0]:
            cad.maw(p)
            assert cad.read(0) == p

    def test_fails(self, session):
        th = session.getDevice('ath')
        th.maw(10)

        cad = session.getDevice('cad')

        assert raises(PositionError, cad.reset)

        assert raises(LimitError, cad.maw, -2)

        th.maw(0)
        th.userlimits = 0, 50
        assert raises(LimitError, cad.maw, -60)
        th.userlimits = th.abslimits
