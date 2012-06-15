#!/usr/bin/env python
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

import os
import sys
import shutil
import signal
import subprocess
from os import path
rootdir = path.join(os.path.dirname(__file__), '..', 'root')
cache = None

def cleanup(rootdir):
    if path.exists(rootdir):
        print 'Cleaning old test output dir...'
        print '-' * 70
        shutil.rmtree(rootdir)
    os.mkdir(rootdir)
    os.mkdir(rootdir + '/cache')
    os.mkdir(rootdir + '/pid')

def startCache():
    global cache #pylint: disable=W0603
    print 'Starting test cache server...'

    # start the cache server
    os.environ['PYTHONPATH'] = path.join(rootdir, '..', '..', 'lib')
    cache = subprocess.Popen([sys.executable, path.join(rootdir, '..', 'cache.py')])

    print 'Cache PID = %s' % cache.pid
    print '-' * 70


def setupPackage():
    cleanup(rootdir)
    startCache()
    print 'Running NICOS test suite...'
    print '-' * 70


def teardownPackage():
    # kill the cache server
    print '-' * 70
    print 'Killing cache server...' , cache.pid
    cache.terminate()
    cache.wait()
    print '-' * 70
