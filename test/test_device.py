#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""NICOS device class test suite."""

__version__ = "$Revision$"

from nicos import session
from nicos import status
from nicos.device import Device, Moveable, HasLimits, HasOffset, Param
from nicos.errors import ConfigurationError, ProgrammingError, LimitError, \
     FixedError, UsageError
from test.utils import raises


methods_called = set()

def setup_module():
    global axis
    session.loadSetup('device')
    methods_called.clear()

def teardown_module():
    session.unloadSetup()


class Dev1(Device):
    pass

class Dev2(HasLimits, HasOffset, Moveable):
    attached_devices = {'attached': (Dev1, 'Test attached device')}
    parameters = {
        'param1': Param('An optional parameter', type=int, default=42),
        'param2': Param('A mandatory parameter', type=int, mandatory=True,
                        settable=True, category='instrument'),
        'failinit': Param('If true, fail the doInit() call', type=bool,
                          default=False),
    }

    def doInit(self):
        if self.failinit:
            1/0
        self._val = 0
        methods_called.add('doInit')

    def doRead(self):
        return self._val

    def doIsAllowed(self, pos):
        if pos == 5:
            return False, 'foo'
        methods_called.add('doIsAllowed')
        return True, ''

    def doStart(self, pos):
        self._val = pos
        methods_called.add('doStart')

    def doStop(self):
        methods_called.add('doStop')

    def doWait(self):
        methods_called.add('doWait')

    def doStatus(self):
        return status.BUSY, 'busy'

    def doReset(self):
        methods_called.add('doReset')

    def doReadParam2(self):
        return 21

    def doWriteParam2(self, value):
        methods_called.add('doWriteParam2')
        return value + 1

    def doUpdateParam2(self, value):
        methods_called.add('doUpdateParam2')

    def doInfo(self):
        return [('instrument', 'testkey', 'testval')]


def test_initialization():
    # make sure dev2_1 is created and then try to instantiate another device
    # with this name...
    session.getDevice('dev2_1')
    assert raises(ProgrammingError, Dev2, 'dev2_1')
    # Dev2 instance without 'attached' adev set
    assert raises(ConfigurationError, session.getDevice, 'dev2_2')
    # try to instantiate a device that fails init()
    assert raises(ZeroDivisionError, session.getDevice, 'dev2_4')
    # assert correct cleanup
    assert 'dev2_4' not in session.devices

def test_special_methods():
    dev = session.getDevice('dev2_1')
    # pickling a device should yield its name as a string
    import pickle
    assert pickle.loads(pickle.dumps(dev)) == 'dev2_1'
    # test that the repr() works
    assert dev.name in repr(dev)

def test_params():
    dev2 = session.getDevice('dev2_1')
    # make sure adev instances are created
    assert isinstance(dev2._adevs['attached'], Dev1)
    # an inherited and writable parameter
    assert dev2.unit == 'mm'
    dev2.unit = 'deg'
    assert dev2.unit == 'deg'
    # a readonly parameter
    assert dev2.param1 == 42
    assert raises(ConfigurationError, setattr, dev2, 'param1', 21)
    # a parameter with custom getter and setter
    assert dev2.param2 == 21
    dev2.param2 = 5
    assert dev2.param2 == 6
    assert 'doWriteParam2' in methods_called
    assert 'doUpdateParam2' in methods_called
    # nonexisting parameters
    assert raises(UsageError, setattr, dev2, 'param3', 1)
    # test legacy getPar/setPar API
    dev2.setPar('param2', 7)
    assert dev2.getPar('param2') == 8

def test_methods():
    dev2 = session.getDevice('dev2_3')
    assert 'doInit' in methods_called
    dev2.move(10)
    assert 'doStart' in methods_called
    assert 'doIsAllowed' in methods_called
    # moving beyond limits
    assert raises(LimitError, dev2.move, 50)
    # or forbidden by doIsAllowed()
    assert raises(LimitError, dev2.move, 5)
    # read() and status()
    assert dev2.read() == 10
    assert dev2.status()[0] == status.BUSY
    # __call__ interface
    dev2(7)
    assert dev2() == 7
    # further methods
    dev2.reset()
    assert 'doReset' in methods_called
    dev2.stop()
    assert 'doStop' in methods_called
    dev2.wait()
    assert 'doWait' in methods_called
    # fixing and releasing
    dev2.fix('blah')
    try:
        assert raises(FixedError, dev2.move, 7)
    finally:
        dev2.release()
    dev2.move(7)
    # test info() method
    keys = set(value[1] for value in dev2.info())
    assert 'testkey' in keys
    assert 'param2' in keys
    assert 'value' in keys
    assert 'status' in keys

def test_limits():
    dev2 = session.getDevice('dev2_3')
    # abslimits are (0, 10) as set in configuration
    dev2.userlimits = dev2.abslimits
    assert dev2.userlimits == dev2.abslimits
    # individual getters/setters
    dev2.usermin, dev2.usermax = dev2.absmin + 1, dev2.absmax - 1
    assert (dev2.usermin, dev2.usermax) == (1, 9)
    # checking limit setting
    assert raises(ConfigurationError, setattr, dev2, 'userlimits', (5, 4))
    assert raises(ConfigurationError, setattr, dev2, 'userlimits', (-1, 1))
    assert raises(ConfigurationError, setattr, dev2, 'userlimits', (9, 11))
    assert raises(ConfigurationError, setattr, dev2, 'userlimits', (11, 12))
    # offset behavior
    dev2.userlimits = dev2.abslimits
    assert dev2.offset == 0
    dev2.offset = 1
    # now physical 1 is logical 0 -> userlimits must be shifted downwards, while
    # absolute limits stay in physical units
    assert dev2.userlimits[0] == dev2.abslimits[0] - 1
    dev2.offset = 0
    # warn when setting limits that don't include current position
    dev2.move(6)
    assert session.testhandler.warns(setattr, dev2, 'userlimits', (0, 4))
