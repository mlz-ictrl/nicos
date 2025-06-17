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
import pytest

session_setup = 'xccm'

from nicos.commands.measure import count


class TestCapillarySelector:

    @pytest.fixture(autouse=True)
    def cs(self, session):
        dev = session.getDevice('capillary_selector')
        yield dev

    @pytest.mark.parametrize('target', [1, 2, 3])
    def test_move(self, cs, target):
        cs.maw(target)
        assert cs.read(0) == target


class TestDetector:

    @pytest.fixture(autouse=True)
    def det(self, session):
        dev = session.getDevice('det')
        yield dev


    def test_count(self, det):
        count(det, t=0.1)


class TestOpticToolSwitch:

    @pytest.fixture(autouse=True)
    def ot(self, session):
        dev = session.getDevice('optic_tool_switch')
        yield dev

    @pytest.mark.parametrize('target', (1, 2, 3, 1))
    def test_move(self, ot, target):
        ot.maw(target)
        assert ot.read(0) == target
