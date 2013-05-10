#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

import time

from nicos import session
from nicos.core import LimitError, ConfigurationError, InvalidValueError, \
     PositionError
from test.utils import raises


def setup_module():
    session.loadSetup('multiswitch')

def teardown_module():
    session.unloadSetup()

def test_multi_switcher():
    sc1 = session.getDevice('sc1')
    sc1.maw('1')
    assert sc1.read(0) == '1'

    assert raises(InvalidValueError, sc1.maw, '23')
    assert raises(LimitError, sc1.start, 'outside')

    sc1.move('2')
    time.sleep(0.01)
    assert sc1.read() in ['2']

    sc1.stop()

    sc2 = session.getDevice('sc2')
    sc2.maw('1')
    assert sc2.read(0) == '1'

    assert raises(InvalidValueError, sc2.maw, '23')
    assert raises(LimitError, sc2.start, 'outside')

    msw5 = session.getDevice('msw5')
    msw5.move('1')
    # msw5 has a precision of None for motor 'y', but that motor has
    # a jitter set so that it will never be exactly at 0
    assert raises(PositionError, msw5.wait)

def test_multi_switcher_fails():
    assert raises(ConfigurationError, session.getDevice, 'msw3')
    assert raises(ConfigurationError, session.getDevice, 'msw4')
