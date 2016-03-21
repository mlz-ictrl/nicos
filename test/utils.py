#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
import time
import shutil
import signal
import socket
import subprocess
from os import path
from logging import ERROR, WARNING, DEBUG
from functools import wraps

from nose.tools import istest, assert_raises  # pylint: disable=E0611
from nose.plugins.skip import SkipTest

from nicos import config
from nicos.core import Moveable, HasLimits, DataSink, DataSinkHandler, \
    status
from nicos.core.sessions import Session
from nicos.core.sessions.utils import MASTER
from nicos.devices.notifiers import Mailer
from nicos.utils import tcpSocket
from nicos.utils.loggers import ColoredConsoleHandler, NicosLogger
from nicos.pycompat import exec_, reraise

# try to get the nose conf singleton provided by the noseglobalconf plugin
# if it is not available,  set verbosity to 2.
try:
    from noseglobalconf import noseconf
except ImportError:
    class DummyConf(object):
        pass
    noseconf = DummyConf()
    noseconf.verbosity = 2


rootdir = path.join(os.path.dirname(__file__), 'root')
pythonpath = None


def gen_if_verbose(func):
    '''Wrapper to reduce verbosity for test-generator functions
    '''

    @wraps(func)
    def new_func():
        if noseconf.verbosity >= 3:
            for f_args in func():
                def run(r_args):
                    r_args[0](*r_args[1:])
                run.description =f_args[0].description
                yield run, f_args
        else:
            @istest
            def collecttests():
                for f_args in func():
                    f_args[0](*f_args[1:])
            yield collecttests
    return new_func


def raises(exc, *args, **kwds):
    assert_raises(exc, *args, **kwds)
    return True


def requires(condition, message=''):
    """Decorator to mark test functions as skips depending on a condition."""
    def deco(func):
        @wraps(func)
        def new_func(*args, **kwds):
            if not condition:
                raise SkipTest(message or 'skipped due to condition')
            return func(*args, **kwds)
        return new_func
    return deco


def assert_response(resp, contains=None, matches=None):
    """Check for specific strings in a response array.

    resp: iterable object containing reponse strings
    contains: string to check for presence, does string comparison
    matches: regexp to search for in response
    """
    if contains:
        assert contains in resp, "Response does not contain %r" % contains

    if matches:
        reg = re.compile(matches)
        for sub in resp:
            found = reg.findall(sub)
            if len(found):
                return True
        assert False, "Response does not match %r" % matches


# from unittest.TestCase
def assertAlmostEqual(first, second, places=7, msg=None):
    """Fail if the two objects are unequal as determined by their
       difference rounded to the given number of decimal places
       (default 7) and comparing to zero.

       Note that decimal places (from zero) are usually not the same
       as significant digits (measured from the most signficant digit).
    """
    if round(abs(second - first), places) != 0:
        assert False, \
            (msg or '%r != %r within %r places' % (first, second, places))


def assertNotAlmostEqual(first, second, places=7, msg=None):
    """Fail if the two objects are equal as determined by their
       difference rounded to the given number of decimal places
       (default 7) and comparing to zero.

       Note that decimal places (from zero) are usually not the same
       as significant digits (measured from the most signficant digit).
    """
    if round(abs(second - first), places) == 0:
        assert False, \
            (msg or '%r == %r within %r places' % (first, second, places))


class ErrorLogged(Exception):
    """Raised when an error is logged by NICOS."""


class TestLogHandler(ColoredConsoleHandler):
    def __init__(self):
        ColoredConsoleHandler.__init__(self)
        self._warnings = []
        self._raising = True
        self._messages = 0

    def emit(self, record):
        if record.levelno >= ERROR and self._raising:
            raise ErrorLogged(record.message)
        elif record.levelno >= WARNING:
            self._warnings.append(record)
        else:
            self._messages += 1
        ColoredConsoleHandler.emit(self, record)

    def enable_raising(self, raising):
        self._raising = raising

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
            print (ret)
            print (self._warnings)
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


class TestSession(Session):
    autocreate_devices = False

    def __init__(self, appname, daemonized=False):
        Session.__init__(self, appname, daemonized)
        self._mode = MASTER
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = NicosLogger('nicos')
        self.log.parent = None
        self.log.setLevel(DEBUG)
        self.testhandler = TestLogHandler()
        self.log.addHandler(self.testhandler)
        self._master_handler = None

    def runsource(self, source, filename='<input>', symbol='single'):
        """Mostly copied from code.InteractiveInterpreter, but added the
        logging call before runcode().
        """
        code = self.commandHandler(source,
                                   lambda src: compile(src, filename, symbol))
        if code is None:
            return
        exec_(code, self.namespace)

config.user = None
config.group = None
config.nicos_root = rootdir


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
    if path.exists(rootdir):
        shutil.rmtree(rootdir)
    os.mkdir(rootdir)
    os.mkdir(rootdir + '/cache')
    os.mkdir(rootdir + '/pid')
    os.mkdir(rootdir + '/bin')
    shutil.copy(path.join(rootdir, '..', 'simulate.py'),
                rootdir + '/bin/nicos-simulate')


def adjustPYTHONPATH():
    global pythonpath  # pylint: disable=global-statement
    if pythonpath is None:
        topdir = path.abspath(path.join(rootdir, '..', '..'))
        pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
        pythonpath.insert(0, topdir)
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
                             path.join(rootdir, '..', filename)] + list(args),
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


def startCache(setup='cache', wait=10):
    # start the cache server
    def cache_wait_cb():
        if wait:
            start = time.time()
            while time.time() < start + wait:
                try:
                    s = tcpSocket('localhost', getCachePort())
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


def getCachePort():
    return int(os.environ.get('NICOS_CACHE_PORT', 14877))


def getCacheNameAndPort(host):
    return '%s:%d' % (host, getCachePort())


def getDaemonPort():
    return int(os.environ.get('NICOS_DAEMON_PORT', 14874))


def selfDestructAfter(seconds):
    """If possible, setup a SIGALRM after *seconds* to clean up otherwise
    hanging test processes.
    """
    if hasattr(signal, 'alarm'):
        signal.alarm(seconds)
