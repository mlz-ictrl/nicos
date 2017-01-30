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

import pytest

from nicos import session as nicos_session
from nicos.core import MASTER

from test.utils import cleanup, startCache, startSubprocess, killSubprocess, \
    getCacheAddr, TestSession


# This fixture will run during the entire test suite.  Therefore, the special
# cache stresstests must use a different port.
@pytest.yield_fixture(scope='session', autouse=True)
def setup_test_suite():
    # make the test suite run the same independent of the hostname
    os.environ['INSTRUMENT'] = 'test'
    try:
        cleanup()
    except OSError:
        sys.stderr.write('Failed to clean up old test dir. Check if NICOS '
                         'processes are still running.')
        sys.stderr.write('=' * 80)
        raise
    cache = startCache(getCacheAddr())
    elog = startSubprocess('elog.py')
    yield
    killSubprocess(elog)
    killSubprocess(cache)


@pytest.yield_fixture(scope='module')
def session(request):
    nicos_session.__class__ = TestSession
    nicos_session.__init__(request.module.__name__)
    # override the sessionid: test module, and a finer resolved timestamp
    nicos_session.sessionid = '%s-%s' % (request.module.__name__, time.time())
    nicos_session.setMode(getattr(request.module, 'session_mode', MASTER))
    if request.module.session_setup:
        nicos_session.loadSetup(request.module.session_setup,
                                **getattr(request.module,
                                          'session_load_kw', {}))
    if getattr(request.module, 'session_spmode', False):
        nicos_session.setSPMode(True)
    yield nicos_session
    nicos_session.setSPMode(False)
    nicos_session.data.reset()
    nicos_session.shutdown()


@pytest.yield_fixture
def log(session):
    handler = session.testhandler
    handler.clearcapturedmessages()
    yield handler
    handler.clearcapturedmessages()
