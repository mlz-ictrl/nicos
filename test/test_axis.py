#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS axis test suite
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

"""NICOS axis test suite."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm import nicos
from nicm import status
from nicm.errors import NicmError, LimitError
from test.utils import raises

axis = None

def setup_module():
    global axis
    nicos.load_setup('axis')
    axis = nicos.get_device('axis')

def teardown_module():
    nicos.unload_setup()

def test_params():
    # min/max parameters got from motor device
    assert axis.getAbsmin() == -100
    assert axis.getAbsmax() == +100
    # usermin/usermax parameters in the config
    assert axis.getUsermin() == -50
    assert axis.getUsermax() == +50
    # unit automatically from motor device
    assert axis.getUnit() == 'mm'

def test_movement():
    # initial position
    assert axis.read() == 0
    # moving once
    axis.move(1)
    axis.wait()
    assert axis.read() == 1
    assert axis.status() == status.OK
    # moving again
    axis.move(2)
    axis.wait()
    assert axis.read() == 2
    assert axis.status() == status.OK
    # moving out of limits?
    assert raises(LimitError, axis.move, 150)
    # simulate a busy motor
    axis.motor._VirtualMotor__busy = True
    # moving while busy?
    assert raises(NicmError, axis.move, 10)
    # forwarding of motor status by doStatus()
    assert axis.status() == status.BUSY
    axis.motor._VirtualMotor__busy = False
