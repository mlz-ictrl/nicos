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

"""NICOS commands tests."""

from __future__ import with_statement

from nicos import session
from nicos.core import UsageError, LimitError, ModeError

from nicos.commands.measure import count
from nicos.commands.device import move, maw
from nicos.commands.scan import scan
from nicos.commands.basic import help, dir #pylint: disable=W0622
from nicos.commands.basic import listcommands, sleep, \
     NewSetup, AddSetup, RemoveSetup, ListSetups, \
     CreateDevice, DestroyDevice, CreateAllDevices, \
     NewExperiment, FinishExperiment, AddUser, NewSample, \
     Remark, Remember, SetMode, ClearCache, UserInfo
from nicos.commands.output import printdebug, printinfo, printwarning, \
     printerror, printexception

from test.utils import ErrorLogged, raises

def setup_module():
    session.loadSetup('axis')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()


def test_output_commands():
    printdebug('a', 'b')
    printinfo('testing...')
    try:
        1/0
    except ZeroDivisionError:
        assert session.testhandler.warns(printwarning, 'warn!', exc=1)
    assert raises(ErrorLogged, printerror, 'error!')
    assert raises(ZeroDivisionError, printexception, 'exception!')

def test_basic_commands():
    dev = session.getDevice('motor')

    help(help)
    listcommands()

    d = dir(dev)
    assert 'start' in d
    assert 'doStart' not in d
    assert '_get_from_cache' not in d

    sleep(0.1)

    ListSetups()
    NewSetup('axis')
    AddSetup('slit')
    assert 'slit' in session.configured_devices  # not autocreated
    RemoveSetup('slit')
    assert 'slit' not in session.configured_devices
    assert session.testhandler.warns(RemoveSetup, 'blah')

    assert 'motor' not in session.devices
    CreateDevice('motor')
    assert 'motor' in session.devices
    DestroyDevice('motor')
    assert 'motor' not in session.devices
    CreateAllDevices()
    assert 'motor' in session.devices
    assert 'motor' in session.explicit_devices
    assert 'coder' in session.devices
    assert 'coder' not in session.explicit_devices

    exp = session.getDevice('Exp')

    NewExperiment(1234, 'Test experiment', 'L. Contact', '1. User')
    assert exp.proposal == '1234'
    assert exp.title == 'Test experiment'
    AddUser('F. X. User', 'user@example.com')
    assert 'F. X. User <user@example.com>' in exp.users
    NewSample('MnSi', lattice=[4.58]*3, angles=[90]*3)
    FinishExperiment()

    Remark('hi')
    assert exp.remark == 'hi'
    Remember('blah')
    assert 'blah' in exp.remember[0]

    SetMode('slave')
    SetMode('master')
    assert raises(UsageError, SetMode, 'blah')

    ClearCache('motor')

    with UserInfo('userinfo'):
        assert 'userinfo' == session._actionStack[-1]

def test_device_commands():
    motor = session.getDevice('motor')

    session.setMode('slave')
    assert raises(ModeError, scan, motor, [0, 1, 2, 10])

    session.setMode('master')
    scan(motor, [0, 1, 2, 10])

    assert raises(UsageError, count, motor)
    count()

    assert raises(LimitError, move, motor, max(motor.abslimits)+1)

    positions = (min(motor.abslimits), 0, max(motor.abslimits))
    for pos in positions:
        move(motor, pos)
        motor.wait()
        assert motor.curvalue == pos

    for pos in positions:
        maw(motor, pos)
        assert motor.curvalue == pos
