#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from nicos.core import UsageError, ConfigurationError, NoDevice
from nicos.commands.device import read, adjust
from nicos.commands.basic import ListCommands

from test.utils import raises, ErrorLogged

session_setup = 'alias'


def test_alias_nodev(session, log):
    alias = session.getDevice('aliasNoDev', object)
    # first, proxy without target
    assert isinstance(alias._obj, NoDevice)
    assert alias.alias == ''
    # accesses raise ConfigurationError
    assert raises(AttributeError, getattr, alias, 'read')
    assert raises(ConfigurationError, setattr, alias, 'speed', 0)
    assert raises(ErrorLogged, read, alias)
    # but stringification is still the name of the alias object
    assert str(alias) == 'aliasNoDev'
    assert 'aliasNoDev' in repr(alias)
    with log.assert_msg_matches([r' name +description *$',
                                 # explicitly no check on help text!
                                 r'ClearCache\(dev, \.\.\.\)']):
        ListCommands()


def test_alias_dev(session, log):
    alias = session.getDevice('aliasDev', object)
    # now set the alias to some object
    v1 = session.getDevice('v1')
    # "alias" is a chatty property, so it should emit something when changed
    with log.assert_msg_matches('alias set to'):
        alias.alias = v1
    # check delegation of methods etc.
    assert isinstance(alias, type(v1))
    assert type(alias) != type(v1)  # pylint: disable=unidiomatic-typecheck
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


def test_alias_valueinfo2(session):
    # check with multiple values, check setting from config
    alias = session.getDevice('aliasDev2', object)
    # check the value info replacement
    vistr = str(alias.valueInfo())
    assert 'aliasDev2.' in vistr


def test_adjust_alias(session, log):
    alias = session.getDevice('aliasDev3', object)
    # now set the alias to some object
    axis = session.getDevice('axis')
    # "alias" is a chatty property, so it should emit something when changed
    with log.assert_msg_matches('alias set to'):
        alias.alias = axis

    alias.alias = axis
    alias.offset = 0.0
    adjust(alias, 1)
    assert alias.offset == -1.0
    assert axis.offset == -1.0
    adjust(alias, 0)
    assert alias.offset == 0.0
    assert axis.offset == 0.0


def test_alias_valueinfo(session):
    # check the value info replacement
    alias = session.getDevice('aliasDev4', object)
    v1 = session.getDevice('v1')
    alias.alias = v1
    vistr = str(alias.valueInfo())
    assert 'aliasDev4' in vistr
    assert alias.valueInfo()[0].name == 'aliasDev4'
