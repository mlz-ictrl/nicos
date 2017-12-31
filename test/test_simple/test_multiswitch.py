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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS generic devices test suite."""

import mock

from nicos.core import LimitError, ConfigurationError, InvalidValueError, \
    PositionError, NicosError, status
from test.utils import raises

session_setup = 'multiswitch'


def test_multi_switcher(session):
    sc1 = session.getDevice('sc1')
    x = session.getDevice('x')
    y = session.getDevice('y')
    sc1.maw('1')
    assert sc1.read(0) == '1'

    assert raises(NicosError, sc1.doStart, '123')
    assert raises(InvalidValueError, sc1.maw, '23')
    assert raises(LimitError, sc1.start, 'outside')

    sc1.move('2')
    assert sc1.read() in ['2']
    assert abs(x.read() - 535.5) < 0.05
    x.curstatus = (status.BUSY, 'moving')
    sc1.stop()
    assert x.status(0)[0] == status.OK
    y.curvalue = 0
    assert raises(PositionError, sc1.read, 0)
    assert sc1.status(0)[0] == status.NOTREACHED

    sc2 = session.getDevice('sc2')
    sc2.maw('1')
    assert sc2.read(0) == '1'
    assert sc2.status(0)[0] == status.OK
    sc2.move('3')
    # case 1: motor in position, but still busy
    y.curstatus = (status.BUSY, 'busy')
    assert sc2.status(0)[0] != status.OK
    # case 2: motor idle, but wronmg position
    y.curstatus = (status.OK, 'on target')
    y.curvalue = 22.0
    assert sc2.status(0)[0] == status.NOTREACHED
    y.curvalue = 28.0
    assert sc2.status(0)[0] == status.OK

    assert raises(InvalidValueError, sc2.maw, '23')
    assert raises(LimitError, sc2.start, 'outside')

    with mock.patch('nicos.devices.generic.virtual.VirtualMotor.doReset',
                    create=True) as m:
        sc2.reset()
        assert m.call_count == 2  # once for x, once for y


def test_multi_switcher_fallback(session):
    mswfb = session.getDevice('mswfb')
    x = session.getDevice('x')
    x.maw(0)
    assert mswfb.read(0) == 'unknown'


def test_multi_switcher_fails(session, log):
    assert raises(ConfigurationError, session.getDevice, 'msw3')
    assert raises(ConfigurationError, session.getDevice, 'msw4')

    msw5 = session.getDevice('msw5')
    msw5.move('1')
    # msw5 has a precision of None for motor 'y', but that motor has
    # a jitter set so that it will never be exactly at 0
    with log.allow_errors():
        assert raises(PositionError, msw5.wait)
