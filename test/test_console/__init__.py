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

import sys

from test.utils import TestSession, cleanup, startCache, startSubprocess, \
    killSubprocess
from nicos import session

cache = None
console = None


def setup_package():
    global cache, console  # pylint: disable=W0603
    sys.stderr.write('\nSetting up console test, cleaning old test dir...\n')
    session.__class__ = TestSession
    session.__init__('testconsole')
    cleanup()
    cache = startCache()
    console = startSubprocess('aio.py', piped=True)


def teardown_package():
    killSubprocess(console)
    session.shutdown()
    killSubprocess(cache)
