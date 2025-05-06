# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS device class test suite."""

import os

import pytest

from nicos.commands.basic import NewSetup
from nicos.core import ADMIN, GUEST, AccessError, Attach, CanDisable, \
    CommunicationError, ConfigurationError, Device, HasCommunication, \
    HasLimits, HasOffset, LimitError, Moveable, NicosError, Param, \
    ProgrammingError, UsageError, requires, secret, status, usermethod
from nicos.core.device import DeviceMetaInfo, DeviceParInfo
from nicos.core.sessions.utils import MAINTENANCE
from nicos.utils.credentials import keystore

from test.utils import raises

session_setup = 'device'
methods_called = set()


class Dev1(Device):
    pass


class Dev2(HasLimits, HasOffset, CanDisable, Moveable):
    attached_devices = {
        'attached':  Attach('Test attached device', Dev1),
        'attlist':   Attach('Test list of attached devices', Dev1,
                            multiple=True, optional=True),
        'missingok': Attach('Test missing attached devices', Moveable,
                            missingok=True, optional=True),
    }
    parameters = {
        'param1': Param('An optional parameter', type=int, default=42,
                        prefercache=False),
        'param2': Param('A mandatory parameter', type=int, mandatory=True,
                        settable=True, category='instrument'),
        'failinit': Param('If true, fail the doInit() call', type=bool,
                          default=False),
        'failshutdown': Param('If true, fail the doShutdown() call', type=bool,
                              default=False),
    }

    def doInit(self, mode):
        if self.failinit:
            raise ZeroDivisionError
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

    def doStart(self, target):
        self._val = target
        methods_called.add('doStart')

    def doStop(self):
        methods_called.add('doStop')

    def doFinish(self):
        methods_called.add('doFinish')

    def isAtTarget(self, pos=None, target=None):
        if target is None:
            target = self.target
        if pos is None:
            pos = self.read(0)
        methods_called.add('isAtTarget')
        return target == pos

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
        return [DeviceMetaInfo(
            'testkey', DeviceParInfo('testval', 'testval', '', 'instrument'))]

    def doVersion(self):
        return [('testversion', 1.0)]

    def doEnable(self, on):
        methods_called.add('doEnable %s' % on)

    @usermethod
    @requires(level=ADMIN, mode=MAINTENANCE)
    def calibrate(self):
        return True


class Dev3(HasLimits, HasOffset, Moveable):
    parameters = {
        'offsetsign': Param('Offset sign', type=int, settable=True),
    }

    def doRead(self, maxage=0):
        return self._val - self.offsetsign * self.offset

    def doStart(self, target):
        self._val = target + self.offsetsign * self.offset

    def doAdjust(self, oldvalue, newvalue):
        self.offset += self.offsetsign * (oldvalue - newvalue)


class Dev4(Device):

    parameters = {
        'intparam': Param('internal parameter', internal=True),
        'param': Param('non-internal parameter'),
        'intexplicit': Param('internal parameter with explicit userparam',
                             internal=True, userparam=True),
        'explicit': Param('non-internal parameter with explicit userparam '
                          'setting', userparam=False),
    }


class DevSecret(Device):
    parameters = {
        'verysecretval': Param('a secret param', type=secret),
    }


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


def test_initialization(session, log):
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

    with log.assert_warns('could not shutdown after creation failed'):
        assert raises(ZeroDivisionError, session.getDevice, 'dev2_5')
    # assert device is cleaned up anyway
    assert 'dev2_5' not in session.devices

    # assert parameter configured although declared internal
    with log.assert_warns(
            "'intparam' is configured in a setup file although declared as "
            "internal parameter"):
        session.getDevice('dev4')


def test_special_methods(session):
    dev = session.getDevice('dev2_1')
    # pickling a device should yield its name as a string
    import pickle
    assert pickle.loads(pickle.dumps(dev)) == 'dev2_1'
    # test that the repr() works
    assert dev.name in repr(dev)


def test_attached_devices_property(session):
    dev1 = session.getDevice('dev1')
    dev2 = session.getDevice('dev2_1')
    # stupid name: _attached_<name of attachment>
    assert dev2._attached_attached == dev1


def test_inline_attached_devices(session):
    dev0 = session.getDevice('dev2_0')
    single = session.getDevice('dev2_0_attached')
    assert dev0._attached_attached == single
    list1 = session.getDevice('dev2_0_attlist1')
    list2 = session.getDevice('dev2_0_attlist2')
    assert dev0._attached_attlist == [list1, list2]


def test_missingok_attached_devices(session):
    dev0 = session.getDevice('dev2_0')
    assert dev0._attached_missingok is None


def test_params(session):
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
    assert raises(NicosError, setattr, dev2, 'param3', 1)
    # test parameter value when in cache, but default value updated
    session.cache.put(dev2, 'param1', 50)
    session.createDevice('dev2_1', recreate=True)
    # restored the default value from the code?
    assert dev2.param1 == 42
    # test default values for userparam in respect to internal
    dev4 = session.getDevice('dev4')
    assert dev4.parameters['intparam'].userparam is False
    assert dev4.parameters['param'].userparam is True
    # test explicit userparam settings in respect to internal
    assert dev4.parameters['intexplicit'].userparam is True
    assert dev4.parameters['explicit'].userparam is False
    # ambiguous parameter settings of internal and mandatory should raise
    assert raises(ProgrammingError, Param, 'ambiguous', internal=True,
                  mandatory=True)


def test_forbidden_assignments(session):
    dev = session.getDevice('dev2_1')
    # test assignment of a value to a device method must fail
    assert raises(UsageError, setattr, dev, 'read', 0)
    # changing valuetype function must be allowed
    dev.valuetype = float
    assert dev.valuetype == float
    # internal variable '_val' exists and must be changeable
    dev._val = 10
    assert dev._val == 10
    # creating a new member must be allowed
    dev._myval = 1
    assert dev._myval == 1
    # creating a new method must be allowed
    dev._myfunction = float
    assert dev._myfunction(1) == 1
    # changing a internal function to a value must be allowed
    dev._myfunction = 1
    assert dev._myfunction == 1


def test_params_fromconfig(session):
    NewSetup('vmotor1')
    motor = session.getDevice('vmotor')
    # min/max parameters got from motor device
    assert motor.abslimits == (-100, +100)
    # usermin/usermax parameters in the config
    assert motor.userlimits == (-100, +100)

    NewSetup('vmotor2')
    motor = session.getDevice('vmotor')
    # min/max parameters got from motor device
    assert motor.abslimits == (-100, +80)
    # usermin/usermax parameters in the config
    assert motor.userlimits == (-100, +80)


def test_methods(session):
    dev2 = session.getDevice('dev2_3')
    dev2.userlimits = dev2.abslimits
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
    dev2.enable()
    assert 'doEnable True' in methods_called
    dev2.disable()
    assert 'doEnable False' in methods_called

    # test info() method
    keys = set(value[0] for value in dev2.info())
    assert 'testkey' in keys
    assert 'param2' in keys
    assert 'value' in keys
    assert 'status' in keys
    # test version() method
    assert ('testversion', 1.0) in dev2.version()

    # test access control (test session always returns False for access check)
    assert raises(AccessError, dev2.calibrate)


def test_loglevel(session, log):
    dev2 = session.getDevice('dev2_3')

    # reject invalid loglevels
    assert raises(ConfigurationError, setattr, dev2, 'loglevel', 'xxx')

    # ensure that changing loglevels is effective
    dev2.loglevel = 'info'
    with log.assert_no_msg_matches('debug message'):
        dev2.log.debug('debug message')
    dev2.loglevel = 'debug'
    with log.assert_msg_matches('debug message'):
        dev2.log.debug('debug message')


def test_is_at_target(session, log):
    # check target warning behavior in finish
    dev2 = session.getDevice('dev2_3')
    dev2.start(0)
    with log.assert_warns(count=0):
        dev2.finish()
    dev2.start(1)
    dev2._val = 0.5
    with log.assert_warns('did not reach target', count=1):
        dev2.finish()


def test_fix_and_release(session, log):
    # fixing and releasing
    dev2 = session.getDevice('mot')
    dev2.curvalue = 7
    dev2.curstatus = (status.OK, '')
    dev2.fix('blah')
    try:
        dev2.move(7)  # allowed, since we are at 7 already
        with log.assert_warns('device fixed, not moving'):
            dev2.move(9)
    finally:
        dev2.release()
    dev2.move(7)
    # fixing and do not stop
    dev2.curvalue = 9
    dev2.curstatus = (status.BUSY, 'moving')
    # fixing while busy should emit a warning
    with log.assert_warns('device appears to be busy'):
        dev2.fix()
    assert dev2.status()[0] == status.BUSY
    try:
        dev2.stop()
        assert dev2.status()[0] == status.BUSY
    finally:
        dev2.release()
    dev2.stop()
    assert dev2.status()[0] == status.OK


def test_fix_and_release_block(session, log):
    dev2 = session.getDevice('mot')
    assert dev2.fix('blah')
    assert dev2.fix('blubb')
    assert dev2.fixedby == ('system', ADMIN)
    dev2._setROParam('fixedby', ('guest', GUEST))
    assert dev2.fix('blah')
    with session.withUserLevel(GUEST):
        with log.allow_errors():
            assert not dev2.fix('blah')
            assert not dev2.release()
    assert dev2.release()
    assert dev2.release()


def test_fix_superdev(session, log):
    dev = session.getDevice('dev2_6')
    adev = dev._attached_missingok
    adev.maw(0)
    dev.fix('fix superdevice')
    adev.maw(1)
    assert adev.read() == 0
    dev.release()
    adev.maw(1)
    assert adev.read() == 1


def test_fix_recursive_superdev(session, log):
    dev = session.getDevice('dev2_7')
    mot = dev._attached_missingok._attached_motor
    mot.maw(0)
    dev.fix('fix supersuperdevice')
    mot.maw(1)
    assert mot.read() == 0
    dev.release()
    mot.maw(1)
    assert mot.read() == 1


def test_limits(session, log):
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
    with log.assert_warns('current device value .* not within new userlimits'):
        dev2.userlimits = (0, 4)


@pytest.mark.parametrize('new_abslimits,new_userlimits',
                         [((-20, -10), (-20, -10)),  # completely outside
                          ((-5, 5), (0, 5)),         # half inside
                          ((-2, 12), (0, 10)),       # completely inside
                          ((5, 15), (5, 10)),        # other half inside
                          ((20, 30), (20, 30))])     # completely outside
def test_reset_limits(session, log, new_abslimits, new_userlimits):
    # check proper resetting of userlimits after abslimits change
    dev2 = session.createDevice('dev2_3')
    assert dev2.abslimits == (0, 10)  # from setup file
    dev2.userlimits = (0, 10)
    session.destroyDevice('dev2_3')
    session.configured_devices['dev2_3'][1]['abslimits'] = new_abslimits
    try:
        dev2 = session.createDevice('dev2_3')
        assert dev2.abslimits == new_abslimits
        assert dev2.userlimits == new_userlimits
    finally:
        session.configured_devices['dev2_3'][1]['abslimits'] = (0, 10)


def test_hascomm(session):
    bus = session.getDevice('bus')

    bus._replyontry = 5
    assert raises(CommunicationError, bus.communicate, 'test')

    bus._replyontry = 2
    assert bus.communicate('test') == 'test'


def test_special_params():
    # check that special parameter names cannot be used in "parameters"
    for param in ('value', 'status'):
        assert raises(ProgrammingError,
                      type, 'Dev', (Device,),
                      dict(__module__='dummy',
                           parameters={param: Param('...')}))


def test_offset_sign(session):
    dev = session.getDevice('dev3')

    assert dev.offset == 0
    dev.move(1)
    assert dev._val == 1

    dev.offsetsign = 1
    dev.doAdjust(1, 0)
    assert dev.offset == 1
    assert dev.read(0) == 0

    dev.offset = 0

    dev.offsetsign = -1
    dev.doAdjust(1, 0)
    assert dev.offset == -1
    assert dev.read(0) == 0


def test_secret_device(session):
    dev = session.getDevice('dev_secret')
    try:
        keystore.nicoskeystore.delCredential('secretenv')
    except Exception:
        # raises if key is not in keystore, but always cleanup in case of fails
        pass
    assert dev.verysecretval.lookup() not in ['env', 'store']
    os.environ['NICOS_SECRETENV'] = 'env'
    assert dev.verysecretval.lookup() == 'env'
    keystore.nicoskeystore.setCredential('secretenv', 'store')
    assert dev.verysecretval.lookup() == 'store'
    keystore.nicoskeystore.delCredential('secretenv')
