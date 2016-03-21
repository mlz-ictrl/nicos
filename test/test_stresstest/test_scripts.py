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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

import os
import re
import logging
from os import path

from nicos.utils import loggers
from nicos.core.sessions.simple import ScriptSession
from nicos.pycompat import exec_

# import all public symbols from nicos.core to get all nicos exceptions
from nicos.core import *  # pylint: disable=unused-wildcard-import,wildcard-import


from test.utils import raises, assert_raises


class ScriptSessionTest(ScriptSession):
    def __init__(self, appname, daemonized=False):
        ScriptSession.__init__(self, appname, daemonized)
        self.setSetupPath(
            path.normpath(path.join(path.dirname(__file__), '../setups')))

    def createRootLogger(self, prefix='nicos', console=True):
        self.log = loggers.NicosLogger('nicos')
        self.log.parent = None
        # show errors on the console
        handler = logging.StreamHandler()
        handler.setLevel(logging.WARNING)
        handler.setFormatter(
            logging.Formatter('[SCRIPT] %(name)s: %(message)s'))
        self.log.addHandler(handler)
        log_path = path.join(path.dirname(__file__), '../root', 'log')
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
            self.log.error('cannot open log file: %s' % err)


def run_script_session(setup, code):
    from nicos import session
    session.__class__ = ScriptSessionTest
    session.__init__('TestScriptSession')
    session.handleInitialSetup(setup)
    try:
        exec_(code, session.namespace)
    finally:
        session.shutdown()


def test_simple():
    run_script_session('startup', 'print("Test")')


def test_raise_simple():
    code = 'raise Exception("testing")'
    setup = 'startup'
    assert raises(Exception, run_script_session, setup, code)


def test_scripts():
    def raises(*args):
        assert_raises(*args)
    # test generator executing scripts
    testscriptspath = path.normpath(
        path.join(path.dirname(__file__), '..', 'scripts'))
    allscripts = []
    matcher = re.compile(r'.*Raises(.*)\..*')
    for root, _dirs, files in os.walk(testscriptspath):
        allscripts += [path.join(root, f) for f in files]
    setup = 'script_tests'
    for fn in allscripts:
        with open(fn) as codefile:
            code = codefile.read()
        m = matcher.match(fn)
        if m:
            etype = eval(m.group(1))
            raises.description = '%s.test_scripts:%s' % \
                (test_scripts.__module__, path.basename(fn))
            yield raises, etype, run_script_session, setup, code
        else:
            run_script_session.description = '%s.test_scripts:%s' % \
                (test_scripts.__module__, path.basename(fn))
            yield run_script_session, setup, code
