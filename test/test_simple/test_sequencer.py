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

"""NICOS sequence class test suite."""

import os
import time

from nicos import session
from nicos.core import LimitError
from nicos.devices.generic.sequence import SeqDev, SeqParam, SeqMethod, \
    SeqCall, SeqSleep, SeqNOP

from test.utils import raises

methods_called = set()

# due to time.time() and time.sleep() resolution on windows
DELTA = 0.05 if os.name == 'nt' else 0


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
    # parameter checking
    assert raises(TypeError, SeqDev)
    assert raises(TypeError, SeqParam)
    assert raises(TypeError, SeqMethod)
    assert raises(TypeError, SeqCall)
    assert raises(TypeError, SeqSleep)
    SeqNOP()


def test_seqdev():
    # Device move
    sm1 = session.getDevice('sm1')
    sd = SeqDev(sm1, 3)
    assert repr(sd) == 'sm1 -> 3.000'
    sm1.start(0)
    sm1.wait()
    assert sm1.read(0) == 0

    sd.check()
    sd.run()
    while not sd.isCompleted():
        pass
    assert sm1.read(0) == 3


def test_seqparam():
    # Param setting
    sm2 = session.getDevice('sm2')
    sp = SeqParam(sm2, 'speed', 1)
    assert 'sm2.speed' in repr(sp)
    assert repr(sp).endswith('1')

    sm2.speed = 5
    assert sm2.speed == 5
    sp.check()
    sp.run()
    while not sp.isCompleted():
        pass
    assert sm2.speed == 1


def test_seqmethod():
    # method calling, use fix/relase here
    sm1 = session.getDevice('sm1')
    sm = SeqMethod(sm1, 'fix', 'blubb')
    assert repr(sm) == "sm1 fix"

    assert sm1.fixed == ''

    sm.check()
    sm.run()
    while not sm.isCompleted():
        pass
    assert 'blubb' in sm1.fixed

    sm1.release()


def test_seqsleep():
    # Sleeping??
    sw = SeqSleep(0.1)
    assert repr(sw).startswith('0.1')
    a = time.time()
    sw.check()
    sw.run()
    while not sw.isCompleted():
        pass
    b = time.time()

    assert 0.08 - DELTA <= b - a <= 0.15 + DELTA


def test_seqcall():
    # Calling
    sc = SeqCall(time.sleep, 0.1)
    assert repr(sc) == 'sleep'
    a = time.time()
    sc.check()
    sc.run()
    assert sc.isCompleted() is True
    b = time.time()
    assert 0.08 - DELTA <= b - a <= 0.15 + DELTA


def test_seqnop():
    # NOP
    sn = SeqNOP()
    sn.check()
    sn.run()
    assert sn.isCompleted() is True
    sn.stop()
    sn.retry(5)


def test_locked_multiswitcher():
    # Guard against regression of #1315
    lms = session.getDevice('ld2')
    assert raises(LimitError, lms.move, 0)
