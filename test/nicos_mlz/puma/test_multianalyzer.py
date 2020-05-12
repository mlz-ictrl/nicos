#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import ast
import os

import pytest

from nicos.core import status
from nicos.core.errors import InvalidValueError, LimitError

session_setup = 'multianalyzer'


class TestMultiAnalyzer(object):
    """Multi analyzer test class."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        """Prepare tests."""
        man = session.getDevice('man')
        man.reference()
        man.wait()
        for d in man._attached_rotations + man._attached_translations:
            d.speed = 0.

        yield

        man.stop()

    def test_neighbours_rot(self, session):
        """Check some positions of a rotation device."""
        ra1 = session.getDevice('ra1')

        assert not ra1.isAllowed(10)[0]
        assert not ra1.isAllowed(-45)[0]
        assert ra1.isAllowed(-25)[0]
        assert ra1.isAllowed(0)[0]

    def test_single_move(self, session):
        """Check not allowed if one device is moving."""
        ra1 = session.getDevice('ra1')
        ra2 = session.getDevice('ra2')

        ra1.speed = 0
        ra1.move(-0.3)
        ra1.motor.curstatus = status.BUSY, 'moving'
        assert ra2.isAllowed(-2)
        ra1.motor.curstatus = status.OK, ''
        ra1.wait()

    @pytest.mark.timeout(timeout=10, method='thread', func_only=True)
    def test_neighbours_trans(self, session):
        """Check some positions of translation devices."""
        man = session.getDevice('man')
        ta1 = session.getDevice('ta1')
        ta2 = session.getDevice('ta2')
        ra1 = session.getDevice('ra1')
        ra2 = session.getDevice('ra2')

        for d in ta1, ta2, ra1, ra2:
            assert d.speed == 0

        # Create collision free setup
        man.maw([-30, -10, 20] + [0] * 19)
        assert man.isAdevTargetAllowed(ta1, -10)[0]
        assert man.isAdevTargetAllowed(ta2, -30)[0]
        assert man.isAdevTargetAllowed(ra1, -60)[0]
        assert man.isAdevTargetAllowed(ra2, -60)[0]

        # Move crystals to positions where passing is not allowed
        man.maw([-30, -10, 30] + [0] * 8 + [-60, -60, -60] + [0] * 8)
        assert not man.isAdevTargetAllowed(ta1, -10)[0]
        assert not man.isAdevTargetAllowed(ta1, 0)[0]
        # approaching to neighbour is allowed
        assert man.isAdevTargetAllowed(ta1, -23)[0]
        assert man.isAdevTargetAllowed(ta2, -17)[0]
        # now too close
        assert not man.isAdevTargetAllowed(ta2, -18)[0]

        # rotate to a "passing" angle
        ra1.maw(-23.3)
        assert man.isAdevTargetAllowed(ta1, -20)[0]

        # rotate to non "passing" angle but come closer to 13 mm
        ra2.maw(-23.3)
        ta1.maw(2.9)
        ra2.maw(-60)
        ra1.maw(-28)
        assert man.isAdevTargetAllowed(ta2, 2.8)[0]

    def test_targets(self, session):
        """Check targets of the whole device."""
        man = session.getDevice('man')
        assert not man.isAllowed([300] + [0] * 10 + [1] + [0] * 10)[0]
        # To less arguments
        with pytest.raises(InvalidValueError):
            man.move([0] * 21)
        # To many arguments
        with pytest.raises(InvalidValueError):
            man.move([0] * 23)
        # one of the translations and one of the rotations out of range
        with pytest.raises(LimitError):
            man.move([300] * 22)

        dirname = os.path.dirname(__file__)
        # read good targets from file
        with open(os.path.join(dirname, 'man_test.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = ast.literal_eval(s)
                assert man.isAllowed(v)[0]

        # read bad targets from file
        with open(os.path.join(dirname, 'man_test_fail.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = ast.literal_eval(s)
                assert not man.isAllowed(v)[0]

    def test_movement(self, session):
        """Check some special movements."""
        man = session.getDevice('man')

        man.maw([0] * 22)
        assert man.read(0) == [0] * 22
        # already at position, so do nothing
        man.maw([0] * 22)

        man.maw([0] * 11 + [-i * 0.1 for i in range(11)])
        man.maw([0] * 22)
        man.maw([i for i in range(11)] + [-i * 0.1 for i in range(11)])

    def test_reset(self, session):
        """Check reset and reference of device."""
        man = session.getDevice('man')

        man.reset()
        man.wait()

        man.reference()
        man.wait()

        assert man.read(0) == [0] * 11 + [0.1] * 11

        # test move away from referenced system
        man.maw([1] * 11 + [0] * 11)
        assert man.read(0) == [1] * 11 + [0] * 11
