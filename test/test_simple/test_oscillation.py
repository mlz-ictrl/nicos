#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS oscillation device test suite."""

from test.utils import raises

from nicos.core import ConfigurationError, UsageError, status

session_setup = 'oscillator'


def test_params(session):
    axis = session.getDevice('axis')
    limits = axis.userlimits
    osci = session.getDevice('osci')
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


def test_movement(session):
    osci = session.getDevice('osci')
    osci.maw('on')
    assert osci.read() == 'on'
    assert osci.status()[0] == status.OK

    assert raises(UsageError, osci.stop)

    osci.maw('off')
    assert osci.read() == 'off'
    assert osci.status()[0] == status.OK

    osci2 = session.getDevice('osci2')
    osci2.maw('on')
    assert osci2.read() == 'on'
    assert osci2.status()[0] == status.OK

    osci2.stop()
    assert osci2.read() == 'off'
    assert osci2.status()[0] == status.OK


def test_reset(session):
    osci = session.getDevice('osci')
    osci.reset()
