#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

import os

try:
    from string import maketrans  # pylint: disable=deprecated-module
except ImportError:
    maketrans = str.maketrans

from test.utils import raises

from nicos.core.errors import LimitError

import pytest

session_setup = 'multianalyzer'


class TestMultiAnalyzer(object):

    @pytest.yield_fixture(scope='function', autouse=True)
    def prepare(self, session):
        man = session.getDevice('man')
        session.getDevice('ra1').release()
        session.getDevice('ta1').release()
        man.reference()
        man.wait()

        yield

        man.stop()

    def test_neighbours(self, session):
        man = session.getDevice('man')
        # case which should normally not happen
        assert not man._checkTransNeighbour(11)

    def test_targets(self, session):
        man = session.getDevice('man')
        assert not man.isAllowed([300] + [0] * 10 + [1] + [0] * 10)[0]
        # To less arguments
        assert raises(LimitError, man, 'move', [0] * 21)
        # To many arguments
        assert raises(LimitError, man, 'move', [0] * 23)
        # one of the translations and one of the rotations out of range
        assert raises(LimitError, man, 'move', [300] * 22)

        dirname = os.path.dirname(__file__)
        # read good targets from file
        with open(os.path.join(dirname, 'man_test.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = map(float, s.translate(maketrans('][,', '   ')).split())
                assert man.isAllowed(list(v))[0]

        # read bad targets from file
        with open(os.path.join(dirname, 'man_test_fail.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = map(float, s.translate(maketrans('][,', '   ')).split())
                assert not man.isAllowed(list(v))[0]

    def test_movement(self, session):
        man = session.getDevice('man')

        man.maw([0] * 22)
        assert man.read(0) == [0] * 22
        # already at position, so do nothing
        man.move([0] * 22)

        man.maw([0] * 11 + [-i * 0.1 for i in range(11)])
        man.maw([0] * 22)
        man.maw([i for i in range(11)] + [-i * 0.1 for i in range(11)])

    def test_reset(self, session):
        man = session.getDevice('man')

        man.reset()
        man.wait()

        man.reference()
        man.wait()

        assert man.read() == [0] * 11 + [0.1] * 11

        # test move away from referenced system
        man.maw([1] * 11 + [0] * 11)
        assert man.read() == [1] * 11 + [0] * 11
