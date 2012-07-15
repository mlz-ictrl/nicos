#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS generic devices test suite."""

__version__ = "$Revision$"

from nicos import session
from nicos.core import PositionError, NicosError, LimitError, UsageError, \
     ConfigurationError, status
from nicos.generic.alias import NoDevice
from nicos.commands.device import read
from test.utils import raises


def setup_module():
    session.loadSetup('generic')

def teardown_module():
    session.unloadSetup()


def test_virtual_motor():
    v = session.getDevice('v1')
    v.maw(1)
    assert v.read() == 1
    v.move(0)
    v.stop()
    assert 0 <= v.read() <= 1

def test_virtual_switch():
    v = session.getDevice('v2')
    v.maw('up')
    assert v.read() == 'up'
    assert raises(NicosError, v.move, 'sideways')
    assert v.read() == 'up'

def test_manual_switch():
    m = session.getDevice('m1')
    assert m.read() == 'up'
    m.maw('down')
    assert m.read() == 'down'
    assert raises(NicosError, m.move, 'sideways')
    assert m.read() == 'down'
    assert m.status()[0] == status.OK

def test_switcher():
    sw = session.getDevice('sw')
    v3 = session.getDevice('v3')
    v3.maw(1)
    assert sw.read(0) == 'left'
    v3.maw(3)
    assert sw.read(0) == 'right'
    sw.maw('left')
    assert v3.read() == 1
    sw.maw('right')
    assert v3.read() == 3

    assert sw.status() == v3.status()

    assert raises(NicosError, sw.start, '#####')
    assert raises(LimitError, sw.start, 'outside')

    v3.maw(1.01)
    assert sw.read(0) == 'left'
    v3.maw(1.2)
    assert raises(PositionError, sw.read, 0)

    assert raises(ConfigurationError, session.getDevice, 'broken_sw')

    rsw = session.getDevice('rsw')
    assert raises(PositionError, rsw.read, 0)

    v3.maw(1)
    assert rsw.read(0) == 'left'
    v3.maw(3)
    assert rsw.read(0) == 'right'

    assert rsw.status() == v3.status()

def test_alias():
    px = session.getDevice('alias', object)

    # first, proxy without target
    assert isinstance(px._obj, NoDevice)
    assert px.alias == ''
    # attribute accesses raise ConfigurationError
    assert raises(ConfigurationError, getattr, px, 'read')
    assert raises(ConfigurationError, setattr, px, 'speed', 0)
    # trying to access as device raises UsageError
    assert raises(UsageError, read, px)
    # but stringification is still the name of the alias object
    assert str(px) == 'alias'
    assert 'alias' in repr(px)

    # now set the alias to some object
    v1 = session.getDevice('v1')
    px.alias = v1
    # check delegation of methods etc.
    assert v1.read() == px.read()
    # check attribute access
    px.speed = 5.1
    assert v1.speed == 5.1

    # check cache key rewriting
    assert session.cache.get(px, 'speed') == 5.1
    assert session.cache.get_explicit(px, 'speed')[2] == 5.1
