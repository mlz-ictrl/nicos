# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""Test for the SAPHiR specific slit devices."""

import pytest

from nicos.commands.device import resetlimits
from nicos.core.errors import InvalidValueError

session_setup = 'slits'


class TestLShapeSlit:

    @pytest.fixture
    def slit(self, session):
        s = session.getDevice('s1')
        assert s.angle == 45
        assert s.opmode == 'centered'
        yield s
        s.opmode = 'centered'
        s.maw((0, 0))
        s._setROParam('min_opening', 0)

    def test_centered(self, slit):

        assert len(slit.valueInfo()) == 2

        slit.maw((0, 0))
        assert slit._attached_m1.read(0) == 0
        assert slit._attached_m2.read(0) == 0

        slit.maw((10, 10))

        assert slit._attached_m1.read(0) == pytest.approx(7.07107)
        assert slit._attached_m2.read(0) == pytest.approx(7.07107)

        pytest.raises(InvalidValueError, slit._getPositions, [1, 2, 4])

    def test_minopening(self, slit):
        # Set user limits to not allow negative moves of the m1, m2
        slit._attached_m1.userlimits = (0, 50)
        slit._attached_m2.userlimits = (0, 50)

        # Negative opening not allowed due to user limits of m1, m2
        assert not slit.isAllowed((-1, -1))[0]

        # Closing not allowed due to minimum opening > 0
        slit._setROParam('min_opening', 1)
        assert not slit.isAllowed((0, 0))[0]

        # Overlap not allowed due to user limits of m1, m2
        slit._setROParam('min_opening', -1)
        assert not slit.isAllowed((-1, -1))[0]

        resetlimits(slit._attached_m1)
        resetlimits(slit._attached_m2)

        # Overlap is allowed
        assert slit.isAllowed((-1, -1))[0]

        # Overlap would be to big
        assert not slit.isAllowed((-2, -2))[0]

    def test_offcentered_moves(self, slit):
        slit.opmode = 'offcentered'

        assert len(slit.valueInfo()) == 4

        assert slit.read(0) == [pytest.approx(0), pytest.approx(0),
                                pytest.approx(0), pytest.approx(0)]
        slit.maw((1, 1, 5, 5))
        assert slit.read(0) == [pytest.approx(1), pytest.approx(1),
                                pytest.approx(5), pytest.approx(5)]

        pytest.raises(InvalidValueError, slit._getPositions, [1, 2, 4])
