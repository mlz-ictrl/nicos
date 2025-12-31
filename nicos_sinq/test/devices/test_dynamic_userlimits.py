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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.commands.device import adjust, resetlimits
from nicos.core import ConfigurationError, Override, HasOffset
from nicos.core.errors import LimitError
from nicos.devices.generic.manual import ManualMove

from nicos_sinq.devices.dynamic_userlimits import DynamicUserlimits

session_setup = 'dynamic_userlimits'


class DynamicUserlimitsDev(DynamicUserlimits, HasOffset, ManualMove):

    hardware_access = False

    _position = 0

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    def doRead(self, maxage=0):
        return self._position - self.offset

    def doWriteAbslimits(self, value):
        '''
        In the test environment, no cache process is running and the callback is
        therefore not triggered automatically. Hence, this function simulates
        that behaviour by manually running the callback.
        '''
        self._cache.put(self, 'abslimits', value)
        self._callbackAbsoluteLimitsChanged(None, None, None)


def test_userlim_follow_abslim_true(session):
    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = True
    dylimits.offset = 0
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Set custom userlimits
    dylimits.userlimits = (1, 8)

    # Test the docstring example
    dylimits.doWriteAbslimits((2, 13))
    assert dylimits.userlimits == (3, 11)
    assert dylimits.doReadUserlimits() == (3, 11)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 11

    dylimits.doWriteAbslimits((0, 10))
    assert dylimits.userlimits == (1, 8)
    assert dylimits.usermin == 1
    assert dylimits.usermax == 8

    dylimits.doWriteAbslimits((3, 7))
    assert dylimits.userlimits == (4, 5)
    assert dylimits.usermin == 4
    assert dylimits.usermax == 5

    dylimits.doWriteAbslimits((-8, -1))
    assert dylimits.userlimits == (-7, -3)
    assert dylimits.usermin == -7
    assert dylimits.usermax == -3

    # Additional tests
    dylimits.doWriteAbslimits((0, 0.5))
    assert dylimits.userlimits == (0, 0.5)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0.5

    dylimits.doWriteAbslimits((0, 0))
    assert dylimits.userlimits == (0, 0)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits.doWriteAbslimits((4, 12))
    assert dylimits.userlimits == (5, 10)
    assert dylimits.usermin == 5
    assert dylimits.usermax == 10

    dylimits.doWriteAbslimits((12, 12))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits.doWriteAbslimits((17, 19))
    assert dylimits.userlimits == (17, 18)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 18

    dylimits.doWriteAbslimits((17, 21))
    assert dylimits.userlimits == (18, 19)
    assert dylimits.usermin == 18
    assert dylimits.usermax == 19

    # Set new userlimits
    dylimits.userlimits = (17, 20)
    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20

    dylimits.doWriteAbslimits((3, 5))
    assert dylimits.userlimits == (3, 4)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 4

    dylimits.doWriteAbslimits((0, 26))
    assert dylimits.userlimits == (0, 25)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 25

    # Test with offsets
    dylimits.offset = 5
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -5
    assert dylimits.usermax == 20

    dylimits.offset = 15
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -15
    assert dylimits.usermax == 10

    dylimits.offset = 25
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -25
    assert dylimits.usermax == 0

    dylimits.offset = 45
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -45
    assert dylimits.usermax == -20

    dylimits.offset = -5
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 5
    assert dylimits.usermax == 30

    dylimits.offset = -30
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 30
    assert dylimits.usermax == 55

    dylimits.offset = 30
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -30
    assert dylimits.usermax == -5

    # With offset and varying abslimits
    dylimits.offset = 30
    dylimits.doWriteAbslimits((0, 30))
    assert dylimits.usermin == -30
    assert dylimits.usermax == -1

    dylimits.offset = 30
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == -60
    assert dylimits.usermax == -31

    dylimits.offset = 0
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == -30
    assert dylimits.usermax == -1

    dylimits.offset = -100
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == 70
    assert dylimits.usermax == 99

    # With offset and varying userlimits
    dylimits.offset = -100
    dylimits.doWriteAbslimits((-30, 0))
    dylimits.userlimits = (80, 90)
    assert dylimits.usermin == 80
    assert dylimits.usermax == 90

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
    dylimits.doWriteAbslimits((2, 13))
    assert dylimits.userlimits == (2, 8)
    assert dylimits.doReadUserlimits() == (2, 8)
    assert dylimits.usermin == 2
    assert dylimits.usermax == 8

    dylimits.doWriteAbslimits((0, 10))
    assert dylimits.userlimits == (1, 8)
    assert dylimits.usermin == 1
    assert dylimits.usermax == 8

    dylimits.doWriteAbslimits((3, 7))
    assert dylimits.userlimits == (3, 7)
    assert dylimits.usermin == 3
    assert dylimits.usermax == 7

    dylimits.doWriteAbslimits((-8, -1))
    assert dylimits.userlimits == (-1, -1)
    assert dylimits.usermin == -1
    assert dylimits.usermax == -1

    # Additional tests
    dylimits.doWriteAbslimits((0, 0.5))
    assert dylimits.userlimits == (0.5, 0.5)
    assert dylimits.usermin == 0.5
    assert dylimits.usermax == 0.5

    dylimits.doWriteAbslimits((0, 0))
    assert dylimits.userlimits == (0, 0)
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits.doWriteAbslimits((4, 12))
    assert dylimits.userlimits == (4, 8)
    assert dylimits.usermin == 4
    assert dylimits.usermax == 8

    dylimits.doWriteAbslimits((12, 12))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits.doWriteAbslimits((12, 12.5))
    assert dylimits.userlimits == (12, 12)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 12

    dylimits.doWriteAbslimits((17, 19))
    assert dylimits.userlimits == (17, 17)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 17

    dylimits.doWriteAbslimits((17, 21))
    assert dylimits.userlimits == (17, 17)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 17

    # Set new userlimits
    dylimits.userlimits = (17, 20)

    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20

    dylimits.doWriteAbslimits((3, 5))
    assert dylimits.userlimits == (5, 5)
    assert dylimits.usermin == 5
    assert dylimits.usermax == 5

    dylimits.doWriteAbslimits((0, 26))
    assert dylimits.userlimits == (17, 20)
    assert dylimits.usermin == 17
    assert dylimits.usermax == 20

    # Test with offsets
    dylimits.offset = 5
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 12
    assert dylimits.usermax == 15

    dylimits.offset = 15
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 2
    assert dylimits.usermax == 5

    dylimits.offset = 25
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -8
    assert dylimits.usermax == -5

    dylimits.offset = 45
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -28
    assert dylimits.usermax == -25

    dylimits.offset = -5
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 22
    assert dylimits.usermax == 25

    dylimits.offset = -30
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == 47
    assert dylimits.usermax == 50

    dylimits.offset = 30
    assert dylimits.abslimits == (0, 26)
    assert dylimits.usermin == -13
    assert dylimits.usermax == -10

    # With offset and varying abslimits
    dylimits.offset = 30
    dylimits.doWriteAbslimits((0, 30))
    assert dylimits.usermin == -13
    assert dylimits.usermax == -10

    dylimits.offset = 30
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == -30
    assert dylimits.usermax == -30

    dylimits.offset = 0
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == 0
    assert dylimits.usermax == 0

    dylimits.offset = -100
    dylimits.doWriteAbslimits((-30, 0))
    assert dylimits.usermin == 100
    assert dylimits.usermax == 100

    # With offset and varying userlimits
    dylimits.offset = -100
    dylimits.doWriteAbslimits((-30, 0))
    dylimits.userlimits = (80, 90)
    assert dylimits.usermin == 80
    assert dylimits.usermax == 90


def test_init_with_offset(session):
    dylimits = session.getDevice('dylimits_offset')
    dylimits.userlim_follow_abslim = True
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (-50, -40)
    assert dylimits.inputlimits == (-50, -40)
    assert dylimits.delta_limits == (0, 0)


def test_move_follow_true(session):
    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = True
    dylimits.offset = 0
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Set custom userlimits
    dylimits.userlimits = (1, 8)

    # Change the abslimits
    dylimits.doWriteAbslimits((2, 13))
    assert dylimits.userlimits == (3, 11)

    # These moves are in the valid range
    dylimits.move(10.5)
    dylimits.move(3)
    dylimits.move(11)

    # These moves are not allowed
    with pytest.raises(LimitError):
        dylimits.move(2)

    with pytest.raises(LimitError):
        dylimits.move(11.5)

    # Adjust the offset
    dylimits.offset = -20
    assert dylimits.userlimits == (23, 31)

    # These moves are in the valid range
    dylimits.move(30.5)
    dylimits.move(23)
    dylimits.move(31)

    # These moves are not allowed
    with pytest.raises(LimitError):
        dylimits.move(2)

    with pytest.raises(LimitError):
        dylimits.move(10.5)

    with pytest.raises(LimitError):
        dylimits.move(3)

    with pytest.raises(LimitError):
        dylimits.move(31.5)


def test_move_follow_false(session):
    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = False
    dylimits.offset = 0
    resetlimits(dylimits)

    # Initial abslimits and userlimits
    assert dylimits.abslimits == (0, 10)
    assert dylimits.userlimits == (0, 10)

    # Set custom userlimits
    dylimits.userlimits = (1, 8)

    # Change the abslimits
    dylimits.doWriteAbslimits((2, 13))
    assert dylimits.userlimits == (2, 8)

    # These moves are in the valid range
    dylimits.move(2)
    dylimits.move(7)
    dylimits.move(8)

    # These moves are not allowed
    with pytest.raises(LimitError):
        dylimits.move(1)

    with pytest.raises(LimitError):
        dylimits.move(11.5)

    # Adjust the offset
    dylimits.offset = -20
    assert dylimits.userlimits == (22, 28)

    # These moves are in the valid range
    dylimits.move(22)
    dylimits.move(27)
    dylimits.move(28)

    # These moves are not allowed
    with pytest.raises(LimitError):
        dylimits.move(1)

    with pytest.raises(LimitError):
        dylimits.move(10.5)

    with pytest.raises(LimitError):
        dylimits.move(3)

    with pytest.raises(LimitError):
        dylimits.move(30.5)

    with pytest.raises(LimitError):
        dylimits.move(31.5)


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

def test_adjust_userlim_follow_abslim_true(session):

    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = True
    resetlimits(dylimits)

    # Set a new position with adjust
    assert dylimits.userlimits == (0, 10)
    dylimits._position = 5
    assert dylimits.read(0) == 5

    adjust(dylimits, 0)
    assert dylimits.read(0) == 0
    assert dylimits.userlimits == (-5, 5)

    adjust(dylimits, 20)
    assert dylimits.read(0) == 20
    assert dylimits.userlimits == (15, 25)

def test_adjust_userlim_follow_abslim_false(session):

    dylimits = session.getDevice('dylimits')
    dylimits.userlim_follow_abslim = False
    resetlimits(dylimits)

    # Set a new position with adjust
    assert dylimits.userlimits == (0, 10)
    dylimits._position = 5
    assert dylimits.read(0) == 5

    adjust(dylimits, 0)
    assert dylimits.read(0) == 0
    assert dylimits.userlimits == (-5, 5)

    adjust(dylimits, 20)
    assert dylimits.read(0) == 20
    assert dylimits.userlimits == (15, 25)
