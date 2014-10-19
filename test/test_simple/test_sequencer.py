#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""NICOS sequence class test suite."""

import time

from nicos import session
from nicos.core import LimitError
from nicos.devices.generic.sequence import SeqDev, SeqParam, SeqMethod, \
    SeqCall, SeqSleep, SeqNOP

from test.utils import raises

methods_called = set()


def setup_module():
    session.loadSetup('sequencer')
    methods_called.clear()


def teardown_module():
    session.unloadSetup()


def test_lockeddevice():
    ld = session.getDevice('ld')
    sm1 = session.getDevice('sm1')
    ld.move(3)
    ld.wait()
    assert sm1.read(0) == 3


def test_sequence_items():
    # Check SeqenceItems by instantiating and checking
    sm1 = session.getDevice('sm1')
    sm2 = session.getDevice('sm2')

    # parameter checking
    assert raises(TypeError, SeqDev)
    assert raises(TypeError, SeqParam)
    assert raises(TypeError, SeqMethod)
    assert raises(TypeError, SeqCall)
    assert raises(TypeError, SeqSleep)
    SeqNOP()

    # Device move
    sd = SeqDev(sm1, 3)
    assert repr(sd) == 'maw(sm1, 3)'
    sm1.start(0)
    sm1.wait()
    assert sm1.read(0) == 0

    sd.check()
    sd.run()
    while not sd.wait():
        pass
    assert sm1.read(0) == 3

    # Param setting
    sp = SeqParam(sm2, 'speed', 1)
    assert 'sm2.speed' in repr(sp)
    assert '=' in repr(sp)
    assert repr(sp).endswith('1')

    sm2.speed = 5
    assert sm2.speed == 5
    sp.check()
    sp.run()
    while not sp.wait():
        pass
    assert sm2.speed == 1

    # method calling, use fix/relase here
    sm = SeqMethod(sm1, 'fix', 'blubb')
    assert repr(sm) == "sm1.fix('blubb')"

    assert sm1.fixed == ''

    sm.check()
    sm.run()
    while not sm.wait():
        pass
    assert 'blubb' in sm1.fixed

    sm1.release()

    # Sleeping??
    sw = SeqSleep(1)
    assert repr(sw).startswith('wait')
    a = time.time()
    sw.check()
    sw.run()
    while not sw.wait():
        pass
    b = time.time()

    assert 0.9 <= b - a <= 1.1

    # Calling
    sc = SeqCall(time.sleep, 0.1)
    assert repr(sc).startswith('sleep(0.1')
    a = time.time()
    sc.check()
    sc.run()
    assert sc.wait() is True
    b = time.time()
    assert 0.09 <= b - a <= 0.13

    # NOP
    sn = SeqNOP()
    sn.check()
    sn.run()
    assert True == sn.wait()
    sn.stop()
    sn.retry(5)


def test_locked_multiswitcher():
    # Guard against regression of #1315
    lms = session.getDevice('ld2')
    assert raises(LimitError, lms.move, 0)
