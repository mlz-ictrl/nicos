# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

session_setup = 'kompass'


class TestDevices:
    """Test class for the KOMPASS devices."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    @pytest.fixture(scope='function', autouse=True)
    def stt(self, session):
        yield session.getDevice('stt')

    @pytest.mark.parametrize('targets',
                             [[1, 31, 0, -1, -31], [-31, 39, -31], [0, 39]])
    def test_stt_with_beamstop(self, stt, targets):
        # The list of target sequences is needed to cover all cases in
        # generating the sequences in the SttWithPbs device from the current
        # positions
        for target in targets:
            stt.maw(target)
