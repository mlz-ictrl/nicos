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
import subprocess
from os import path
from logging import ERROR, WARNING, DEBUG

import pytest

from nicos import config
from nicos.core import Moveable, HasLimits, DataSink, DataSinkHandler, \
    status
from nicos.core.sessions import Session
from nicos.devices.notifiers import Mailer
from nicos.devices.cacheclient import CacheClient
from nicos.utils import tcpSocket
from nicos.utils.loggers import ColoredConsoleHandler, NicosLogger
from nicos.pycompat import exec_, reraise

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


class TestLogHandler(ColoredConsoleHandler):
    def __init__(self):
        ColoredConsoleHandler.__init__(self)
        self._warnings = []
        self._raising = True
        self._messages = 0
        self._capturedmessages = []

    def emit(self, record):
        if record.levelno >= ERROR and self._raising:
            raise ErrorLogged(record.message)
        elif record.levelno >= WARNING:
            self._warnings.append(record)
        else:
            self._messages += 1
            self._capturedmessages.append(self.xformat(record))
        try:
            ColoredConsoleHandler.emit(self, record)
        except ValueError:
            # Closed capture device, ignore.
            pass

    def xformat(self, record):
        if record.name == 'nicos':
            namefmt = ''
        else:
            namefmt = '%(name)-10s: '
        fmtstr = '%s%%(levelname)s: %%(message)s' % namefmt
        fmtstr = '%(filename)s' + fmtstr
        s = fmtstr % record.__dict__
        return s

    def clearcapturedmessages(self):
        # XXX: clear warnings too!
        self._capturedmessages = []

    def dump_messages(self, where=''):
        """Helper to get message content for test preparation."""
        print("#" * 10 + ' ' + where + ' ' + '#' * 10, file=sys.stderr)
        for m in self._capturedmessages:
            print(m, file=sys.stderr)
        print("#" * 60, file=sys.stderr)

    def enable_raising(self, raising):
        self._raising = raising

    def assert_response(self, contains=None, matches=None):
        """Check for specific strings in a response array.

        resp: iterable object containing reponse strings
        contains: string to check for presence, does string comparison
        matches: regexp to search for in response
        """
        if contains:
            assert contains in self._capturedmessages, \
                "Response does not contain %r" % contains

        if matches:
            reg = re.compile(matches)
            for sub in self._capturedmessages:
                found = reg.findall(sub)
                if len(found):
                    return True
            self.dump_messages('')
            assert False, "Response does not match %r" % matches

    def assert_notresponse(self, contains=None, matches=None):
        """Check for the absences of specific strings in a response array.

        resp: iterable object containing reponse strings
        contains: string to check for absence, does string comparison
        matches: regexp to search for in response
        """
        if contains:
            assert contains not in self._capturedmessages, \
                "Response does contain %r" % contains

        if matches:
            reg = re.compile(matches)
            for sub in self._capturedmessages:
                found = reg.findall(sub)
                if len(found):
                    self.dump_messages('')
                    assert False, "Response does match %r" % matches
        return True

    def check_response(self, contains=None, matches=None, absent=False):
        """Check response messages for the presence/absence of string.

        *contains* string checked for string equality in messages
        *matches* regex to search in messages
        *absent* if True, check for absence of string
        """
        if absent:
            return self.assert_notresponse(contains, matches)
        return self.assert_response(contains, matches)

    def warns(self, func, *args, **kwds):
        """check if a warning is emitted

            arguments:
            ``func``: Function Under Test (FUT)
            ``warns_clear``:
                clear warnings before running the FUT
            ``warns_text``:
                if present, a regex to test the warning messages for.
            All other arguments a passed to the FUT
        """

        if kwds.pop('warns_clear', None):
            self.clear_warnings()
        _text = kwds.pop('warns_text', None)

        plen = len(self._warnings)
        ret = func(*args, **kwds)
        plen_after = len(self._warnings)
        if plen == plen_after:
            print(ret)
            print(self._warnings)
            return False
        if not _text:
            if plen + 1 == plen_after:
                return True
            else:
                sys.stderr.write('More then one warning added')
            for msg in self._warnings:
                sys.stderr.write(msg.getMessage())
            return False
        else:
            for msg in self._warnings:
                if re.search(_text, msg.getMessage()):
                    return True
            sys.stderr.write('Specified text not in any warning:')
            for msg in self._warnings:
                sys.stderr.write('MSG: ' + msg.getMessage())

            return False

    def emits_message(self, func, *args, **kwds):
        before = self._messages
        func(*args, **kwds)
        return self._messages > before

    def clear_messages(self):
        self._messages = 0

    def clear_warnings(self):
        self._warnings = []
        self.clear_messages()


class TestCacheClient(CacheClient):

    # Do not try to get/release the master lock in the test session.
    # We have too many setup changes with/without cache to do that
    # correctly all the time.

    # Note that CacheClient.lock is still tested in the elog subprocess.

    def lock(self, key, ttl=None, unlock=False, sessionid=None):
        pass


class TestSession(Session):
    autocreate_devices = False
    has_datamanager = True
    cache_class = TestCacheClient

    def __init__(self, appname, daemonized=False):
        Session.__init__(self, appname, daemonized)
        self.setSetupPath(path.join(module_root, 'test', 'setups'))

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


class TestDevice(HasLimits, Moveable):

    def doInit(self, mode):
        self._value = 0
        self._start_exception = None
        self._read_exception = None
        self._status_exception = None

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


def cleanup():
    if path.exists(runtime_root):
        shutil.rmtree(runtime_root)
    os.mkdir(runtime_root)
    os.mkdir(path.join(runtime_root, 'cache'))
    os.mkdir(path.join(runtime_root, 'pid'))
    os.mkdir(path.join(runtime_root, 'bin'))
    shutil.copy(path.join(module_root, 'test', 'simulate.py'),
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
    proc = subprocess.Popen([sys.executable,
                             path.join(module_root, 'test', filename)] +
                            list(args),
                            **popen_kwds)
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
    cache = startSubprocess('cache.py', setup, wait_cb=cache_wait_cb)
    return cache


def hasGnuplot():
    """Check for the presence of gnuplot in the environment.

    To be used with the `requires` decorator.
    """
    try:
        gpProcess = subprocess.Popen(b'gnuplot', shell=True,
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
