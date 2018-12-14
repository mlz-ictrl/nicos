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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS custom lib tests: dry-run instrument test scripts with the real
instrument setups.
"""

from __future__ import absolute_import, division, print_function

import os
from logging import ERROR, LogRecord
from os import path

from test.utils import module_root

from nicos import session
from nicos.core.sessions.simulation import SimulationSupervisor
from nicos.core.utils import system_user
from nicos.pycompat import configparser

import pytest

from uuid import uuid1

session_setup = None


class Request(object):

    def __init__(self, uuid, code):
        self.user = None
        self.text = code
        self.reqid = '%s' % uuid

    def serialize(self):
        return {'reqid': self.reqid, 'user': '', 'text': self.text}

    # Simstate/ETA support, unneeded

    def updateRuntime(self, block, time):
        pass

    def setSimstate(self, simstate):
        pass

    def resetSimstate(self):
        pass

    def emitETA(self, controller):
        pass


class Emitter(object):
    def __init__(self, uuid, script):
        self.request = Request(uuid, script)
        self.messages = []
        self.errored = False
        self.result = None
        self._controller = None

    def current_script(self):
        return self.request

    def emit_event(self, evtype, msg):
        if evtype == 'simmessage':
            if msg[2] >= ERROR:
                self.errored = True
                session.log.info('%s', msg[4])
            record = LogRecord(msg[0], msg[2], msg[5], 0, msg[3].rstrip(),
                               (), None)
            session.testhandler.emit(record)
            self.messages.append(msg)
        elif evtype == 'simresult':
            assert msg[2] == self.request.reqid
            self.result = msg


custom_dir = path.join(module_root, 'nicos_mlz')
custom_subdirs = {}


def find_scripts():
    for instr in sorted(os.listdir(custom_dir)):
        testdir = path.join(custom_dir, instr, 'testscripts')
        nicosconf = path.join(custom_dir, instr, 'nicos.conf')
        if not path.isdir(testdir):
            continue
        custom_subdirs[instr] = []
        cp = configparser.ConfigParser()
        cp.read(nicosconf)
        if cp.has_option('nicos', 'setup_subdirs'):
            sbd = cp.get('nicos', 'setup_subdirs').split(',')
            custom_subdirs[instr] = sbd
        for testscript in sorted(os.listdir(testdir)):
            # For now, only the "basic" scripts are run.
            if testscript.endswith('basic.py'):
                yield pytest.param(instr, testscript,
                                   id="{}-{}".format(instr, testscript))


@pytest.mark.parametrize('instr, script', find_scripts())
def test_dryrun(session, instr, script):

    setups = ['system']
    setupcode = []
    code = []
    needs_modules = []
    timing_condition = None
    subdirs = custom_subdirs[instr]
    fullpath = path.join(custom_dir, instr, 'testscripts', script)
    cachepath = path.join(custom_dir, instr, 'testscripts', 'cache')

    with open(fullpath) as fp:
        for line in fp:
            if line.startswith('# test:'):
                parts = line.split(None, 4)
                if len(parts) < 4:  # -> # test: name = value...
                    continue
                if parts[2] == 'subdirs':
                    subdirs.extend(v.strip() for v in parts[4].split(','))
                elif parts[2] == 'setups':
                    setups.extend(v.strip() for v in parts[4].split(','))
                elif parts[2] == 'setupcode':
                    setupcode.insert(0, parts[4] + '\n')
                elif parts[2] == 'needs':
                    needs_modules.append(parts[4].strip())
                elif parts[2] == 'timing':
                    timing_condition = parts[4].strip()
                else:
                    assert False, 'invalid test directive in file: %r' % line
            code.append(line)
    code[0:0] = setupcode
    code = ''.join(code)

    for modname in needs_modules:
        try:
            __import__(modname)
        except Exception:
            pytest.skip('required module %r is not available' % modname)

    setup_subdirs = ','.join(path.join(custom_dir, sbd) for sbd in subdirs)
    uuid = uuid1()
    emitter = Emitter(uuid, code)
    supervisor = SimulationSupervisor(None, str(uuid), code, setups,
                                      system_user, emitter,
                                      [setup_subdirs, cachepath], quiet=False)
    supervisor.start()
    supervisor.join()
    assert emitter.result is not None
    assert not emitter.errored
    if timing_condition:
        time_estimation, _devices, _script = emitter.result
        assert eval('x ' + timing_condition, {'x': time_estimation})
