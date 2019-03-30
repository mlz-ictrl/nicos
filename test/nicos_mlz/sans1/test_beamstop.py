#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""SANS-1 specific device tests."""

import pytest

from nicos.core.errors import ConfigurationError, LimitError, UsageError

from test.utils import raises

session_setup = 'sans1'


class TestBeamStop:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        bs = session.getDevice('bs')
        yield bs
        bs.maw((500, 300))

    def test_beamstop(self, session):
        bs = session.getDevice('bs')
        assert bs.read() == (500, 300)
        assert bs.ylimits == (100, 590)
        assert bs.xlimits == (480, 868)
        assert bs._attached_yaxis.read() > min(bs.ylimits)

        assert raises(LimitError, bs.maw, (100, 300))
        assert raises(LimitError, bs.maw, (500, 600))

    def test_beamstop_shape(self, session):
        bs = session.getDevice('bs')
        assert bs.shape == 'none'

        bs.shape = 'd35'
        # The 2 following errors are expected due to busy state
        assert raises(UsageError, setattr, bs, 'shape', '70x70')
        assert raises(LimitError, bs.maw, (480, 100))
        bs.wait()
        assert bs.shape == 'd35'
        bs.maw((481, 100))

        assert raises(ConfigurationError, setattr, bs, 'shape', 'unknown')

    def test_beamstop_axis(self, session):
        dev = session.getDevice('bs_xax')
        assert dev.offset == 0.
        assert raises(ConfigurationError, setattr, dev, 'offset', 10)
        dev.offset = 0
