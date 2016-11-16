#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

from __future__ import print_function

import time

from functools import partial
from test.utils import getDaemonPort, raises
from nose.tools import with_setup

from nicos import nicos_version
from nicos.clients.base import NicosClient, ConnectionData
from nicos.protocols.daemon import STATUS_IDLE, STATUS_IDLEEXC
from nicos.core.sessions.utils import MASTER


class TestClient(NicosClient):
    def __init__(self):
        self._signals = []
        self._estatus = STATUS_IDLE
        self._disconnecting = False
        NicosClient.__init__(self, print)

    def signal(self, name, data=None, exc=None):  # pylint: disable=W0221
        if name == 'error':
            raise AssertionError('client error: %s (%s)' % (data, exc))
        if name == 'disconnected' and not self._disconnecting:
            raise AssertionError('client disconnected')
        if name == 'status':
            self._estatus = data[0]
        self._signals.append((name, data, exc))

    def iter_signals(self, startindex, timeout):
        starttime = time.time()
        while True:
            endindex = len(self._signals)
            for sig in self._signals[startindex:endindex]:
                yield sig
            startindex = endindex
            time.sleep(0.05)
            if time.time() > starttime + timeout:
                raise AssertionError('timeout in iter_signals')

    def wait_idle(self):
        while True:
            time.sleep(0.05)
            st = client.ask('getstatus')
            if st['status'][0] in (STATUS_IDLE, STATUS_IDLEEXC):
                break

    def run_and_wait(self, command, name=None, allow_exc=False):
        idx = len(self._signals)
        reqno = self.run(command, name)
        # wait for idle status
        processing = False
        for sig in self.iter_signals(idx, 5.0):
            if sig[0] == 'processing' and sig[1]['reqno'] == reqno:
                processing = True
            if processing and sig[0] == 'status' and \
               sig[1][0] in (STATUS_IDLE, STATUS_IDLEEXC):
                if sig[1][0] == STATUS_IDLEEXC and not allow_exc:
                    raise AssertionError('script failed with exception')
                break


client = None


def setup_module():
    # pylint: disable=global-statement
    global client
    client = TestClient()
    client.connect(ConnectionData('localhost', getDaemonPort(), 'user', 'user'))
    assert ('connected', None, None) in client._signals

    # wait until initial setup is done
    client.wait_idle()


def teardown_module():
    if client.connected:
        client._disconnecting = True
        client.disconnect()


def start_simple_mode():
    client.run_and_wait('SetSimpleMode(True)')


def finish_simple_mode():
    if client.connected:
        try:
            client.run_and_wait('SetSimpleMode False')
        except Exception:
            pass


def loading_setup(setup):
    client.run_and_wait("NewSetup('%s')" % setup)


def test_version():
    # getversion
    assert client.ask('getversion') == nicos_version


def test_startup_setup():
    # eval
    setups = client.eval('session.explicit_setups')
    assert setups == ['startup']


@with_setup(start_simple_mode, finish_simple_mode)
def test_simple():
    client.run_and_wait('NewSetup daemonmain')

    # getstatus
    status = client.ask('getstatus')
    assert status['status'] == (STATUS_IDLE, -1)      # execution status
    assert status['script'] == 'NewSetup daemonmain'  # current script
    assert status['mode'] == MASTER                   # current mode
    assert status['watch'] == {}                      # no watch expressions
    assert status['setups'][1] == ['daemonmain']      # explicit setups
    assert status['requests'] == []                   # no requests queued

    # queue/unqueue/emergency
    client.run('sleep 0.1')
    client.run('printinfo 2')
    status = client.ask('getstatus')
    assert status['requests'][-1]['script'] == 'printinfo 2'
    assert status['requests'][-1]['user'] == 'user'
    client.tell('unqueue', str(status['requests'][-1]['reqno']))

    # test view-only mode
    client.viewonly = True
    try:
        assert raises(AssertionError, client.tell, 'exec', 'sleep')
    finally:
        client.viewonly = False

    # wait until command is done
    client.wait_idle()


@with_setup(partial(loading_setup, 'daemonmain'))
def test_encoding():
    client.run_and_wait('''\
# Kommentar: Meßzeit 1000s, d = 5 Å
Remark("Meßzeit 1000s, d = 5 Å")
scan(t_psi, 0, 0.1, 1, det, "Meßzeit 1000s, d = 5 Å")
''', 'Meßzeit.py')


@with_setup(partial(loading_setup, 'daemonmain'))
def test_htmlhelp():
    # NOTE: everything run with 'queue' will not show up in the coverage
    # report, since the _pyctl trace function replaces the trace function from
    # coverage, so if we want HTML help generation to get into the report we
    # use 'exec'
    client._signals = []
    client.tell('exec', 'help()')
    for name, data, _exc in client.iter_signals(0, timeout=5.0):
        if name == 'showhelp':
            # default help page is the index page
            assert data[0] == 'index'
            assert data[1].startswith('<html>')
            break
    client._signals = []
    client.tell('exec', 'help(t_phi)')
    for name, data, _exc in client.iter_signals(0, timeout=5.0):
        if name == 'showhelp' and data[0] == 'dev:t_phi':
            # default help page is the index page
            assert data[1].startswith('<html>')
            break


@with_setup(partial(loading_setup, 'daemonmain'))
def test_simulation():
    idx = len(client._signals)
    client.tell('simulate', '', 'read()', 'sim')
    for name, _data, _exc in client.iter_signals(idx, timeout=5.0):
        if name == 'simresult':
            return
