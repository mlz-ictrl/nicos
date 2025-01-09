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

from time import monotonic, sleep

import pytest

from nicos.clients.base import ConnectionData, NicosClient
from nicos.protocols.daemon import STATUS_IDLE, STATUS_IDLEEXC
from nicos.utils import parseConnectionString

from test.utils import daemon_addr


class ClientTestMixin:
    def __init__(self):
        self._signals = []
        self._estatus = STATUS_IDLE
        self._disconnecting = False

    def signal(self, name, data=None, data2=None):  # pylint: disable=W0221
        if name == 'error':
            raise AssertionError('client error: %s (%s)' % (data, data2))
        if name == 'disconnected' and not self._disconnecting:
            raise AssertionError('client disconnected')
        if name == 'status':
            self._estatus = data[0]
        self._signals.append((name, data, data2))

    def iter_signals(self, startindex, timeout):
        starttime = monotonic()
        while True:
            endindex = len(self._signals)
            yield from self._signals[startindex:endindex]
            startindex = endindex
            sleep(0.05)
            if monotonic() > starttime + timeout:
                raise AssertionError('timeout in iter_signals')

    def wait_idle(self):
        while True:
            sleep(0.05)
            st = self.ask('getstatus')
            if st['status'][0] in (STATUS_IDLE, STATUS_IDLEEXC):
                break

    def run_and_wait(self, command, name=None, allow_exc=False):
        idx = len(self._signals)
        reqid = self.run(command, name)
        # wait for idle status
        processing = False
        for sig in self.iter_signals(idx, 5.0):
            if sig[0] == 'processing' and sig[1]['reqid'] == reqid:
                processing = True
            if processing and sig[0] == 'status' and \
               sig[1][0] in (STATUS_IDLE, STATUS_IDLEEXC):
                if sig[1][0] == STATUS_IDLEEXC and not allow_exc:
                    raise AssertionError('script failed with exception')
                break


class TestClient(ClientTestMixin, NicosClient):
    def __init__(self):
        ClientTestMixin.__init__(self)
        NicosClient.__init__(self, print)


def client_with_class(client_class, auth):
    """Create a nicos client session and log in"""
    client = client_class()
    parsed = parseConnectionString(f'{auth}@{daemon_addr}', 0)
    client.connect(ConnectionData(**parsed))
    assert ('connected', None, None) in client._signals

    # wait until initial setup is done
    client.wait_idle()

    yield client

    if client.isconnected:
        client._disconnecting = True
        client.disconnect()


@pytest.fixture(scope='function')
def client(daemon):
    yield from client_with_class(TestClient, 'user:user')


@pytest.fixture(scope='function')
def adminclient(daemon):
    yield from client_with_class(TestClient, 'admin:admin')
