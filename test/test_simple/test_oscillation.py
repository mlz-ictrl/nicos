#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS oscillation device test suite."""

import pytest

from nicos.core import ConfigurationError, status

from test.utils import raises

session_setup = 'oscillator'


@pytest.fixture(scope='function', autouse=True)
def osci(session):
    osci = session.getDevice('osci')
    yield osci
    session.destroyDevice(osci)


def test_params(session, osci):
    axis = session.getDevice('axis')
    limits = axis.userlimits
    # min/max parameters got from moveable device
    assert osci.range == limits
    # stoppable paramter check
    assert osci.stoppable is False

    osci.range = (0, 10)
    assert osci.range == (0, 10)

    assert raises(ConfigurationError, setattr, osci, 'range', (10, 0))
    assert raises(ConfigurationError, setattr, osci, 'range', (-110, 0))
    assert raises(ConfigurationError, setattr, osci, 'range', (0, 110))

    osci2 = session.getDevice('osci2')
    osci2.range = (0, 50)
    assert osci2.stoppable is True

    # The following test forces the use of the doReadRange method which is not
    # called with osci.range
    osci3 = session.getDevice('osci3')
    # forces an error since the configured lower range limit is below userlimt
    assert raises(ConfigurationError, osci3.doReadRange)

    osci4 = session.getDevice('osci4')
    # forces an error since the configured upper range limit is above userlimt
    assert raises(ConfigurationError, osci4.doReadRange)


def test_movement(session, osci, log):
    osci.maw('on')
    assert osci.read() == 'on'
    assert osci.status(0)[0] == status.OK

    with log.assert_errors(r"^ERROR   : \w+ : Please use: 'move\(\w+,"):
        osci.stop()

    osci.maw('off')
    assert osci.read() == 'off'
    assert osci.status(0)[0] == status.OK
    assert osci.stop() is None

    osci2 = session.getDevice('osci2')
    osci2.maw('on')
    assert osci2.read() == 'on'
    assert osci2.status(0)[0] == status.OK

    osci2.stop()
    assert osci2.read() == 'off'
    assert osci2.status(0)[0] == status.OK


def test_reset(osci):
    osci.reset()


def test_range_setting(osci):

    # set range to (0, 0) and moving is not allowed
    osci.range = (0, 0)
    assert raises(ConfigurationError, osci.start, 'on')

    # empty range is not allowed
    osci.range = (1, 1)
    assert raises(ConfigurationError, osci.start, 'on')
