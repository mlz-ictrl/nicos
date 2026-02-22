# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""NICOS MLZ CCR test suite."""

import pytest

session_setup = 'ccr'


class TestCCR:

    @pytest.mark.parametrize('mode', ['stick', 'tube', 'both'])
    def test_ccr(self, session, mode):
        ccr = session.getDevice('T_ccr')
        ccr.regulationmode = mode
        assert ccr.regulationmode == mode
        assert ccr.read(0) == pytest.approx(10, abs=0.1)
        assert ccr.ramp == 100
        assert ccr.setpoint == 0
        # Set the ramp to 0 to enforce ramp setting to ramp limits
        ccr.ramp = 0
        assert ccr.ramp == 100
        ccr.maw(10)
