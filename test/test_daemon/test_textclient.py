#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

# Test the text client.

import os
import sys
import signal
import subprocess
from os import path

import nose

from nicos.pycompat import from_utf8

from test.utils import rootdir, getDaemonPort

if os.name != 'posix':
    # text client needs the readline C library
    raise nose.SkipTest('text client not available on this system')

client = None


def setup_module():
    global client
    os.environ['EDITOR'] = 'cat'
    client = subprocess.Popen([sys.executable,
                               path.join(rootdir, '..', 'cliclient.py'),
                               'guest:guest@localhost:%s' % getDaemonPort()],
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stderr.write(' [client start... %s ok]\n' % client.pid)


def teardown_module():
    sys.stderr.write('\n [client kill %s...' % client.pid)
    if client.poll() is None:  # usually should have exited already during the test
        os.kill(client.pid, signal.SIGTERM)
        if os.name == 'posix':
            os.waitpid(client.pid, 0)
    sys.stderr.write(' ok]\n')


def test_textclient():
    stdout, _ = client.communicate(b'''\
/log 100
/help
/edit test.py
/sim read
NewSetup
/wait
read
/wait
help read
/wait
set t_alpha speed 1
/wait
maw t_alpha 100
/wait 0.1
maw t_alpha 200
Q
/wait 0.1
/pending
/where
/cancel *
/trace
/spy
t_alpha()
/spy
/stop
S
/wait
/disconnect
/quit
''')
    res = from_utf8(stdout)
    assert 'Simulated minimum runtime' in res
    assert 'Current stacktrace' in res
    assert 'Showing pending scripts' in res
    assert 'Printing current script' in res
    assert 'Spy mode on' in res
    assert 'Spy mode off' in res
    assert 'Your choice?' in res
    assert 'Disconnected from server' in res

    print(res)
