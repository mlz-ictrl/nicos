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

import logging

from nicos import nicos_version
from nicos.core.constants import LIVE


def load_setup(client, setup):
    client.run_and_wait("NewSetup('%s')" % setup)


def test_version(client):
    # getversion
    assert client.ask('getversion') == nicos_version


def test_encoding(client):
    load_setup(client, 'daemontest')
    client.run_and_wait("""\
# Kommentar: Meßzeit 1000s, d = 5 Å
Remark("Meßzeit 1000s, d = 5 Å")
scan(dax, 0, 0.1, 1, det, "Meßzeit 1000s, d = 5 Å", ctr1=1)
""", 'Meßzeit.py')


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
    client._signals = []
    client.tell('exec', 'help("nicos_demo")')
    for name, data, _exc in client.iter_signals(0, timeout=10.0):
        if name == 'showhelp':
            assert data[0] == 'nicos_demo'
            assert 'This entry examples' in data[1]
            break
    client._signals = []
    client.tell('exec', 'help("topic:nicos_demo")')
    for name, data, _exc in client.iter_signals(0, timeout=10.0):
        if name == 'showhelp':
            assert data[0] == 'topic:nicos_demo'
            assert 'This entry examples' in data[1]
            break
    client._signals = []
    client.tell('exec', 'help("RST")')
    for name, data, _exc in client.iter_signals(0, timeout=10.0):
        if name == 'showhelp':
            assert data[0] == 'RST'
            assert '<li>List entry <strong>1</strong>.</li>' in data[1]
            break


def test_userinput(client):
    load_setup(client, 'daemontest')
    idx = len(client._signals)
    client.run('userval = userinput("gimme", float)')
    for name, data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'prompt':
            uid = data[1]
            assert data[0] == 'gimme'
            assert data[2] is float
            idx = len(client._signals)
            client.eval(f'session.setUserinput({uid!r}, 42)')
            client.tell('continue')
            break
    for name, data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'promptdone':
            assert data[0] == uid
            assert client.eval('userval == 42.0')
            break


def test_simulation(client):
    load_setup(client, 'daemontest')
    idx = len(client._signals)
    client.tell('simulate', '', 'read()', 'sim')
    for name, _data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'simresult':
            return


def test_dualaccess(client, adminclient):
    load_setup(client, 'daemontest')
    adminclient.run('fix(dm2, "test")', 'adminfix')
    client.wait_idle()
    assert 'fixed by ' in client.eval('dm2.fixed')
    client.run('release(dm2)')
    assert 'fixed by ' in client.eval('dm2.fixed')
    client.run('count(10)')
    adminclient.tell('exec', 'release(dm2)')
    client.wait_idle()
    assert 'fixed by' not in client.eval('dm2.fixed')


def test_get_device_list(client):
    load_setup(client, 'daemontest')
    full = client.eval('[(dn, str(d.classes)) '
                       'for (dn, d) in session.devices.items()]')
    assert full

    l1 = client.getDeviceList()
    l2 = client.getDeviceList('nicos.core.device.Moveable')
    # expected:
    # l1: ['dax', 'dm1', 'dm2', 'Exp', 'Instr', 'Sample', 'testnotifier']
    # l2: ['dax', 'dm1', 'dm2', 'Sample']
    assert 'Exp' in l1
    assert l1 != l2
    assert all(item in l1 for item in l2)
    assert 'Exp' not in l2
    assert 'Instr' not in l2
    assert 'testnotifier' not in l2


def test_live_events(client):
    idx = len(client._signals)
    client.run_and_wait("""\
import numpy
from nicos import session
from nicos.core.constants import LIVE
from nicos.utils import byteBuffer
arr = numpy.array([[1, 2], [3, 4]], dtype='<u1')
session.updateLiveData(dict(
    tag=LIVE,
    uid='uid',
    det='detname',
    time=12345,
    datadescs=[dict(
        dtypes='<u1',
        shapes=(2, 2, 1),
        count=1)]),
    [byteBuffer(arr)])
""", 'live.py')
    for name, data, blobs in client.iter_signals(idx, timeout=10.0):
        if name == 'livedata':
            assert data == dict(uid='uid',
                                tag=LIVE,
                                det='detname',
                                time=12345,
                                datadescs=[dict(
                                    dtypes='<u1',
                                    shapes=[2, 2, 1],
                                    count=1)])

            assert [b.tobytes() for b in blobs] == [b'\x01\x02\x03\x04']
            return


def test_abort(client):
    # load_setup(client, 'daemontest')
    idx = len(client._signals)
    client.run_and_wait('abort(); sleep(600)', allow_exc=True)
    for name, data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'message':
            if 'Script stopped by abort()' in data[3]:
                return


def test_run(client):
    idx = len(client._signals)
    script, filename = 'print(42)', 'file.py'
    client.run_and_wait(script, filename)
    reqid = None
    for name, data, _exc in client.iter_signals(idx, timeout=10.0):
        if name == 'request':
            reqid = data['reqid']
            assert data['script'] == script
            assert data['name'] == filename
            assert data['user'] == 'user'
        elif name == 'processing':
            assert data['reqid'] == reqid
        elif name == 'message':
            if data[2] == logging.INFO:
                assert data[3].strip() == '42'
        elif name == 'done':
            assert data['reqid'] == reqid
            assert data['success'] is True
            break


def test_parameter_queries(client):
    load_setup(client, 'daemontest')
    pinfo = client.getDeviceParamInfo('dmalias')
    assert sorted(list(pinfo.keys())) == sorted([
        'name', 'classes', 'description', 'visibility', 'loglevel', 'fmtstr',
        'unit', 'maxage', 'pollinterval', 'warnlimits', 'target', 'fixed',
        'fixedby', 'requires', 'precision', 'userlimits', 'abslimits', 'alias',
        'speed', 'offset', 'jitter', 'curvalue', 'curstatus', 'ramp',
        'devclass', 'ignore_general_stop'])
    params = client.getDeviceParams('dm1')
    # parameters 'status' and 'value' not in all test cases available
    # their occurances depends on the previous test history
    assert set(params.keys()).issubset({
        'abslimits', 'classes', 'curstatus', 'curvalue', 'description', 'fixed',
        'fixedby', 'fmtstr', 'jitter', 'loglevel', 'maxage', 'name', 'offset',
        'pollinterval', 'precision', 'ramp', 'requires', 'speed', 'target',
        'unit', 'userlimits', 'visibility', 'warnlimits', 'status', 'value',
        'ignore_general_stop'})
    assert client.getDeviceParam('dm1', 'name') == 'dm1'
    assert client.getDeviceParam('dm1', 'noparam') is None


def test_devices_values(client):
    load_setup(client, 'daemontest')
    assert client.getDeviceValuetype('dm1') == float
    assert client.getDeviceValue('dm1') == 0.
