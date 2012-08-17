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

from time import sleep

from nicos import session
from nicos.core import UsageError, ConfigurationError
from nicos.generic.alias import NoDevice
from nicos.commands.device import read
from test.utils import raises


def setup_module():
    session.loadSetup('alias')

def teardown_module():
    session.unloadSetup()


def test_alias_nodev():
    px = session.getDevice('aliasDev', object)

    # first, proxy without target
    assert isinstance(px._obj, NoDevice)
    assert px.alias == ''
    # accesses raise ConfigurationError
    assert raises(ConfigurationError, getattr, px, 'read')
    assert raises(ConfigurationError, setattr, px, 'speed', 0)
    assert raises(ConfigurationError, read, px)
    # but stringification is still the name of the alias object
    assert str(px) == 'aliasDev'
    assert 'aliasDev' in repr(px)

def test_alias_dev():
    px = session.getDevice('aliasDev', object)
    # now set the alias to some object
    v1 = session.getDevice('v1')
    px.alias = v1
    # check delegation of methods etc.
    assert v1.read() == px.read()
    # check attribute access
    px.speed = 5.1
    assert v1.speed == 5.1
    # check cache key rewriting
    sleep(0.5)
    assert session.cache.get(px, 'speed') == 5.1
    assert session.cache.get_explicit(px, 'speed')[2] == 5.1
    # check type restriction by devclass parameter
    slit = session.getDevice('slit')
    assert raises(UsageError, setattr, px, 'alias', slit)

def test_alias_valueinfo():
    # check the value info replacement
    px = session.getDevice('aliasDev', object)
    v1 = session.getDevice('v1')
    px.alias = v1
    vistr = str(px.valueInfo())
    assert 'aliasDev' in vistr
    assert 'aliasDev' == px.valueInfo()[0].name

def test_alias_valueinfo2():
    # check with multiple values, check setting from config
    py = session.getDevice('aliasDev2', object)
    # check the value info replacement
    vistr = str(py.valueInfo())
    assert 'aliasDev2.' in vistr
