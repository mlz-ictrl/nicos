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

# from nicos.commands.device import adjust
# from nicos.core.errors import ConfigurationError, InvalidValueError, \
#     LimitError, UsageError

session_setup = 'refsans_optic'


class TestOptic:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    def test_read(self, session):
        optic = session.getDevice('optic')
        assert optic.read(0) == optic.target

    @pytest.mark.parametrize('target', [
        'horizontal',
        '12mrad_b3_12.000',
        '12mrad_b2_12.254_eng',
        '12mrad_b2_12.88_big',
        # '12mrad_b3_13.268',
        '12mrad_b3_789',
        '48mrad',
        # 0, 24, 48,
    ])
    def test_move(self, session, target):
        optic = session.getDevice('optic')

        optic.maw(target)
        assert optic.read(0) == target
