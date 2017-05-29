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

"""Py.test configuration file containing fixtures for individual tests."""

import os
import sys
import time
from os import path

import pytest

from nicos import config, session as nicos_session
from nicos.core import MASTER
from nicos.utils import updateFileCounter

from test.utils import cleanup, startCache, startSubprocess, killSubprocess, \
    cache_addr, TestSession


# This fixture will run during the entire test suite.  Therefore, the special
# cache stresstests must use a different port.
@pytest.yield_fixture(scope='session', autouse=True)
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
    elog = startSubprocess('elog')
    yield
    killSubprocess(elog)
    killSubprocess(cache)


@pytest.yield_fixture(scope='class')
def session(request):
    """Test session fixture"""

    nicos_session.__class__ = TestSession
    nicos_session.__init__(request.module.__name__)
    # override the sessionid: test module, and a finer resolved timestamp
    nicos_session.sessionid = '%s-%s' % (request.module.__name__, time.time())
    nicos_session.setMode(getattr(request.module, 'session_mode', MASTER))
    if request.module.session_setup:
        nicos_session.unloadSetup()
        nicos_session.loadSetup(request.module.session_setup,
                                **getattr(request.module,
                                          'session_load_kw', {}))
    if getattr(request.module, 'session_spmode', False):
        nicos_session.setSPMode(True)
    yield nicos_session
    nicos_session.setSPMode(False)
    nicos_session.data.reset()
    nicos_session.shutdown()


@pytest.fixture(scope='class')
def dataroot(request, session):
    """Dataroot handling fixture"""

    exp = session.experiment
    dataroot = path.join(config.nicos_root, request.module.exp_dataroot)
    os.makedirs(dataroot)

    counter = path.join(dataroot, exp.counterfile)
    open(counter, 'w').close()
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
