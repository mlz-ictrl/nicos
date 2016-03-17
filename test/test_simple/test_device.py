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

"""NICOS device class test suite."""

from nicos import session
from nicos.core import ADMIN, AccessError, CommunicationError, \
    ConfigurationError, Device, HasCommunication, HasLimits, HasOffset, \
    LimitError, Moveable, Param, ProgrammingError, UsageError, requires, status, \
    usermethod, Attach
from nicos.core.sessions.utils import MAINTENANCE
from test.utils import raises


methods_called = set()


def setup_module():
    session.loadSetup('device')
    methods_called.clear()


def teardown_module():
    session.unloadSetup()


class Dev1(Device):
    pass


class Dev2(HasLimits, HasOffset, Moveable):
    attached_devices = {
        'attached': Attach('Test attached device', Dev1),
    }
    parameters = {
        'param1': Param('An optional parameter', type=int, default=42),
        'param2': Param('A mandatory parameter', type=int, mandatory=True,
                        settable=True, category='instrument'),
        'failinit': Param('If true, fail the doInit() call', type=bool,
                          default=False),
        'failshutdown': Param('If true, fail the doShutdown() call', type=bool,
                              default=False),
    }

    def doInit(self, mode):
        if self.failinit:
            1/0  # pylint: disable=W0104
        self._val = 0
        methods_called.add('doInit')

    def doShutdown(self):
        if self.failshutdown:
            raise Exception('shutdown failure')
        methods_called.add('doShutdown')

    def doRead(self, maxage=0):
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

    def doFinish(self):
        methods_called.add('doFinish')

    def isAtTarget(self, pos):
        methods_called.add('isAtTarget')
        return self.target == pos

    def doStatus(self, maxage=0):
        return status.OK, 'idle'

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
        return [('testkey', 'testval', 'testval', '', 'instrument')]

    def doVersion(self):
        return [('testversion', 1.0)]

    @usermethod
    @requires(level=ADMIN, mode=MAINTENANCE)
    def calibrate(self):
        return True


class Bus(HasCommunication, Device):

    _replyontry = 5

    def _llcomm(self, msg):
        if self._replyontry == 0:
            return 'reply: ' + msg
        self._replyontry -= 1
        raise Exception

    def _com_raise(self, err, info):
        raise CommunicationError(self, info)

    def _com_return(self, result, info):
        return result[7:]  # strip 'reply: '

    def communicate(self, msg):
        return self._com_retry('', self._llcomm, msg)


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
    before = session.testhandler._messages

    assert raises(ZeroDivisionError, session.getDevice, 'dev2_5')
    assert session.testhandler._messages > before
    assert 'could not shutdown after creation failed' \
        in session.testhandler._warnings[-1].msg
    # assert device is cleaned up anyway
    assert 'dev2_5' not in session.devices


def test_special_methods():
    dev = session.getDevice('dev2_1')
    # pickling a device should yield its name as a string
    import pickle
    assert pickle.loads(pickle.dumps(dev)) == 'dev2_1'
    # test that the repr() works
    assert dev.name in repr(dev)


def test_attached_devices_property():
    dev1 = session.getDevice('dev1')
    dev2 = session.getDevice('dev2_1')
    # stupid name: _attached_<name of attachment>
    assert dev2._attached_attached == dev1


def test_params():
    dev2 = session.getDevice('dev2_1')
    # make sure adev instances are created
    assert isinstance(dev2._attached_attached, Dev1)
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
    assert raises(UsageError, dev2.setPar, 'param3', 1)
    assert raises(UsageError, dev2.getPar, 'param3')


def test_methods():
    dev2 = session.getDevice('dev2_3')
    assert 'doInit' in methods_called
    dev2.move(10)
    dev2.maw(10)
    assert 'doStart' in methods_called
    assert 'doIsAllowed' in methods_called
    # moving beyond limits
    assert raises(LimitError, dev2.move, 50)
    # or forbidden by doIsAllowed()
    assert raises(LimitError, dev2.move, 5)
    # read() and status()
    assert dev2.read() == 10
    assert dev2.status()[0] == status.OK
    # __call__ interface
    dev2(7)
    assert dev2() == 7
    # further methods
    dev2.reset()
    assert 'doReset' in methods_called
    dev2.stop()
    assert 'doStop' in methods_called
    dev2.wait()
    assert 'doFinish' in methods_called
    assert 'isAtTarget' in methods_called
    # test info() method
    keys = set(value[0] for value in dev2.info())
    assert 'testkey' in keys
    assert 'param2' in keys
    assert 'value' in keys
    assert 'status' in keys
    # loglevel
    dev2.loglevel = 'info'
    assert raises(ConfigurationError, setattr, dev2, 'loglevel', 'xxx')
    # test version() method
    assert ('testversion', 1.0) in dev2.version()

    # test access control (test session always returns False for access check)
    assert raises(AccessError, dev2.calibrate)


def test_is_at_target():
    # check target warning behavior in finish
    dev2 = session.getDevice('dev2_3')
    dev2.start(0)
    assert not session.testhandler.warns(dev2.finish)
    dev2.start(1)
    dev2._val = 0.5
    assert session.testhandler.warns(dev2.finish)


def test_fix_and_release():
    # fixing and releasing
    dev2 = session.getDevice('t_mtt')
    dev2.curvalue = 7
    dev2.curstatus = (status.OK, '')
    dev2.fix('blah')
    try:
        dev2.move(7)  # allowed, since we are at 7 already
        assert session.testhandler.warns(dev2.move, 9)
    finally:
        dev2.release()
    dev2.move(7)
    # fixing and do not stop
    dev2.curvalue = 9
    dev2.curstatus = (status.BUSY, 'moving')
    # fixing while busy should emit a warning
    assert session.testhandler.warns(dev2.fix, 'do not stop in fixed mode')
    assert dev2.status()[0] == status.BUSY
    try:
        dev2.stop()
        assert dev2.status()[0] == status.BUSY
    finally:
        dev2.release()
    dev2.stop()
    assert dev2.status()[0] == status.OK


def test_limits():
    dev2 = session.getDevice('dev2_3')
    # abslimits are (0, 10) as set in configuration
    dev2.userlimits = dev2.abslimits
    assert dev2.userlimits == dev2.abslimits
    # individual getters/setters
    dev2.usermin, dev2.usermax = dev2.absmin + 1, dev2.absmax - 1
    assert (dev2.usermin, dev2.usermax) == (1, 9)
    assert raises(ConfigurationError, setattr, dev2, 'usermin', dev2.absmin - 1)
    assert raises(ConfigurationError, setattr, dev2, 'usermax', dev2.usermin - 0.5)
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


def test_hascomm():
    bus = session.getDevice('bus')

    bus._replyontry = 5
    assert raises(CommunicationError, bus.communicate, 'test')

    bus._replyontry = 2
    assert bus.communicate('test') == 'test'
