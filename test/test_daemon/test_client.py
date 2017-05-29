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

import pytest

from nicos import nicos_version
from nicos.core import MASTER
from nicos.protocols.daemon import STATUS_IDLE

from test.utils import raises


@pytest.yield_fixture
def simple_mode(client):
    """Run nicos session in SimpleMode"""

    client.run_and_wait('SetSimpleMode(True)')
    yield
    if client.connected:
        try:
            client.run_and_wait('SetSimpleMode False')
        except Exception:
            pass


def load_setup(client, setup):
    client.run_and_wait("NewSetup('%s')" % setup)


def test_version(client):
    # getversion
    assert client.ask('getversion') == nicos_version


def test_simple(client, simple_mode):
    client.run_and_wait('NewSetup stdsystem')

    # getstatus
    status = client.ask('getstatus')
    assert status['status'] == (STATUS_IDLE, -1)      # execution status
    assert status['script'] == 'NewSetup stdsystem'   # current script
    assert status['mode'] == MASTER                   # current mode
    assert status['watch'] == {}                      # no watch expressions
    assert status['setups'][1] == ['stdsystem']       # explicit setups
    assert status['requests'] == []                   # no requests queued

    # queue/unqueue/emergency
    client.run('sleep 0.1')
    client.run('printinfo 2')
    status = client.ask('getstatus')
    assert status['requests'][-1]['script'] == 'printinfo 2'
    assert status['requests'][-1]['user'] == 'user'
    client.tell('unqueue', str(status['requests'][-1]['reqid']))

    # test view-only mode
    client.viewonly = True
    try:
        assert raises(AssertionError, client.tell, 'exec', 'sleep')
    finally:
        client.viewonly = False

    # wait until command is done
    client.wait_idle()


def test_encoding(client):
    load_setup(client, 'scanning')
    client.run_and_wait('''\
# Kommentar: Meßzeit 1000s, d = 5 Å
Remark("Meßzeit 1000s, d = 5 Å")
scan(dax, 0, 0.1, 1, det, "Meßzeit 1000s, d = 5 Å", ctr1=1)
''', 'Meßzeit.py')


def test_htmlhelp(client):
    load_setup(client, 'daemontest')
    # NOTE: everything run with 'queue' will not show up in the coverage
    # report, since the _pyctl trace function replaces the trace function from
    # coverage, so if we want HTML help generation to get into the report we
    # use 'exec'
    client._signals = []
    client.tell('exec', 'help()')
    for name, data, _exc in client.iter_signals(0, timeout=10.0):
        if name == 'showhelp':
            # default help page is the index page
            assert data[0] == 'index'
            assert data[1].startswith('<html>')
            break
    client._signals = []
    client.tell('exec', 'help(dax)')
    for name, data, _exc in client.iter_signals(0, timeout=10.0):
        if name == 'showhelp' and data[0] == 'dev:dax':
            # default help page is the index page
            assert data[1].startswith('<html>')
            break


def test_simulation(client):
    load_setup(client, 'daemontest')
    idx = len(client._signals)
    client.tell('simulate', '', 'read()', 'sim')
    for name, _data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'simresult':
            return
