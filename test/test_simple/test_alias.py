#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from time import sleep

from nicos import session
from nicos.core import UsageError, ConfigurationError, NoDevice
from nicos.commands.device import read, adjust

from test.utils import raises, ErrorLogged


def setup_module():
    session.loadSetup('alias')


def teardown_module():
    session.unloadSetup()


def test_alias_nodev():
    alias = session.getDevice('aliasDev', object)

    # first, proxy without target
    assert isinstance(alias._obj, NoDevice)
    assert alias.alias == ''
    # accesses raise ConfigurationError
    assert raises(ConfigurationError, getattr, alias, 'read')
    assert raises(ConfigurationError, setattr, alias, 'speed', 0)
    assert raises(ErrorLogged, read, alias)
    # but stringification is still the name of the alias object
    assert str(alias) == 'aliasDev'
    assert 'aliasDev' in repr(alias)


def test_alias_dev():
    alias = session.getDevice('aliasDev', object)
    # now set the alias to some object
    v1 = session.getDevice('v1')
    # "alias" is a chatty property, so it should emit something when changed
    assert session.testhandler.emits_message(setattr, alias, 'alias', v1)
    # check delegation of methods etc.
    assert isinstance(alias, type(v1))
    assert type(alias) != type(v1)
    assert v1.read() == alias.read()
    # check attribute access
    alias.speed = 5.1
    assert alias.speed == 5.1
    assert v1.speed == 5.1
    # check cache key rewriting
    sleep(0.5)
    assert session.cache.get(alias, 'speed') == 5.1
    assert session.cache.get(v1, 'speed') == 5.1
    assert session.cache.get_explicit(alias, 'speed')[2] == 5.1
    # check type restriction by devclass parameter
    slit = session.getDevice('slit')
    assert raises(UsageError, setattr, alias, 'alias', slit)


def test_adjust_alias():
    alias = session.getDevice('aliasDev3', object)
    # now set the alias to some object
    axis = session.getDevice('axis')
    # "alias" is a chatty property, so it should emit something when changed
    assert session.testhandler.emits_message(setattr, alias, 'alias', axis)

    alias.alias = axis
    alias.offset = 0.0
    # # old behaviour
    # assert raises(UsageError, adjust, alias, 0)
    # # after fix of bug#870
    adjust(alias, 1)
    adjust(alias, 0)
    alias.alias = ''


def test_alias_valueinfo():
    # check the value info replacement
    alias = session.getDevice('aliasDev', object)
    v1 = session.getDevice('v1')
    alias.alias = v1
    vistr = str(alias.valueInfo())
    assert 'aliasDev' in vistr
    assert 'aliasDev' == alias.valueInfo()[0].name


def test_alias_valueinfo2():
    # check with multiple values, check setting from config
    alias = session.getDevice('aliasDev2', object)
    # check the value info replacement
    vistr = str(alias.valueInfo())
    assert 'aliasDev2.' in vistr
