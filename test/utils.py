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

"""NICOS test suite utilities."""

import os
import re
import sys
import time
import shutil
import socket
import subprocess
from os import path
from logging import ERROR, WARNING
from functools import wraps

from nose.tools import assert_raises #pylint: disable=E0611
from nose.plugins.skip import SkipTest

from nicos.core import Moveable, HasLimits, DataSink, status
from nicos.core.sessions import Session
from nicos.utils.loggers import ColoredConsoleHandler, NicosLogger

rootdir = path.join(os.path.dirname(__file__), 'root')


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

# from unittest.Testcase
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
            if record.exc_info:
                # raise the original exception
                raise record.exc_info[1], None, record.exc_info[2]
            else:
                raise ErrorLogged(record.message)
        elif record.levelno >= WARNING:
            self._warnings.append(record)
        else:
            self._messages += 1
        ColoredConsoleHandler.emit(self, record)

    def enable_raising(self, raising):
        self._raising = raising

    def warns(self, func, *args, **kwds):
        plen = len(self._warnings)
        func(*args, **kwds)
        plen_after = len(self._warnings)
        if plen == plen_after:
            return False
        if plen + 1 == plen_after:
            return True
        sys.stderr.write('More then one warning added')
        print >> sys.stderr, plen, plen_after, self._warnings
        return False

    def emits_message(self, func, *args, **kwds):
        before = self._messages
        func(*args, **kwds)
        return self._messages > before


class TestSession(Session):
    autocreate_devices = False

    def __init__(self, appname):
        Session.__init__(self, appname)
        self._mode = 'master'
        self.setSetupPath(path.join(path.dirname(__file__), 'setups'))

    def createRootLogger(self, prefix='nicos'):
        self.log = NicosLogger('nicos')
        self.log.parent = None
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
        exec code in self.namespace, self.local_namespace

TestSession.config.user = None
TestSession.config.group = None
TestSession.config.control_path = rootdir


class TestDevice(HasLimits, Moveable):

    def doInit(self, mode):
        self._value = 0
        self._start_exception = None
        self._read_exception = None
        self._status_exception = None

    def doRead(self, maxage=0):
        if self._read_exception is not None:
            raise self._read_exception
        return self._value

    def doStart(self, target):
        if self._start_exception is not None and target != 0:
            raise self._start_exception
        self._value = target

    def doWait(self):
        return self._value

    def doStatus(self, maxage=0):
        if self._status_exception is not None:
            raise self._status_exception
        return status.OK, 'fine'


class TestSink(DataSink):

    def doInit(self, mode):
        self.clear()

    def clear(self):
        self._calls = []
        self._info = []
        self._points = []

    def prepareDataset(self, dataset):
        self._calls.append('prepareDataset')

    def beginDataset(self, dataset):
        self._calls.append('beginDataset')

    def addInfo(self, dataset, category, valuelist):
        self._calls.append('addInfo')
        self._info.extend(valuelist)

    def addPoint(self, dataset, xvalues, yvalues):
        self._calls.append('addPoint')
        self._points.append(xvalues + yvalues)

    def addBreak(self, dataset):
        self._calls.append('addBreak')

    def endDataset(self, dataset):
        self._calls.append('endDataset')


def cleanup():
    if path.exists(rootdir):
        shutil.rmtree(rootdir)
    os.mkdir(rootdir)
    os.mkdir(rootdir + '/cache')
    os.mkdir(rootdir + '/pid')

def startCache(setup='cache', wait=5):
    global cache  #pylint: disable=W0603
    sys.stderr.write(' [cache start... ')

    # start the cache server
    os.environ['PYTHONPATH'] = path.join(rootdir, '..', '..', 'lib')
    cache = subprocess.Popen([sys.executable,
                              path.join(rootdir, '..', 'cache.py'), setup])
    if wait:
        start = time.time()
        while time.time() < start + wait:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(('localhost', 14877))
            except socket.error:
                time.sleep(0.2)
            else:
                s.close()
                break
        else:
            raise Exception('cache failed to start within %s sec' % wait)
    sys.stderr.write('%s ok] ' % cache.pid)
    return cache

def killCache(cache):
    sys.stderr.write(' [cache kill %s... ' % cache.pid)
    if cache.poll() is None:
        cache.terminate()
        cache.wait()
    sys.stderr.write('ok] ')
