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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""STRESS-SPEC specific slits tests."""

from nicos.core.errors import MoveError
from test.utils import raises

session_setup = 'stressi'


def test_slit(session):
    slit = session.getDevice('slits')
    slit.maw((0, 0))
    assert slit.read(0) == [0, 0]

    slit.opmode = 'offcentered'
    slit.maw((1, 1, 0, 0))
    assert slit.read(0) == [1, 1, 0, 0]

    slit.maw((-1, -1, 0, 0))
    assert slit.read(0) == [-1, -1, 0, 0]

    slit._attached_left.speed = 1
    slit._attached_right.speed = 1
    slit._attached_top.speed = 1
    slit._attached_bottom.speed = 1
    slit.move((0, 0, 0, 0))
    assert raises(MoveError, slit.move, (0, 0, 0, 0))


def test_twoaxisslit(session):
    slit = session.getDevice('slitm')
    slit.maw((0, 0))
    assert slit.read(0) == [0, 0]
