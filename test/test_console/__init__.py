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
import signal
import subprocess
from os import path
from time import sleep

from test.utils import TestSession, cleanup, rootdir, startCache, killCache, \
    adjustPYTHONPATH
from nicos import session

cache = None
console = None


def setup_package():
    global cache, console  # pylint: disable=W0603
    sys.stderr.write('\nSetting up console test, cleaning old test dir...')
    session.__class__ = TestSession
    session.__init__('testconsole')
    cleanup()
    cache = startCache()
    sys.stderr.write('\n')
    adjustPYTHONPATH()

    console = subprocess.Popen([sys.executable,
                                path.join(rootdir, '..', 'aio.py')],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stderr.write(' [console start... %s ok]\n' % console.pid)


def teardown_package():
    sys.stderr.write('\n [console kill %s...' % console.pid)
    if console.poll():  # usually should have exited already during the test
        os.kill(console.pid, signal.SIGTERM)
        if os.name == 'posix':
            os.waitpid(console.pid, 0)
    sys.stderr.write(' ok]\n')
    session.shutdown()
    killCache(cache)
