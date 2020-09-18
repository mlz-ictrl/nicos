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

"""NICOS tests for Eulerian cradle code."""

import pytest

from nicos.core.errors import NicosError

from test.utils import approx, raises

session_setup = 'euler'


class TestEulerian:

    @pytest.fixture()
    def eulerian(self, session):
        ec = session.getDevice('ec')
        session.getDevice('Sample').clear()
        ec.reflex1 = [1, 0, 0]
        ec.reflex2 = [0, 1, 0]
        ec.angles1 = [90, 45, 45, 60]
        ec.angles2 = [180, 45, 45, 60]
        yield ec

    @pytest.fixture()
    def not_init_eulerian(self, session):
        ec = session.getDevice('ec')
        ec.reflex1 = [0, 0, 0]
        ec.reflex2 = [0, 0, 0]
        ec.angles1 = [0, 0, 0, 0]
        ec.angles2 = [0, 0, 0, 0]
        yield ec

    def test_move(self, eulerian):
        ec = eulerian
        ec.maw([[1, 0, 0], [2, 1, 0]])
        assert ec.read(0) == ([1.0, 0.0, 0.0], [2.0, 1.0, 0.0])
        assert ec._attached_omega.read(0) == approx(-135., abs=0.0001)
        assert ec._attached_chi.read(0) == approx(135., abs=0.0001)

    def test_move_fail(self, not_init_eulerian):
        ec = not_init_eulerian
        assert raises(NicosError, ec.maw, ([[1, 0, 0], [2, 1, 0]]))

    def test_plane_calculation(self, eulerian, log):
        """Test calc_plane function."""
        with log.assert_msg_matches([r'found scattering plane',
                                     r'chi:[ ]*135.000 deg',
                                     r'omega:[ ]*-135.000 deg']):
            eulerian.calc_plane([1, 0, 0], [2, 1, 0])
        with log.assert_msg_matches([r'found scattering plane',
                                     r'chi:[ ]*135.000 deg',
                                     r'omega:[ ]*-135.000 deg']):
            eulerian.calc_plane([[1, 0, 0], [2, 1, 0]])

        assert raises(NicosError, eulerian.calc_plane, ([0, 0, 0], [0, 0, 0]))

    def test_plane_calculation_fail(self, not_init_eulerian):
        ec = not_init_eulerian
        assert raises(NicosError, ec.calc_plane, ([0, 0, 0], [0, 0, 0]))

    def test_or_calculation(self, eulerian):
        """Test calc_or function."""
        assert eulerian.calc_or().tolist() == [[approx(-0.862, abs=0.001),
                                                approx(0.0795, abs=0.001),
                                                approx(-0.5, abs=0.001)],
                                               [approx(0.362, abs=0.001),
                                                approx(0.787, abs=0.001),
                                                approx(-0.5, abs=0.001)],
                                               [approx(0.354, abs=0.001),
                                                approx(-0.612, abs=0.001),
                                                approx(-0.707, abs=0.001)]]
