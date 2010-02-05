#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS device test suite
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICOS device class test suite."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from nicm import nicos
from nicm import status
from nicm.device import Device, Moveable
from nicm.errors import ConfigurationError, LimitError, FixedError
from test.utils import raises


methods_called = set()

def setup_module():
    global axis
    nicos.load_setup('device')
    methods_called.clear()

def teardown_module():
    nicos.unload_setup()


class Dev1(Device):
    pass

class Dev2(Moveable):
    attached_devices = {'attached': Dev1}
    parameters = {
        'param1': (42, False, 'An optional parameter.'),
        'param2': (0, True, 'A mandatory parameter.'),
    }

    def doInit(self):
        self._val = 0
        methods_called.add('doInit')

    def doRead(self):
        return self._val

    def doIsAllowed(self, pos):
        if pos == 5:
            return False, 'foo'
        methods_called.add('doIsAllowed')
        return True, ''

    def doStart(self, pos):
        self._val = pos
        methods_called.add('doStart')

    def doStop(self):
        methods_called.add('doStop')

    def doWait(self):
        methods_called.add('doWait')

    def doStatus(self):
        return status.BUSY

    def doReset(self):
        methods_called.add('doReset')

    def doFix(self):
        methods_called.add('doFix')

    def doRelease(self):
        methods_called.add('doRelease')

    def doGetParam2(self):
        return self._params['param2'] + 1

    def doSetParam2(self, value):
        self._params['param2'] = value + 1


def test_params():
    dev2 = nicos.get_device('dev2_1')
    # make sure adev instances are created
    assert isinstance(dev2.attached, Dev1)
    # an inherited and writable parameter
    assert dev2.getUnit() == 'mm'
    dev2.setUnit('deg')
    assert dev2.getUnit() == 'deg'
    # a readonly parameter
    assert dev2.getParam1() == 42
    assert raises(ConfigurationError, dev2.setParam1, 21)
    # a parameter with custom getter and setter
    assert dev2.getParam2() == 2
    dev2.setParam2(5)
    assert dev2.getParam2() == 7
    # Dev2 instance without adev
    assert raises(ConfigurationError, nicos.get_device, 'dev2_2')

def test_methods():
    dev2 = nicos.get_device('dev2_3')
    assert 'doInit' in methods_called
    dev2.move(10)
    assert 'doStart' in methods_called
    assert 'doIsAllowed' in methods_called
    # moving beyond limits
    assert raises(LimitError, dev2.move, 50)
    # or forbidden by doIsAllowed()
    assert raises(LimitError, dev2.move, 5)
    # read() and status()
    assert dev2.read() == 10
    assert dev2.status() == status.BUSY
    # save time for history query
    t1 = time.time()
    # __call__ interface
    dev2(7)
    assert dev2() == 7
    # another timestamp
    t2 = time.time()
    dev2.move(4)
    dev2.read()
    # history (provided by LocalHistory)
    history = dev2.history()
    assert [x[1] for x in history] == [10, 7, 4]
    history = dev2.history(totime=t2)
    assert [x[1] for x in history] == [10, 7]
    history = dev2.history(fromtime=t1)
    assert [x[1] for x in history] == [7, 4]
    history = dev2.history(fromtime=t1, totime=t2)
    assert [x[1] for x in history] == [7]
    # further methods
    dev2.reset()
    assert 'doReset' in methods_called
    dev2.stop()
    assert 'doStop' in methods_called
    dev2.wait()
    assert 'doWait' in methods_called
    # fixing and releasing
    dev2.fix()
    assert 'doFix' in methods_called
    assert raises(FixedError, dev2.move, 7)
    assert raises(FixedError, dev2.stop)
    dev2.release()
    assert 'doRelease' in methods_called
    dev2.move(7)
