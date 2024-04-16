# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

"""Module to test MORPHEUS specific modules."""

import pytest

session_setup = 'sinq_morpheus'


class TestMorpheusSpin:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        yield
        session.getDevice('ispin').maw(1)

    def test_read(self, session):
        spin = session.getDevice('ispin')
        assert spin.read(0) == 1

    def test_move(self, session):
        spin = session.getDevice('ispin')
        spin.move(0)
        assert spin.read(0) == -1
        spin.wait()

    @pytest.mark.parametrize('target', [0, 1, '+', '-', 'down', 'up'])
    def test_flipping(self, session, target):
        spin = session.getDevice('ispin')
        spin.maw(target)
        assert spin.read(0) == (1 if target in (1, '-', 'down') else 0)
