#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS device class test suite."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
 
from nicos import session
from nicos import status
from nicos.device import Device, Moveable, HasLimits, Param
from nicos.errors import ConfigurationError, LimitError, FixedError
from test.utils import raises


methods_called = set()

def setup_module():
    global axis
    session.loadSetup('device')
    methods_called.clear()

def teardown_module():
    session.unloadSetup()


class Dev1(Device):
    pass

class Dev2(HasLimits, Moveable):
    attached_devices = {'attached': Dev1}
    parameters = {
        'param1': Param('An optional parameter', type=int, default=42),
        'param2': Param('A mandatory parameter', type=int, mandatory=True,
                        settable=True),
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
        return status.BUSY, 'busy'

    def doReset(self):
        methods_called.add('doReset')

    def doReadParam2(self):
        return 21

    def doWriteParam2(self, value):
        methods_called.add('doWriteParam2')
        return value + 1

    def doUpdateParam2(self, value):
        methods_called.add('doUpdateParam2')


def test_params():
    dev2 = session.getDevice('dev2_1')
    # make sure adev instances are created
    assert isinstance(dev2._adevs['attached'], Dev1)
    # an inherited and writable parameter
    assert dev2.unit == 'mm'
    dev2.unit = 'deg'
    assert dev2.unit == 'deg'
    # a readonly parameter
    assert dev2.param1 == 42
    assert raises(ConfigurationError, setattr, dev2, 'param1', 21)
    # a parameter with custom getter and setter
    assert dev2.param2 == 21
    dev2.param2 = 5
    assert dev2.param2 == 6
    # Dev2 instance without adev
    assert raises(ConfigurationError, session.getDevice, 'dev2_2')

def test_methods():
    dev2 = session.getDevice('dev2_3')
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
    assert dev2.status()[0] == status.BUSY
    # save time for history query
    t1 = time.time()
    # __call__ interface
    dev2(7)
    assert dev2() == 7
    # another timestamp
    t2 = time.time()
    dev2.move(4)
    dev2.read()
    # further methods
    dev2.reset()
    assert 'doReset' in methods_called
    dev2.stop()
    assert 'doStop' in methods_called
    dev2.wait()
    assert 'doWait' in methods_called
    # fixing and releasing
    dev2.fix()
    assert raises(FixedError, dev2.move, 7)
    assert raises(FixedError, dev2.stop)
    dev2.release()
    dev2.move(7)
