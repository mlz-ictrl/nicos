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

"""Module to test PUMA specific modules."""

import os

try:
    from string import maketrans  # pylint: disable=deprecated-module
except ImportError:
    maketrans = str.maketrans

from test.utils import approx

import pytest

session_setup = 'multidetector'


class TestMultiDetector(object):
    """Test class for the PUMA multidetector arranging device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        med = session.getDevice('med')

        yield

        med.stop()
        med.reset()
        med.reference()
        med.wait()

    def test_internal_functions(self, session):
        """Test class internal functions."""
        med = session.getDevice('med')
        assert not med._checkPositionReached(None, '')
        assert not med._checkPositionReached([], '')
        assert not med._checkPositionReached(range(11), '')

    def test_targets(self, session):
        """Test a set of targets."""
        med = session.getDevice('med')
        # To less arguments
        assert not med.isAllowed([0] * 21)[0]
        # To many arguments
        assert not med.isAllowed([0] * 23)[0]
        # Detector position outside limits
        assert not med.isAllowed([10] * 11 + [0] * 11)[0]

        assert med.isAllowed([-2.5 * i for i in range(11)] + [0] * 11)[0]
        # Some of the positions are to close together
        assert not med.isAllowed([-2.2 * i for i in range(11)] + [0] * 11)[0]

    def test_movement(self, session):
        """Test moves to different positions."""
        med = session.getDevice('med')
        med.maw([-2.5 * i for i in range(11)] + [0] * 11)
        # Code should return immediately
        med.move([-2.5 * i for i in range(11)] + [0] * 11)

        assert med.read(0) == [-2.5 * i for i in range(11)] + [0] * 11

        for r, e in zip(med._read_corr()[0], [-8.92, -9.39, -9.98, -10.70,
                                              -11.54, -12.5, -13.58, -14.81,
                                              -16.15, -17.61, -19.19]):
            assert r == approx(e, abs=0.01)

        dirname = os.path.dirname(__file__)
        # read good targets from file
        with open(os.path.join(dirname, 'med_test.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = map(float, s.translate(maketrans('][,', '   ')).split())
                assert med.isAllowed(list(v))[0]

        # read bad targets from file
        with open(os.path.join(dirname, 'med_test_fail.txt')) as f:
            for s in f.readlines():
                # convert stringified list to list avoiding use of 'eval'
                v = map(float, s.translate(maketrans('][,', '   ')).split())
                assert not med.isAllowed(list(v))[0]

    def test_reference(self, session):
        """Test different reference parameters."""
        med = session.getDevice('med')
        assert med.reference() == [-3.5 * (x + 1) for x in range(11)] + \
            [0] * 11
