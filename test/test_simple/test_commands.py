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

"""NICOS commands tests."""

import os
import shutil
import tempfile
import timeit

from nicos.core import GUEST, UsageError, LimitError, NicosError, status as \
    devstatus
from nicos.utils import ensureDirectory

from nicos.commands import usercommandWrapper
from nicos.commands.measure import count
from nicos.commands.device import move, maw, drive, switch, wait, read, \
    status, stop, reset, get, getall, setall, fix, release, adjust, \
    version, history, info, limits, resetlimits, ListParams, ListMethods, \
    ListDevices, unfix, reference, finish
from nicos.commands.device import set  # pylint: disable=W0622
from nicos.commands.basic import help, dir  # pylint: disable=W0622
from nicos.commands.basic import ListCommands, sleep, \
    NewSetup, AddSetup, RemoveSetup, ListSetups, \
    LogEntry, _LogAttach, SetErrorAbort, \
    CreateDevice, RemoveDevice, CreateAllDevices, \
    NewExperiment, FinishExperiment, AddUser, \
    Remark, SetMode, ClearCache, UserInfo, run, \
    notify, SetMailReceivers, SetDataReceivers
from nicos.commands.sample import NewSample, SetSample, SelectSample, \
    ClearSamples, ListSamples
from nicos.commands.output import printdebug, printinfo, printwarning, \
    printerror, printexception
from nicos.core.sessions.utils import MASTER, SLAVE

from test.utils import ErrorLogged, raises

import pytest

session_setup = 'test_commands'


class TestBasic(object):

    def test_output_commands(self, session, log):
        with log.assert_msg_matches(r'printdebugtest1 printdebugtest2'):
            printdebug('printdebugtest1', 'printdebugtest2')
        with log.assert_msg_matches(r'printinfo testing\.\.\.'):
            printinfo('printinfo testing...')
        with log.assert_warns():
            printwarning('warn!')
        assert raises(ErrorLogged, printerror, 'error!')
        assert raises(ErrorLogged, printexception, 'exception!')

    def test_basic_commands(self, session, log):
        with log.assert_msg_matches([r'Usage: help\(\[object\]\)',
                                     r'>>> help\(\) {12}# show list of commands']):
            help(help)
        with log.assert_msg_matches([r'name {48}description',
                                     # explicitly no check on help text!
                                     r'ClearCache\(dev, \.\.\.\)']):
            ListCommands()

    def test_sleep_command(self, session, log):
        tosleep = 0.1
        with log.assert_msg_matches(r'sleeping for %.1f seconds\.\.\.' % tosleep):
            used = timeit.timeit(lambda: sleep(tosleep), number=1)
        assert tosleep < used < 1.3 * tosleep

    def test_setup_commands(self, session, log):
        with log.assert_msg_matches([r'axis +yes', r'stdsystem +yes',
                                     r'cache +(?!yes)']):  # cache not loaded
            ListSetups()

        NewSetup('axis')
        AddSetup()  # should list all setups but not fail
        AddSetup('slit')
        assert 'slit' in session.configured_devices  # not autocreated
        RemoveSetup('slit')
        assert 'slit' not in session.configured_devices
        with log.assert_warns('is not a loaded setup, ignoring'):
            RemoveSetup('blah')

    def test_devicecreation_commands(self, session, log):
        if 'motor' in session.devices:
            RemoveDevice('motor')
        assert 'motor' not in session.devices

        CreateDevice('motor')
        assert 'motor' in session.devices

        RemoveDevice('motor')
        assert raises(UsageError, RemoveDevice)
        assert 'motor' not in session.devices
        CreateAllDevices()
        assert 'motor' in session.devices
        assert 'motor' in session.explicit_devices
        assert 'coder' in session.devices
        assert 'coder' not in session.explicit_devices

    def test_mode_commands(self, session):
        SetMode(SLAVE)
        SetMode(MASTER)
        assert raises(UsageError, SetMode, 'blah')

    def test_clearcache(self, session, log):
        with UserInfo('userinfo'):
            assert session._actionStack[-1] == 'userinfo'

        motor = session.getDevice('motor')
        with log.assert_msg_matches('cleared cached information for motor'):
            ClearCache('motor', motor)

    def test_command_exceptionhandling(self, session):
        # basic commands should catch exceptions when wrapped as usercommands
        # (but log an error) depending on setting on the experiment
        wrapped_maw = usercommandWrapper(maw)
        dev = session.getDevice('motor')
        assert dev.usermin == -100

        SetErrorAbort(False)
        try:
            wrapped_maw(dev, -150)
        except ErrorLogged:
            pass
        else:
            assert False, 'no error raised and no error logged'

        SetErrorAbort(True)
        assert raises(LimitError, wrapped_maw, dev, -150)

    def test_commands_elog(self, session):
        LogEntry('== some subheading\n\nThis is a logbook entry.')
        fd, tmpname = tempfile.mkstemp()
        os.close(fd)
        shutil.copyfile(__file__, tmpname)
        _LogAttach('some file description', [tmpname], ['newname.txt'])


def test_experiment_commands(session, log):
    exp = session.experiment

    with log.assert_msg_matches([r'Exp : experiment directory is now .*',
                                 r'Exp : User "F. X. User <user@example.com>" '
                                 'added']):
        NewExperiment(1234, 'Test experiment',
                      'L. Contact <l.contact@frm2.tum.de>', '1. User')
        assert exp.proposal == 'p1234'
        assert exp.title == 'Test experiment'
        AddUser('F. X. User', 'user@example.com')
        assert 'F. X. User <user@example.com>' in exp.users

    NewSample('MnSi', lattice=[4.58] * 3, angles=[90] * 3)

    FinishExperiment()

    Remark('hi')
    assert exp.remark == 'hi'


def test_run_command(session, log):
    exp = session.experiment
    exp.new(0, user='user')
    # create a test script in the current scriptpath
    ensureDirectory(session.experiment.scriptpath)
    with open(os.path.join(session.experiment.scriptpath, 'test.py'), 'w') as f:
        f.write('read()')
    run('test')


def test_sample_commands(session, log):
    exp = session.experiment
    exp.new(0, user='user')
    NewSample('abc')
    assert exp.sample.samplename == 'abc'
    assert exp.samples == {0: {'name': 'abc'}}

    SetSample(1, 'def', param=45)
    assert exp.samples[1] == {'name': 'def', 'param': 45}

    SelectSample(1)
    assert exp.sample.samplename == 'def'
    SelectSample('abc')
    assert exp.sample.samplename == 'abc'

    with log.assert_msg_matches([r'number  sample name  param',
                                 r'0 +abc',
                                 r'1 +def +45']):
        ListSamples()

    with log.assert_no_msg_matches([r'0 +abc',
                                    r'1 +def +45']):
        ClearSamples()
    assert exp.samples == {}


class TestDevice(object):

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        """Prepare a clean setup for each test on device commands."""
        motor = session.getDevice('motor')

        yield

        motor.speed = 0
        motor.maw(0)
        tdev = session.getDevice('tdev')
        tdev._start_exception = None
        tdev._stop_exception = None
        tdev._read_exception = None

    def test_device_class(self, session):
        motor = session.getDevice('motor')
        d = dir(motor)
        assert 'start' in d
        assert 'doStart' not in d
        assert '_getFromCache' not in d
        d = dir()
        assert 'd' in d

    def test_move(self, session, log):
        """Check move() command."""
        motor = session.getDevice('motor')
        for pos in (min(motor.abslimits), 0, max(motor.abslimits)):
            move(motor, pos)
            motor.wait()
            assert motor.curvalue == pos

        assert raises(LimitError, move, motor, max(motor.abslimits) + 1)

        assert raises(UsageError, move)
        assert raises(UsageError, move, motor, 1, motor)

    def test_maw(self, session, log):
        """Check maw() command."""
        motor = session.getDevice('motor')
        for pos in (min(motor.abslimits), 0, max(motor.abslimits)):
            maw(motor, pos)
            assert motor.curvalue == pos

    def test_drive_and_switch(self, session, log):
        """Check drive() and switch() aliases."""
        motor = session.getDevice('motor')
        drive(motor, 0)
        assert motor.curvalue == 0
        switch(motor, 1)
        assert motor.curvalue == 1

    def test_wait(self, session, log):
        """Check wait() command."""
        motor = session.getDevice('motor')
        tdev = session.getDevice('tdev')
        tdev._status_exception = NicosError('expected failed status')
        move(motor, 10)
        wait(motor, 0.1)
        # session.log.error('expl. devices: %r', session.explicit_devices)
        wait()
        with log.assert_errors(r'expected failed status'):
            wait(tdev)
            tdev._status_exception = None

    def test_read(self, session, log):
        """Check read() command."""
        motor = session.getDevice('motor')
        coder = session.getDevice('coder')
        exp = session.getDevice('Exp')
        tdev = session.getDevice('tdev')
        tdev._status_exception = NicosError('expected failed status')
        tdev._read_exception = NicosError('expected failed read')

        read()
        read(motor, coder)
        with log.assert_errors(r'expected failed read'):
            read(tdev)
        assert raises(UsageError, read, exp)
        # ensure that target != position to generate a read message containing
        # a 'target' entry
        s = motor.speed
        motor.speed = 0.1
        move(motor, 1)
        stop(motor)
        with log.assert_msg_matches(r'target'):
            read(motor)
        motor.speed = s

    def test_status(self, session, log):
        """Check status() command."""
        motor = session.getDevice('motor')
        coder = session.getDevice('coder')
        tdev = session.getDevice('tdev')
        tdev._status_exception = NicosError('expected failed status')
        tdev._read_exception = NicosError('expected failed read')
        status()
        status(motor, coder, tdev)
        with log.assert_errors('expected failed read'):
            tdev._status_exception = None
            tdev.warnlimits = [-4.99, 4.99]
            status(tdev)
            tdev._status_exception = NicosError('expected failed status')

    def test_stop(self, session, log):
        """Check stop() command."""
        motor = session.getDevice('motor')
        tdev = session.getDevice('tdev')
        tdev._stop_exception = NicosError('expected failed stop')

        stop()
        stop(motor, tdev)
        # check stop moving motor
        move(motor, 10)
        stop(motor)

        # Change the user level to lower access rights to check that the stop
        # on higher level requesting devices will be ignored
        AddSetup('device')
        pdev = session.getDevice('privdev')
        speed = pdev.speed
        pdev.speed = 0.1
        move(pdev, 10)
        level = session.getExecutingUser().level
        session.setUserLevel(GUEST)
        assert pdev.status(0)[0] == devstatus.BUSY
        stop(pdev)
        assert pdev.status(0)[0] == devstatus.BUSY
        session.setUserLevel(level)
        stop(pdev)
        wait(pdev)
        assert pdev.status(0)[0] == devstatus.OK
        pdev.speed = speed

    def test_reset(self, session, log):
        """Check reset() command."""
        motor = session.getDevice('motor')
        reset(motor)
        reset()

    def test_set_and_get(self, session, log):
        """Check set() and get() commands."""
        motor = session.getDevice('motor')
        set(motor, 'speed', 10)
        assert motor.speed == 10
        get(motor, 'speed')
        with log.assert_errors('device has no parameter'):
            set(motor, 'noparam', '')

    def test_all_set_and_get(self, session, log):
        """Check getall() and setall() commands."""
        motor = session.getDevice('motor')
        getall('speed')
        setall('speed', 0)
        assert motor.speed == 0

    def test_info(self, session, log):
        """Check info()."""
        with log.assert_msg_matches([r'Device status',
                                     r'motor +status: +ok: idle']):
            info()

    def test_fix_and_release(self, session, log):
        """Check fix() and release() commands."""
        motor = session.getDevice('motor')
        move(motor, 0)
        fix(motor)
        move(motor, 10)
        stop(motor)
        release(motor)
        assert motor.curvalue == 0
        assert raises(UsageError, release)
        assert raises(UsageError, release, ())
        assert raises(UsageError, unfix, ())

    def test_adjust(self, session, log):
        """Check adjust() command."""
        motor = session.getDevice('motor')
        maw(motor, 1)
        adjust(motor, 0)
        assert motor() == 0
        assert motor.offset == 1
        assert motor.target == 0
        adjust(motor, 0, 1)
        assert motor() == 1
        assert motor.offset == 0
        assert motor.target == 1

    def test_version(self, session, log):
        """Check version() command."""
        motor = session.getDevice('motor')
        version(motor)
        # check the NICOS version
        version()

    def test_history(self, session, log):
        """Check history() command."""
        motor = session.getDevice('motor')
        history(motor)
        history(motor, 'value')
        # check history of parameter and automatic adding of fromtime
        history(motor, 'speed')
        history(motor, -24)
        history(motor, 24)
        # check adjusting totime
        history(motor, totime=10)
        history(motor, 'value', -24)
        for timespec in ['1 week', '30 minutes', '2012-01-01',
                         '2012-01-01 14:00', '14:00']:
            history(motor, 'value', timespec)

    def test_limits(self, session, log):
        """Check limits() command."""
        m4 = session.getDevice('m4')
        motor = session.getDevice('motor')
        coder = session.getDevice('coder')

        with log.assert_msg_matches([r'limits for this device',
                                     r'absolute limits',
                                     r'user limits']):
            limits(motor, m4)
        with log.assert_warns(r'device has no limits'):
            limits(coder)
        limits()

    def test_resetlimits(self, session, log):
        """Check resetlimits() command."""
        m4 = session.getDevice('m4')
        motor = session.getDevice('motor')
        coder = session.getDevice('coder')
        CreateDevice('motor')  # needs to be explicit
        motor.userlimits = (1, 1)
        resetlimits(motor, coder, m4)
        assert motor.userlimits == motor.abslimits
        # check resetting of all devices having limits
        motor.userlimits = (-0.5, 0.5)
        resetlimits()
        assert motor.userlimits == motor.abslimits

    def test_lists(self, session, log):
        """Check ListParams(), ListMethods(), ListDevices() commands."""
        motor = session.getDevice('motor')
        alias = session.getDevice('aliasAxis')
        exp = session.getDevice('Exp')
        ListParams(motor)
        # ListParams of the 'aliased' device
        ListParams(alias)
        ListMethods(motor)
        # exp contains 'usermethods' which should be listed too
        ListMethods(exp)
        ListDevices()

    def test_count(self, session, log):
        """Check count() command."""
        motor = session.getDevice('motor')
        assert raises(UsageError, count, motor)
        count()

    def test_finish(self, session, log):
        """Check finish() command."""
        finish()
        det = session.getDevice('det')
        finish(det)

    def test_reference(self, session, log):
        """Check reference() command."""
        motor = session.getDevice('motor')
        with log.assert_errors('has no reference function'):
            reference(motor)
        axis = session.getDevice('nocoder_axis')
        axis.maw(1)
        reference(axis)
        assert axis.read(0) == 0.0


def test_notifiers(session):
    notifier = session.getDevice('testnotifier')
    exp = session.getDevice('Exp')

    notifier.reset()
    assert notifier.receivers == []
    receiver = 'receiver@example.com'
    SetMailReceivers(receiver)
    assert notifier.receivers == [receiver]

    notifier.clear()
    notify('something\nimportant')
    assert notifier._messages == [('something', 'something\nimportant',
                                   None, None, False)]

    notifier.clear()
    notify('subject', 'body')
    assert notifier._messages == [('subject', 'body', None, None, False)]

    assert raises(UsageError, notify, 'lots', 'of', 'args')

    # store current state
    msrv, msend = exp.mailserver, exp.mailsender
    exp.mailserver = 'localhost'
    exp.mailsender = 'noreply@example.com'
    SetDataReceivers(receiver)
    # restore previous state
    exp.mailserver, exp.mailsender = msrv, msend
    assert exp.propinfo['user_email'] == [receiver]
