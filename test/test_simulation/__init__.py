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

"""Tests for simulation mode."""

from __future__ import print_function

import sys

from nicos import session
from nicos.commands.scan import scan
from nicos.commands.basic import sleep
from nicos.core.sessions.utils import SIMULATION

from test.utils import cleanup, TestSession, startCache, killSubprocess

cache = None


def setup_package():
    global cache  # pylint: disable=W0603
    sys.stderr.write('\nSetting up simulation test, cleaning old test dir...\n')
    cleanup()
    # While the simulation doesn't use a cache, we start it to verify that
    # it isn't used.
    cache = startCache()
    session.__class__ = TestSession
    session.__init__('test_simulation')
    session.loadSetup('simscan')
    session.setMode(SIMULATION)


def teardown_package():
    session.shutdown()
    killSubprocess(cache)


def test_simmode():
    m = session.getDevice('motor')
    det = session.getDevice('det')
    scan(m, 0, 1, 5, 0., det, 'test scan')
    assert m._sim_min == 0
    assert m._sim_max == 4
    assert m._sim_value == 4


def test_special_behavior():
    oldtime = session.clock.time
    sleep(1000)   # should take no time in simulation mode, but advance clock
    newtime = session.clock .time
    assert newtime - oldtime == 1000
