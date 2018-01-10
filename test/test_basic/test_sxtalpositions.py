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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Tests for the single (4-circle and related) positions
"""

import pytest
import numpy as np

from nicos.devices.sxtal.goniometer.base import PositionFactory, typelist
from nicos.devices.sxtal.goniometer.posutils import equal

session_setup = 'sxtalpositions'


def getPositions():
    pos = []
    p0 = PositionFactory(
        ptype='n', theta=-7.23, omega=-10.00, chi=54.74, phi=100.00)
    pos.append(p0)
    pos.append(p0.With(chi=0))
    pos.append(p0.With(omega=0))
    pos.append(p0.With(phi=0))
    pos.append(p0.With(chi=90))
    pos.append(p0.With(theta=0))

    p0 = PositionFactory(
        ptype='k', theta=7.23, omega=-10.00, kappa=73.00, phi=100.00)

    pos.append(p0)
    pos.append(p0.With(kappa=0))
    pos.append(p0.With(omega=0))
    pos.append(p0.With(phi=0))
    pos.append(p0.With(theta=0))
    return pos

class TestPostions(object):

    @pytest.mark.parametrize('p',getPositions())
    @pytest.mark.parametrize('type1', typelist.keys())
    @pytest.mark.parametrize('type2', typelist.keys())
    def test_positions(self, p, type1, type2, session):
        # Set up a range of interesting positions
        type1 = type1.upper()
        if (type1 in ['C', 'B', 'L'] and getattr(p, 'theta', None) == 0):
            return
        if (type1 in ['L'] and hasattr(p, 'chi') and p.chi == np.pi/2):
            return

        p1 = p.asType(type1)

        type2 = type2.upper()
        if (type2 in ['C', 'B', 'L'] and getattr(p, 'theta', None) == 0):
            return
        if (type2 in ['L'] and hasattr(p, 'chi') and p.chi == np.pi/2):
            return
        p2 = p.asType(type2).asType(type1)

        assert equal(p1, p2)
