#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""SPODI specific chopper tests."""

from nicos.core import status

from test.utils import approx

session_setup = 'toftof'


def test_toftof_chopper(session):
    chRatio = session.getDevice('chRatio')
    chCRC = session.getDevice('chCRC')
    chST = session.getDevice('chST')
    chDS = session.getDevice('chDS')
    ch = session.getDevice('ch')

    assert chRatio.read(0) == 1
    assert chCRC.read(0) == 1
    assert chST.read(0) == 1
    # speed = 0
    speed = 6000
    assert chDS.read(0) == [speed, speed, speed, speed, speed, speed, speed]

    for disc in ['d1', 'd2', 'd3', 'd4', 'd6', 'd7']:
        assert session.getDevice(disc).read(0) == speed
    assert session.getDevice('d5').read(0) == -speed

    chSpeed = session.getDevice('chSpeed')
    chSpeed.maw(6000)
    assert chSpeed.read(0) == speed
    assert chDS.status(0)[0] == status.OK

    chWL = session.getDevice('chWL')
    assert chWL.read(0) == 4.5

    chWL.maw(5)
    assert chWL.read(0) == 5

    chRatio.maw(2)
    assert chRatio.read(0) == 2

    chST.maw(2)
    assert chST.read(0) == 2

    chCRC.maw(0)
    assert chCRC.read(0) == 0

    speeds = [6000, 3000, 4000, 4500, 4800, 5000, 5143, 5250, 4667, 4200]

    for r, s in zip(range(1, 11), speeds):
        chRatio.maw(r)
        assert chRatio.read(0) == r
        assert chDS.read(0)[4] == approx(s, 1)
        assert ch.read(0) == approx(6000, 0.1)

    chRatio.maw(1)
    assert chRatio.read(0) == 1
    chCRC.maw(1)
    assert chCRC.read(0) == 1
    chST.maw(1)
    assert chST.read(0) == 1
    chWL.maw(4.5)
    assert chWL.read(0) == 4.5
