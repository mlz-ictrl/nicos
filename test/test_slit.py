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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.errors import LimitError
from test.utils import raises

def setup_module():
    session.loadSetup('slit')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_slit():
    slit = session.getDevice('slit_1')
    motor_right = session.getDevice('motor_right')
    motor_left = session.getDevice('motor_left')
    motor_bottom = session.getDevice('motor_bottom')
    motor_top = session.getDevice('motor_top')

    slit.opmode = '4blades'
    slit.doStart([1, 2, 3, 4])
    slit.doWait()
    assert motor_right.doRead() == 1
    assert motor_left.doRead() == 2
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert slit.doRead() == [motor_right.doRead(),
                             motor_left.doRead(),
                             motor_bottom.doRead(),
                             motor_top.doRead()]

    slit.doStart([8, 7, 6, 5])
    slit.doWait()
    assert slit.doRead() == [8, 7, 6, 5]

    assert raises(LimitError, slit.doStart, [8000, 7, 6, 5])

    slit.doStart([8, 4, 3, 5])
    slit.doWait()
    assert slit.doRead() == [8, 4, 3, 5]

    slit.opmode = 'centered'
    assert slit.doRead() == [-4, 2]

    slit.opmode = 'offcentered'
    assert slit.doRead() == [6, 4, -4, 2]

    slit.doStart([4, 2, 3, 5])
    slit.doWait()
    assert slit.doRead() == [4, 2, 3, 5]
    slit.opmode = '4blades'
    assert slit.doRead() == [2.5, 5.5, -0.5, 4.5]
