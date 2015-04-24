#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2017 by the NICOS contributors (see AUTHORS)
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
#   Bjoern Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Test the IsController mixin.
"""
from nicos.core import LimitError
from test.utils import raises

session_setup = 'controller'


def test_controller(session):
    controller = session.getDevice('controller')
    dev1 = session.getDevice('dev1')
    dev2 = session.getDevice('dev2')
    assert dev1.read() == 0
    assert dev2.read() == 0

    dev2.move(100.)
    assert dev2.read() == 100.
    assert raises(LimitError, dev1.move, 200.)

    controller.move((10., 20.))
    assert dev1.read() == 10.0
    assert dev2.read() == 20.0

    assert raises(LimitError, controller.move, (300., 0))
