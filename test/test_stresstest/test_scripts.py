#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

import os
import re
import logging
from os import path

import pytest

from nicos.core.sessions.simple import ScriptSession
from nicos.utils import loggers
from nicos.pycompat import exec_

# import all public symbols from nicos.core to get all nicos exceptions
from nicos.core import *  # pylint: disable=unused-wildcard-import,wildcard-import


from test.utils import module_root, runtime_root, raises


class ScriptSessionTest(ScriptSession):
    def __init__(self, appname, daemonized=False):
        ScriptSession.__init__(self, appname, daemonized)
        self.setSetupPath(path.join(module_root, 'test', 'setups'))

    def createRootLogger(self, prefix='nicos', console=True):
        if self.log:
            self._closeLogStreams()
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        # show errors on the console
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter('[SCRIPT] %(name)s: %(message)s'))
        self.log.addHandler(handler)
        log_path = path.join(runtime_root, 'log')
        try:
            if prefix == 'nicos':
                self.log.addHandler(loggers.NicosLogfileHandler(
                    log_path, 'nicos', str(os.getpid())))
                # handler for master session only
                self._master_handler = loggers.NicosLogfileHandler(log_path)
                self._master_handler.disabled = True
                self.log.addHandler(self._master_handler)
            else:
                self.log.addHandler(loggers.NicosLogfileHandler(log_path, prefix))
                self._master_handler = None
        except (IOError, OSError) as err:
            self.log.error('cannot open log file: %s', err)

    def shutdown(self):
        self._closeLogStreams()
        ScriptSession.shutdown(self)

    def _closeLogStreams(self):
        for h in self.log.handlers:
            try:
                h.close()
            except Exception:
                pass
            self.log.removeHandler(h)


@pytest.fixture()
def session(request):
    """Script test session fixture"""

    from nicos import session
    session.__class__ = ScriptSessionTest
    session.__init__('TestScriptSession')
    yield session
    session.shutdown()


def run_script_session(session, setup, code):
    session.handleInitialSetup(setup)
    try:
        exec_(code, session.namespace)
    finally:
        session.shutdown()


def test_simple(session):
    run_script_session(session, 'startup', 'print("Test")')


def test_raise_simple(session):
    code = 'raise Exception("testing")'
    setup = 'startup'
    assert raises(Exception, run_script_session, session, setup, code)


testscriptspath = path.join(module_root, 'test', 'scripts')


@pytest.mark.parametrize('script', [f for f in os.listdir(testscriptspath)
                                    if f.endswith('.nic')])
def test_one_script(session, script):
    script = path.join(testscriptspath, script)
    with open(script) as codefile:
        code = codefile.read()
    m = re.match(r'.*Raises(.*)\..*', script)
    if m:
        expected = eval(m.group(1))
        assert raises(expected, run_script_session, session,
                      'script_tests', code)
    else:
        # expected success
        run_script_session(session, 'script_tests', code)
