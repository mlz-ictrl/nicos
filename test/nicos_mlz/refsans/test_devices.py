#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""Module to test custom specific modules."""

from __future__ import absolute_import, division, print_function

from nicos.core import status

session_setup = 'refsans'


def test_beamstop(session):
    hil = session.getDevice('bsh_input_low')
    hi = session.getDevice('bsh_input')
    assert hil.read(0) == 3
    assert hi.read(0) == 3
    assert hi.status(0)[0] == status.OK

    hil.maw(0)
    assert hi.status(0)[0] == status.ERROR

    ci = session.getDevice('bsc_input')
    c = session.getDevice('bsc')
    assert ci.read(0) == 3
    assert c.read(0) == 'None'
    assert c.status(0)[0] == status.ERROR

    ci.maw(5)
    assert c.read(0) == 'Off'
    assert c.status(0)[0] == status.OK

    ci.maw(8)
    assert c.read(0) == 'On'
    assert c.status(0)[0] == status.OK


def test_focuspoint(session):
    table = session.getDevice('det_table_a')
    pivot = session.getDevice('det_pivot')
    pivot.maw(9)
    assert pivot.read(0) == 9
    table.maw(9575)
    assert table.read(0) == 9575
    fp = session.getDevice('det_table')
    assert fp.read(0) == 9575
    state = fp.status(0)
    assert state[0] == status.OK
    assert state[1] == 'focus'

    fp.maw(1000)
    state = fp.status(0)
    assert state[0] == status.OK
    assert state[1] == 'idle'
