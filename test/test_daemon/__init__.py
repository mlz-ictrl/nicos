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

from __future__ import print_function

import os
import sys
import time
import signal
import socket
import subprocess
from os import path

from test.utils import TestSession, cleanup, rootdir, startCache, killCache, \
     adjustPYTHONPATH
from nicos.protocols.daemon import ENQ, LENGTH, serialize, command2code
from nicos import session
from nicos.utils import tcpSocket

cache = None
daemon = None


def setup_package():
    global cache, daemon  # pylint: disable=W0603
    print('\nSetting up daemon test, cleaning old test dir...', file=sys.stderr)
    session.__class__ = TestSession
    session.__init__('testdaemon')
    cleanup()
    cache = startCache()
    adjustPYTHONPATH()

    daemon = subprocess.Popen([sys.executable,
                               path.join(rootdir, '..', 'daemon.py')])
    start = time.time()
    wait = 5
    while time.time() < start + wait:
        try:
            s = tcpSocket('localhost', 14874)
        except socket.error:
            time.sleep(0.02)
        else:
            auth = serialize(({'login': 'guest', 'passwd': '', 'display': ''},))
            s.send((b'\x42' * 16) +  # ident
                   ENQ + command2code['authenticate'] +
                   LENGTH.pack(len(auth)) + auth)
            empty = serialize(())
            s.send(ENQ + command2code['quit'] + LENGTH.pack(len(empty)) + empty)
            time.sleep(0.02)
            s.close()
            break
    else:
        raise Exception('daemon failed to start within %s sec' % wait)
    sys.stderr.write(' [daemon start... %s] ' % daemon.pid)


def teardown_package():
    sys.stderr.write(' [daemon kill %s...' % daemon.pid)
    os.kill(daemon.pid, signal.SIGTERM)
    if os.name == 'posix':
        os.waitpid(daemon.pid, 0)
    sys.stderr.write(' done] ')
    session.shutdown()
    killCache(cache)
