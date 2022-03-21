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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.commands.device import resetlimits
from nicos.core import ConfigurationError, Override, Readable

from nicos_sinq.devices.dynamic_userlimits import DynamicUserlimits

session_setup = 'dynamic_userlimits'


class DynamicUserlimitsDev(DynamicUserlimits, Readable):

    hardware_access = False

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    # Dummy function which is needed to inherit from Readable
    def doRead(self, maxage=0):
        return 0


def test_userlim_follow_abslim_true(session):
    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = True
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Set custom userlimits
    dylimits.userlimits = (1, 8)

    # Test the docstring example
    dylimits._setROParam('abslimits', (2, 13))
    assert dylimits.userlimits == (3, 11)
    assert dylimits.doReadUserlimits() == (3, 11)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 11

    dylimits._setROParam('abslimits', (0, 10))
    assert dylimits.userlimits == (1, 8)
    assert dylimits.usermin == 1
    assert dylimits.usermax == 8

    dylimits._setROParam('abslimits', (3, 7))
    assert dylimits.userlimits == (4, 5)
    assert dylimits.usermin == 4
    assert dylimits.usermax == 5

    dylimits._setROParam('abslimits', (-8, -1))
    assert dylimits.userlimits == (-7, -3)
    assert dylimits.usermin == -7
    assert dylimits.usermax == -3

    # Additional tests
    dylimits._setROParam('abslimits', (0, 0.5))
    assert dylimits.userlimits == (0, 0)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits._setROParam('abslimits', (0, 0))
    assert dylimits.userlimits == (0, 0)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits._setROParam('abslimits', (4, 12))
    assert dylimits.userlimits == (5, 10)
    assert dylimits.usermin == 5
    assert dylimits.usermax == 10

    dylimits._setROParam('abslimits', (12, 12))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits._setROParam('abslimits', (17, 19))
    assert dylimits.userlimits == (17, 17)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 17

    dylimits._setROParam('abslimits', (17, 21))
    assert dylimits.userlimits == (18, 19)
    assert dylimits.usermin == 18
    assert dylimits.usermax == 19

    # Set new userlimits
    dylimits.userlimits = (17, 20)
    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20

    dylimits._setROParam('abslimits', (3, 5))
    assert dylimits.userlimits == (3, 4)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 4

    dylimits._setROParam('abslimits', (0, 26))
    assert dylimits.userlimits == (0, 25)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 25


def test_userlim_follow_abslim_false(session):
    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = False
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Set custom userlimits
    dylimits.userlimits = (1, 8)

    # Test the docstring example
    dylimits._setROParam('abslimits', (2, 13))
    assert dylimits.userlimits == (2, 8)
    assert dylimits.doReadUserlimits() == (2, 8)
    assert dylimits.usermin == 2
    assert dylimits.usermax == 8

    dylimits._setROParam('abslimits', (0, 10))
    assert dylimits.userlimits == (1, 8)
    assert dylimits.usermin == 1
    assert dylimits.usermax == 8

    dylimits._setROParam('abslimits', (3, 7))
    assert dylimits.userlimits == (3, 7)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 7

    dylimits._setROParam('abslimits', (-8, -1))
    assert dylimits.userlimits == (-1, -1)
    assert dylimits.usermin == -1
    assert dylimits.usermax == -1

    # Additional tests
    dylimits._setROParam('abslimits', (0, 0.5))
    assert dylimits.userlimits == (0.5, 0.5)
    assert dylimits.usermin == 0.5
    assert dylimits.usermax == 0.5

    dylimits._setROParam('abslimits', (0, 0))
    assert dylimits.userlimits == (0, 0)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits._setROParam('abslimits', (4, 12))
    assert dylimits.userlimits == (4, 8)
    assert dylimits.usermin == 4
    assert dylimits.usermax == 8

    dylimits._setROParam('abslimits', (12, 12))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits._setROParam('abslimits', (12, 12.5))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits._setROParam('abslimits', (17, 19))
    assert dylimits.userlimits == (17, 17)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 17

    dylimits._setROParam('abslimits', (17, 21))
    assert dylimits.userlimits == (17, 17)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 17

    # Set new userlimits
    dylimits.userlimits = (17, 20)
    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20

    dylimits._setROParam('abslimits', (3, 5))
    assert dylimits.userlimits == (5, 5)
    assert dylimits.usermin == 5
    assert dylimits.usermax == 5

    dylimits._setROParam('abslimits', (0, 26))
    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20


def test_set_illegal_userlims(session):

    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = False
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Try to set illegal userlimits
    with pytest.raises(ConfigurationError):
        dylimits.userlimits = (1, 11)

    with pytest.raises(ConfigurationError):
        dylimits.userlimits = (-1, 9)

    with pytest.raises(ConfigurationError):
        dylimits.userlimits = (-1, 11)

    # Setting a legal userlimit works
    dylimits.userlimits = (1, 9)
    assert dylimits.userlimits == (1, 9)
