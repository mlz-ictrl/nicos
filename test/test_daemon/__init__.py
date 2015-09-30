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

import sys
import time
import socket

from test.utils import TestSession, cleanup, startCache, startSubprocess, \
    killSubprocess, getDaemonPort
from nicos.protocols.daemon import ENQ, LENGTH, serialize, command2code
from nicos import session
from nicos.utils import tcpSocket

cache = None
daemon = None


def setup_package():
    global cache, daemon  # pylint: disable=W0603

    def daemon_wait_cb():
        start = time.time()
        wait = 5
        while time.time() < start + wait:
            try:
                s = tcpSocket('localhost', getDaemonPort())
            except socket.error:
                time.sleep(0.02)
            else:
                auth = serialize(({'login': 'guest', 'passwd': '', 'display': ''},))
                s.send((b'\x42' * 16) +  # ident
                       ENQ + command2code['authenticate'] +
                       LENGTH.pack(len(auth)) + auth)
                s.recv(1024)
                empty = serialize(())
                s.send(ENQ + command2code['quit'] + LENGTH.pack(len(empty)) + empty)
                s.recv(1024)
                s.close()
                break
        else:
            raise Exception('daemon failed to start within %s sec' % wait)
    sys.stderr.write('\nSetting up daemon test, cleaning old test dir...\n')
    session.__class__ = TestSession
    session.__init__('testdaemon')
    cleanup()
    cache = startCache()
    daemon = startSubprocess('daemon.py', wait_cb=daemon_wait_cb)


def teardown_package():
    killSubprocess(daemon)
    session.shutdown()
    killSubprocess(cache)
