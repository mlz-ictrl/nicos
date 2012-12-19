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

import time

from nicos import nicos_version
from nicos.clients.base import NicosClient
from nicos.protocols.daemon import STATUS_IDLE

from test.utils import raises


class TestClient(NicosClient):
    def __init__(self):
        self._signals = []
        self._estatus = STATUS_IDLE
        self._disconnecting = False
        NicosClient.__init__(self)

    def signal(self, name, data=None, exc=None):
        if name == 'error':
            raise AssertionError('client error: %s (%s)' % (data, exc))
        if name == 'disconnected' and not self._disconnecting:
            raise AssertionError('client disconnected')
        if name == 'status':
            self._estatus = data[0]
        self._signals.append((name, data, exc))

client = None

def setup_module():
    global client
    client = TestClient()
    client.connect({'host': 'localhost',
                    'port': 14874,
                    'login': 'user',
                    'passwd': 'user',
                    'display': ''})
    assert ('connected', None, None) in client._signals

def teardown_module():
    if client.connected:
        client._disconnecting = True
        client.disconnect()

def test_simple():
    # getversion
    assert client.ask('getversion') == nicos_version

    # wait until initial setup is done
    while True:
        time.sleep(0.05)
        st = client.ask('getstatus')
        if st[0][0] == STATUS_IDLE:
            break

    # eval/exec
    if client.eval('session._spmode'):
        client.tell('exec', 'SetSimpleMode false')
    client.tell('exec', 'SetSimpleMode(True)')
    client.tell('exec', 'NewSetup daemonmain')

    # queue
    client.tell('queue', '', 'printinfo 1')
    time.sleep(0.05)

    # getstatus
    status = client.ask('getstatus')
    assert status[0] == (STATUS_IDLE, -1)   # execution status
    assert status[1] == 'printinfo 1'       # current script
    assert status[2] == 'master'            # current mode
    assert status[3] == {}                  # no watch expressions
    assert status[4] == ['daemonmain']      # explicit setups
    assert status[5] == []                  # no requests queued

    # queue/unqueue/emergency
    client.tell('queue', '', 'sleep 0.1')
    client.tell('queue', '', 'printinfo 2')
    status = client.ask('getstatus')
    assert status[5][-1]['script'] == 'printinfo 2'
    assert status[5][-1]['user'] == 'user'
    client.tell('unqueue', str(status[5][-1]['reqno']))

    # wait until command is done
    while True:
        time.sleep(0.05)
        if client._estatus == STATUS_IDLE:
            break
