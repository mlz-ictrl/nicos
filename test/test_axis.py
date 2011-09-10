#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS axis test suite."""

__version__ = "$Revision$"

from nicos import session
from nicos import status
from nicos.errors import NicosError, LimitError
from test.utils import raises

def setup_module():
    session.loadSetup('axis')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_params():
    axis = session.getDevice('axis')
    # min/max parameters got from motor device
    assert axis.abslimits == (-100, +100)
    # usermin/usermax parameters in the config
    assert axis.userlimits == (-50, +50)
    # unit automatically from motor device
    assert axis.unit == 'mm'

def test_movement():
    axis = session.getDevice('axis')
    # initial position
    assert axis.read() == 0
    # moving once
    axis.move(1)
    axis.wait()
    assert axis.read() == 1
    assert axis.status()[0] == status.OK
    # moving again
    axis.move(2)
    axis.wait()
    assert axis.read() == 2
    assert axis.status()[0] == status.OK
    # moving out of limits?
    assert raises(LimitError, axis.move, 150)
    # simulate a busy motor
    axis._adevs['motor'].curstatus = (status.BUSY, 'busy')
    # moving while busy?
    assert raises(NicosError, axis.move, 10)
    # forwarding of motor status by doStatus()
    axis._cache.clear(axis.name)
    assert axis.status()[0] == status.BUSY
    axis._adevs['motor'].curstatus = (status.OK, '')
