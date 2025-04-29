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

"""NICOS custom lib tests: dry-run instrument test scripts with the real
instrument setups.
"""

from logging import ERROR, LogRecord
from pathlib import Path
from uuid import uuid1

import pytest

from nicos.configmod import readToml
from nicos.core.sessions.simulation import SimulationSupervisor
from nicos.core.utils import system_user

from test.utils import module_root

session_setup = None


class Request:

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


class Emitter:
    def __init__(self, uuid, script):
        self.request = Request(uuid, script)
        self.messages = []
        self.error_record = None
        self.result = None
        self._controller = None

    def current_script(self):
        return self.request

    def emit_event(self, evtype, msg):
        if evtype == 'simmessage':
            record = LogRecord(msg[0], msg[2], msg[5], 0, msg[3].rstrip(),
                               (), None)
            if msg[2] >= ERROR and not self.error_record:
                self.error_record = record
            self.messages.append(msg)
        elif evtype == 'simresult':
            assert msg[2] == self.request.reqid
            self.result = msg


custom_subdirs = {}


def find_scripts():
    for custom_dir in [d for d in Path(module_root).glob('nicos_*')
                       if d.is_dir() and d.name != 'nicos_demo']:
        facility = custom_dir.name
        for testdir in Path(custom_dir).rglob('testscripts'):
            if not testdir.is_dir():
                continue
            nicosconf = testdir.parent.joinpath('nicos.conf')
            idx = testdir.parts.index(facility) + 1
            instr = '.'.join(testdir.parts[idx:-1])
            full_instr = f'{facility}.{instr}'
            custom_subdirs[full_instr] = []
            cfg = readToml(nicosconf)
            subdirs = cfg.get('nicos', {}).get('setup_subdirs')
            if subdirs is not None:
                custom_subdirs[full_instr] = subdirs
            for testscript in sorted(testdir.iterdir()):
                # For now, only the "basic" scripts are run.
                if testscript.suffix == '.py':
                    yield pytest.param(
                        facility, instr, testscript,
                        id=f'{facility}-{instr}-{testscript.stem}')


@pytest.mark.parametrize('facility, instr, script', find_scripts())
def test_dryrun(session, facility, instr, script):

    setups = ['system']
    setupcode = []
    code = []
    needs_modules = []
    timing_condition = None
    subdirs = custom_subdirs[f'{facility}.{instr}']
    custom_dir = Path(module_root).joinpath(facility)
    fullpath = custom_dir.joinpath(*instr.split('.'), 'testscripts', script)
    cachepath = custom_dir.joinpath(*instr.split('.'), 'testscripts', 'cache')

    with fullpath.open(encoding='utf-8') as fp:
        for line in fp:
            if line.startswith('# test:'):
                parts = line.split(None, 4)
                if len(parts) < 4:  # -> # test: name = value...
                    if parts[2] == 'skip':
                        pytest.skip('test should be skipped')
                    continue
                if parts[2] == 'subdirs':
                    subdirs.extend(v.strip() for v in parts[4].split(','))
                elif parts[2] == 'setups':
                    setups.extend(v.strip() for v in parts[4].split(','))
                elif parts[2] == 'setupcode':
                    setupcode.append(parts[4] + '\n')
                elif parts[2] == 'needs':
                    needs_modules.extend(v.strip() for v in parts[4].split(','))
                elif parts[2] == 'timing':
                    timing_condition = parts[4].strip()
                else:
                    pytest.fail('invalid test directive in file: %r' % line)
            code.append(line)
    code[0:0] = setupcode
    code = ''.join(code)

    for modname in needs_modules:
        try:
            if modname.find('>=') > 0:
                modname, minversion = modname.split('>=')
                pytest.importorskip(modname, minversion=minversion)
            else:
                __import__(modname)
        except Exception:
            pytest.skip('required module %r is not available' % modname)

    setup_subdirs = ','.join('%s' % Path(custom_dir).joinpath(sbd)
                             for sbd in subdirs)
    uuid = uuid1()
    emitter = Emitter(uuid, code)
    supervisor = SimulationSupervisor(None, str(uuid), code, setups,
                                      system_user, emitter,
                                      [setup_subdirs, cachepath], quiet=False)
    supervisor.start()
    supervisor.join()
    if emitter.error_record:
        session.log.handle(emitter.error_record)
        # for safety, but logging the ERROR should have failed already
        pytest.fail(f'error during dry run: {emitter.error_record}')
    if timing_condition:
        time_estimation, _devices, _script = emitter.result
        assert eval('x ' + timing_condition, {'x': time_estimation})
