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

"""Pytest configuration file containing fixtures for individual tests."""

import os
import re
import sys
import time
from os import path
from pathlib import Path
from time import monotonic, sleep

import pytest

from nicos import config, session as nicos_session
from nicos.core import MASTER
from nicos.utils import tcpSocket, updateFileCounter

from test.utils import TestSession, cache_addr, cleanup, daemon_addr, \
    killSubprocess, startCache, startElog, startSubprocess


def pytest_configure(config):
    os.environ['PYTEST_QT_API'] = 'pyqt%s' % os.environ.get('NICOS_QT', '5')


# This fixture will run during the entire test suite.  Therefore, the special
# cache stress tests must use a different port.
@pytest.fixture(scope='session', autouse=True)
def setup_test_suite():
    """General test suite setup (handles cacheserver and elog server)"""
    # make the test suite run the same independent of the hostname
    os.environ['INSTRUMENT'] = 'test'
    try:
        cleanup()
    except OSError:
        sys.stderr.write('Failed to clean up old test dir. Check if NICOS '
                         'processes are still running.')
        sys.stderr.write('=' * 80)
        raise
    cache = startCache(cache_addr)
    elog = startElog()
    yield
    killSubprocess(elog)
    killSubprocess(cache)


@pytest.fixture(scope='class')
def session(request):
    """Test session fixture"""

    nicos_session.__class__ = TestSession
    # pylint: disable=unnecessary-dunder-call
    nicos_session.__init__(request.module.__name__)
    # override the sessionid: test module, and a finer resolved timestamp
    nicos_session.sessionid = '%s-%s' % (request.module.__name__, time.time())
    nicos_session.setMode(getattr(request.module, 'session_mode', MASTER))
    if request.module.session_setup:
        nicos_session.unloadSetup()
        nicos_session._setup_info = {}
        r = re.compile('nicos_[a-z]*')
        p = Path(request.node.fspath.dirname)
        if list(filter(r.match, p.parts)):
            while p.match('test_*'):
                p = p.parent
            nicos_session.setSetupPath(*(nicos_session.getSetupPath() +
                                         ['%s' % p.joinpath('setups')]))
        nicos_session.loadSetup(request.module.session_setup,
                                **getattr(request.module,
                                          'session_load_kw', {}))
    yield nicos_session
    nicos_session.shutdown()


@pytest.fixture(scope='class')
def dataroot(request, session):
    """Dataroot handling fixture"""

    exp = session.experiment
    dataroot = path.join(config.nicos_root, request.module.exp_dataroot)
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    updateFileCounter(counter, 'scan', 42)
    updateFileCounter(counter, 'point', 42)

    exp._setROParam('dataroot', dataroot)
    exp.new(1234, user='testuser')
    exp.sample.new({'name': 'mysample'})

    return dataroot


@pytest.fixture
def log(session):
    """Clear nicos log handler content"""
    handler = session.testhandler
    handler.clear()
    return handler


def daemon_wait_cb():
    start = monotonic()
    wait = 10
    sock = None
    while monotonic() < start + wait:
        try:
            sock = tcpSocket(daemon_addr, 0)
        except OSError:
            sleep(0.02)
        else:
            break
        finally:
            if sock:
                sock.close()
    else:
        raise Exception('daemon failed to start within %s sec' % wait)


@pytest.fixture(scope='session')
def daemon():
    """Start a nicos daemon"""

    daemon = startSubprocess('daemon', wait_cb=daemon_wait_cb)
    yield
    killSubprocess(daemon)
