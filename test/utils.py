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

"""NICOS test suite utilities."""

from __future__ import print_function

import os
import re
import sys
import math
import time
import shutil
import signal
import socket
import contextlib
import subprocess
from os import path
from logging import ERROR, WARNING, DEBUG, StreamHandler, Formatter

import mock
import pytest

from nicos import config
from nicos.core import ACCESS_LEVELS, AccessError, Moveable, HasLimits, \
    DataSink, DataSinkHandler, Attach, status, system_user
from nicos.core.mixins import IsController
from nicos.core.sessions import Session
from nicos.devices.abstract import CanReference
from nicos.devices.generic import VirtualMotor
from nicos.devices.notifiers import Mailer
from nicos.devices.cacheclient import CacheClient
from nicos.services.cache.database import FlatfileCacheDatabase
from nicos.utils import tcpSocket, closeSocket, createSubprocess
from nicos.utils.loggers import NicosLogger, ACTION
from nicos.pycompat import exec_, reraise, string_types

# The NICOS checkout directory, where to find modules.
module_root = path.normpath(path.join(path.dirname(__file__), '..'))
# The temporary root directory, where to put data/logs/pid files during test.
runtime_root = os.environ.get('NICOS_TEST_ROOT',
                              path.join(path.dirname(__file__), 'root'))

# Addresses for services, ports can be allocated by Jenkins.
cache_addr = 'localhost:%s' % os.environ.get('NICOS_CACHE_PORT', 14877)
alt_cache_addr = 'localhost:%s' % os.environ.get('NICOS_CACHE_ALT_PORT', 14878)
daemon_addr = 'localhost:%s' % os.environ.get('NICOS_DAEMON_PORT', 14874)

pythonpath = None


config.user = None
config.group = None
config.nicos_root = runtime_root
config.pid_path = path.join(runtime_root, 'pid')
config.logging_path = path.join(runtime_root, 'log')


def raises(exc, *args, **kwds):
    pytest.raises(exc, *args, **kwds)
    return True


class approx(object):
    """
    Ported from py.test v3.0, can use pytest.approx from then on.
    """

    def __init__(self, expected, rel=None, abs=None):  # pylint: disable=redefined-builtin
        self.expected = expected
        self.abs = abs
        self.rel = rel

    def __repr__(self):
        if isinstance(self.expected, complex):
            return str(self.expected)
        if math.isinf(self.expected):
            return str(self.expected)
        try:
            vetted_tolerance = '{:.1e}'.format(self.tolerance)
        except ValueError:
            vetted_tolerance = '???'
        if sys.version_info[0] == 2:
            return '{0} +- {1}'.format(self.expected, vetted_tolerance)
        else:
            return u'{0} \u00b1 {1}'.format(self.expected, vetted_tolerance)

    def __eq__(self, actual):
        if actual == self.expected:
            return True
        if math.isinf(abs(self.expected)):
            return False
        return abs(self.expected - actual) <= self.tolerance

    __hash__ = None

    def __ne__(self, actual):
        return not (actual == self)

    @property
    def tolerance(self):
        def set_default(x, default):
            return x if x is not None else default
        absolute_tolerance = set_default(self.abs, 1e-12)
        if absolute_tolerance < 0:
            raise ValueError("absolute tolerance can't be negative: {}".
                             format(absolute_tolerance))
        if math.isnan(absolute_tolerance):
            raise ValueError("absolute tolerance can't be NaN.")
        if self.rel is None:
            if self.abs is not None:
                return absolute_tolerance
        relative_tolerance = set_default(self.rel, 1e-6) * abs(self.expected)
        if relative_tolerance < 0:
            raise ValueError("relative tolerance can't be negative: {}".
                             format(absolute_tolerance))
        if math.isnan(relative_tolerance):
            raise ValueError("relative tolerance can't be NaN.")
        return max(relative_tolerance, absolute_tolerance)


class ErrorLogged(Exception):
    """Raised when an error is logged by NICOS."""


class TestLogHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self, sys.stdout)
        self.setFormatter(
            Formatter('%(levelname)-7s : %(name)s : %(message)s\n'))
        self.clear()

    def clear(self):
        self._raising = True
        self._errors = []
        self._warnings = []
        self._messages = []

    def emit(self, record):
        if record.levelno == ACTION:
            return
        msg = self.format(record)
        if record.levelno >= ERROR:
            # On error messages, we normally raise an exception so that any
            # errors logged during the test suite do not pass silently.  This
            # can be temporarily changed using the allow_errors() and
            # expect_errors() context managers.
            if self._raising:
                raise ErrorLogged(record.message)
            self._errors.append(msg)
        elif record.levelno >= WARNING:
            self._warnings.append(msg)
        self._messages.append(msg)
        try:
            self.stream.write(msg)
        except UnicodeEncodeError:
            self.stream.write(msg.encode('utf-8'))
        except ValueError:
            # Closed pytest capture stream, ignore.
            return
        self.stream.flush()

    @contextlib.contextmanager
    def allow_errors(self):
        """Return a context manager that while active, prevents raising an
        exception when an error is logged.
        """
        self._raising = False
        yield
        self._raising = True

    @contextlib.contextmanager
    def assert_msg_matches(self, regexes):
        """Check that the context code logs a message for each of the given
        regexes.
        """
        start = len(self._messages)
        yield
        if not isinstance(regexes, list):
            regexes = [regexes]
        for regex in regexes:
            rx = re.compile(regex)
            for msg in self._messages[start:]:
                if rx.search(msg):
                    break
            else:
                assert False, 'No message matching %r' % regex

    @contextlib.contextmanager
    def assert_no_msg_matches(self, regexes):
        """Check that the context code logs no message that matches the
        given regexes.
        """
        start = len(self._messages)
        yield
        if not isinstance(regexes, list):
            regexes = [regexes]
        for regex in regexes:
            rx = re.compile(regex)
            for msg in self._messages[start:]:
                if rx.search(msg):
                    assert False, 'Message %r matches %r' % (msg, regex)

    def _assert_msglist_contains(self, what, msglist, regex, count):
        emitted = len(msglist)
        if count is not None and emitted != count:
            assert False, '%d %s emitted, %d expected' % (emitted, what, count)
        elif count is None and not emitted:
            assert False, 'No %s emitted, at least one expected' % what
        if regex is not None:
            rx = re.compile(regex)
            for msg in msglist:
                if rx.search(msg):
                    break
            else:
                assert False, 'No %s match %r' % (what, regex)

    @contextlib.contextmanager
    def assert_warns(self, regex=None, count=None):
        """Check the warnings that the context code emits.

        If *count* is given, exactly *count* warnings must be emitted.  If
        *regex* is given, at least one warning must match the regex.
        """
        start = len(self._warnings)
        yield
        self._assert_msglist_contains('warnings', self._warnings[start:],
                                      regex, count)

    @contextlib.contextmanager
    def assert_errors(self, regex=None, count=None):
        """Check the errors that the context code emits.

        If *count* is given, exactly *count* errors must be emitted.  If
        *regex* is given, at least one error must match the regex.
        """
        start = len(self._errors)
        self._raising = False
        yield
        self._raising = True
        self._assert_msglist_contains('errors', self._errors[start:],
                                      regex, count)

    def get_messages(self):
        return self._messages


class TestCacheClient(CacheClient):

    _use_cache = True
    _cached_socket = None

    def _connect(self):
        # Keep the main cache connection open throughout the test suite run.
        # This will stop different cache connections overlapping with the
        # cache clear we need between test functions.
        with mock.patch('nicos.devices.cacheclient.tcpSocket',
                        self._open_cached_socket):
            return CacheClient._connect(self)

    def _disconnect(self, why=''):
        with mock.patch('nicos.devices.cacheclient.closeSocket',
                        self._close_cached_socket):
            CacheClient._disconnect(self, why)

    def _open_cached_socket(self, *args, **kwds):
        if not TestCacheClient._use_cache:
            return tcpSocket(*args, **kwds)
        if TestCacheClient._cached_socket is None:
            TestCacheClient._cached_socket = tcpSocket(*args, **kwds)
        return TestCacheClient._cached_socket

    def _close_cached_socket(self, sock):
        if sock is not TestCacheClient._cached_socket:
            closeSocket(sock)

    def _connect_action(self):
        # On connect, clear cached entries before querying values and updates
        self._socket.sendall(b'__clear__=1\n')
        CacheClient._connect_action(self)

    def lock(self, key, ttl=None, unlock=False, sessionid=None):
        # Do not try to get/release the master lock in the test session.
        # We have too many setup changes with/without cache to do that
        # correctly all the time.
        #
        # Note that CacheClient.lock is still tested in the elog subprocess.
        pass


class TestCacheDatabase(FlatfileCacheDatabase):

    def tell(self, key, value, time, ttl, from_client):
        # Special feature for the test suite to clear all keys quickly.
        if key == '__clear__':
            with self._cat_lock:
                self._cat.clear()
            return
        FlatfileCacheDatabase.tell(self, key, value, time, ttl, from_client)


class TestSession(Session):
    autocreate_devices = False
    has_datamanager = True
    cache_class = TestCacheClient

    def __init__(self, appname, daemonized=False):
        old_setup_info = getattr(self, '_setup_info', {})
        Session.__init__(self, appname, daemonized)
        self._setup_info = old_setup_info
        self._setup_paths = (path.join(module_root, 'test', 'setups'),)
        self._user_level = system_user.level

    def readSetupInfo(self):
        # since we know the setups don't change, only read them once
        if not self._setup_info:
            return Session.readSetupInfo(self)
        return self._setup_info

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = NicosLogger('nicos')
        self.log.parent = None
        self.log.setLevel(DEBUG)
        self.testhandler = TestLogHandler()
        self.log.addHandler(self.testhandler)
        self._master_handler = None

    def runsource(self, source, filename='<input>', symbol='single'):
        code = self.commandHandler(source,
                                   lambda src: compile(src, filename, symbol))
        if code is None:
            return
        exec_(code, self.namespace)

    def delay(self, _secs):
        # Not necessary for test suite.
        pass

    def _string_to_level(self, level):
        if isinstance(level, string_types):
            for k, v in ACCESS_LEVELS.items():
                if v == level:
                    return k
            raise ValueError('invalid access level name: %r' % level)
        return level

    def setUserLevel(self, level):
        self._user_level = self._string_to_level(level)

    def checkAccess(self, required):
        if 'level' in required:
            rlevel = self._string_to_level(required['level'])
            if rlevel > self._user_level:
                raise AccessError('%s access is not sufficient, %s access '
                                  'is required' % (
                                      ACCESS_LEVELS.get(self._user_level,
                                                        str(self._user_level)),
                                      ACCESS_LEVELS.get(rlevel, str(rlevel))))
        return Session.checkAccess(self, required)


class TestDevice(HasLimits, Moveable):

    def doInit(self, mode):
        self._value = 0
        self._start_exception = None
        self._read_exception = None
        self._status_exception = None
        self._stop_exception = None

    def doRead(self, maxage=0):
        if self._read_exception is not None:
            raise self._read_exception  # pylint: disable=E0702
        return self._value

    def doStart(self, target):
        if self._start_exception is not None and target != 0:
            raise self._start_exception  # pylint: disable=E0702
        self._value = target

    def doStatus(self, maxage=0):
        if self._status_exception is not None:
            raise self._status_exception  # pylint: disable=E0702
        return status.OK, 'fine'

    def doStop(self):
        if self._stop_exception is not None:
            raise self._stop_exception  # pylint: disable=E0702


class TestController(IsController, Moveable):

    attached_devices = {
        'dev1':  Attach('First device', Moveable),
        'dev2':  Attach('Second device', Moveable),
    }

    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev == self._attached_dev1:
            other = self._attached_dev2.read()
            if other < adevtarget:
                return (False, 'dev1 can only move to values smaller'
                               ' than %r' % other)
        if adev == self._attached_dev2:
            other = self._attached_dev1.read()
            if other > adevtarget:
                return (False, 'dev2 can only move to values greater'
                               ' than %r' % other)
        return (True, 'Allowed')

    def doRead(self, maxage=0):
        return self._value

    def doIsAllowed(self, target):
        if target[0] > target[1]:
            return (False, 'dev1 can only move to values greater'
                           ' than dev2')
        return (True, 'Allowed')

    def doStart(self, target):
        self._value = target
        self._attached_dev1.start(target[0])
        self._attached_dev2.start(target[1])


class TestSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self.clear()

    def clear(self):
        self._calls = []

    def prepare(self):
        self._calls.append('prepare')

    def begin(self):
        self._calls.append('begin')

    def putMetainfo(self, metainfo):
        self._calls.append('putMetainfo')

    def putValues(self, values):
        self._calls.append('putValues')

    def putResults(self, quality, results):
        self._calls.append('putResults')

    def addSubset(self, subset):
        self._calls.append('addSubset')

    def end(self):
        self._calls.append('end')


class TestSink(DataSink):

    handlerclass = TestSinkHandler
    _handlers = []

    def createHandlers(self, dataset):
        handlers = DataSink.createHandlers(self, dataset)
        self._handlers = handlers
        return handlers


class TestNotifier(Mailer):
    # inherits from Mailer to be handled by SetMailReceivers

    def doInit(self, mode):
        self.clear()

    def clear(self):
        self._messages = []

    def send(self, subject, body, what=None, short=None, important=True):
        self._messages.append((subject, body, what, short, important))


class TestReferenceMotor(CanReference, VirtualMotor):

    def doReference(self):
        # Enforce a change in current position
        self.curvalue = 0


def cleanup():
    if path.exists(runtime_root):
        shutil.rmtree(runtime_root)
    os.mkdir(runtime_root)
    os.mkdir(path.join(runtime_root, 'cache'))
    os.mkdir(path.join(runtime_root, 'pid'))
    os.mkdir(path.join(runtime_root, 'bin'))
    shutil.copy(path.join(module_root, 'test', 'bin', 'simulate'),
                path.join(runtime_root, 'bin', 'nicos-simulate'))


def adjustPYTHONPATH():
    # pylint: disable=global-statement
    global pythonpath
    if pythonpath is None:
        pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
        pythonpath.insert(0, module_root)
        os.environ['PYTHONPATH'] = os.pathsep.join(pythonpath)


def startSubprocess(filename, *args, **kwds):
    adjustPYTHONPATH()
    name = path.splitext(filename)[0]
    sys.stderr.write(' [%s start... ' % name)
    if kwds.get('piped'):
        popen_kwds = dict(stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        popen_kwds = dict()
    proc = createSubprocess(
        [sys.executable, path.join(module_root, 'test', 'bin', filename)] +
        list(args), **popen_kwds)
    proc.nicos_name = name
    if 'wait_cb' in kwds:
        try:
            kwds['wait_cb']()
        except Exception:
            caught = sys.exc_info()
            sys.stderr.write('%s failed]' % proc.pid)
            try:
                proc.kill()
            except Exception:
                pass
            proc.wait()
            reraise(*caught)
    sys.stderr.write('%s ok]\n' % proc.pid)
    return proc


def killSubprocess(proc):
    sys.stderr.write(' [%s terminate %s...' % (proc.nicos_name, proc.pid))
    if proc.poll() is None:
        proc.terminate()
        start = time.time()
        while time.time() < start + 2:
            time.sleep(0.05)
            if proc.poll() is not None:
                break
        else:
            sys.stderr.write(' kill...')
            proc.kill()
            proc.wait()
    sys.stderr.write(' ok]\n')


def startCache(hostport, setup='cache', wait=10):
    # start the cache server
    def cache_wait_cb():
        if wait:
            start = time.time()
            while time.time() < start + wait:
                try:
                    s = tcpSocket(hostport, 0)
                except socket.error:
                    time.sleep(0.02)
                except Exception as e:
                    sys.stderr.write('%r' % e)
                    raise
                else:
                    s.close()
                    break
            else:
                raise Exception('cache failed to start within %s sec' % wait)
    cache = startSubprocess('cache', setup, wait_cb=cache_wait_cb)
    return cache


def hasGnuplot():
    """Check for the presence of gnuplot in the environment.

    To be used with the `requires` decorator.
    """
    try:
        gpProcess = createSubprocess(b'gnuplot', shell=True,
                                     stdin=subprocess.PIPE, stdout=None)
        gpProcess.communicate(b'exit')
        if gpProcess.returncode:
            return False
    except (IOError, ValueError):
        return False
    return True


def selfDestructAfter(seconds):
    """If possible, setup a SIGALRM after *seconds* to clean up otherwise
    hanging test processes.
    """
    if hasattr(signal, 'alarm'):
        signal.alarm(seconds)
