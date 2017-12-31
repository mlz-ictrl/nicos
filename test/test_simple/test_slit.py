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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

from __future__ import print_function

from nicos.core import status, LimitError, InvalidValueError
from nicos.devices.generic.slit import Slit
from test.utils import raises

session_setup = 'slit'
Slit._delay = 0.01


def test_slit(session):
    slit = session.getDevice('slit')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')

    slit.opmode = '4blades'
    slit.maw([1, 2, 3, 4])
    print([motor_right.doRead(),
           motor_left.doRead(),
           motor_bottom.doRead(),
           motor_top.doRead()])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 2
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert slit.doRead() == [motor_left.doRead(),
                             motor_right.doRead(),
                             motor_bottom.doRead(),
                             motor_top.doRead()]

    slit.reset()
    slit.stop()
    assert slit.doStatus()[0] == status.OK


def test_slit_opposite(session):
    s2 = session.getDevice('slit2')
    motor_right = session.getDevice('m_right')
    motor_left = session.getDevice('m_left')
    motor_bottom = session.getDevice('m_bottom')
    motor_top = session.getDevice('m_top')

    s2.opmode = '4blades_opposite'
    s2.maw([1, 2, 3, 4])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 2
    assert s2.width.doRead() == 3
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert s2.height.doRead() == 7
    assert s2.doRead() == [1, 2, 3, 4]

    s2.maw([-2.5, 2.5, -2.5, 2.5])
    assert s2.width.doRead() == 0
    assert s2.height.doRead() == 0

    s2.opmode = 'centered'
    s2.maw([5, 5])
    assert motor_left.doRead() == 2.5
    assert motor_right.doRead() == 2.5
    assert motor_bottom.doRead() == 2.5
    assert motor_top.doRead() == 2.5

    s2.opmode = 'offcentered'
    s2.maw([1, 2, 4, 6])
    assert motor_left.doRead() == 1
    assert motor_right.doRead() == 3
    assert motor_bottom.doRead() == 1
    assert motor_top.doRead() == 5

    assert raises(LimitError, s2.start, [1, 2, -1, 0])


def test_slit_opmodes(session, log):
    slit = session.getDevice('slit')

    slit.opmode = '4blades'
    slit.maw([8, 9, 4, 5])
    assert slit.read() == [8, 9, 4, 5]
    assert raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    assert raises(InvalidValueError, slit.start, [1, 2, 3])
    assert raises(InvalidValueError, slit.start, [800, 0])
    assert raises(LimitError, slit.start, [8, 8000, 4, 6])
    assert len(slit.valueInfo()) == 4

    slit.maw([8, 10, 4, 7])
    assert slit.read() == [8, 10, 4, 7]

    slit.opmode = 'centered'
    with log.assert_warns():
        slit.read()
    slit.maw([0, 0])
    assert raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    assert raises(InvalidValueError, slit.doStart, [800, 0, 0, 0])
    assert raises(LimitError, slit.start, [-2, 0])
    assert raises(LimitError, slit.start, [0, -2])
    slit.maw([2, 3])
    assert len(slit.valueInfo()) == 2

    slit.opmode = 'offcentered'
    assert slit.read() == [0, 0, 2, 3]
    assert raises(InvalidValueError, slit._getPositions, [1, 2, 4])
    assert raises(InvalidValueError, slit.start, [1, 2, 3])
    assert raises(InvalidValueError, slit.start, [800, 0])
    assert raises(LimitError, slit.start, [-1, -1, 1000, 0])
    slit.maw([5, 1, 4, 4])
    assert slit.read() == [5, 1, 4, 4]
    assert len(slit.valueInfo()) == 4

    slit.opmode = '4blades'
    assert slit.read() == [3, 7, -1, 3]


def test_slit_subaxes(session):
    slit = session.getDevice('slit')

    slit.opmode = 'offcentered'
    slit.maw([5, 1, 4, 4])
    assert slit.read() == [5, 1, 4, 4]

    assert slit.centerx() == 5
    assert slit.centery() == 1
    assert slit.width() == 4
    assert slit.height() == 4
    assert slit.left() == 3
    assert slit.right() == 7
    assert slit.bottom() == -1
    assert slit.top() == 3

    slit.centerx.maw(0)
    assert slit.read() == [0, 1, 4, 4]
    slit.centery.maw(0)
    assert slit.read() == [0, 0, 4, 4]
    slit.width.maw(2)
    assert slit.read() == [0, 0, 2, 4]
    slit.height.maw(2)
    assert slit.read() == [0, 0, 2, 2]

    slit.left.maw(-3)
    assert slit.read(0) == [-1, 0, 4, 2]
    slit.right.maw(3)
    assert slit.read(0) == [0, 0, 6, 2]
    slit.bottom.maw(-3)
    assert slit.read(0) == [0, -1, 6, 4]
    slit.top.maw(3)
    assert slit.read(0) == [0, 0, 6, 6]


def test_slit_reference(session, log):
    slit = session.getDevice('slit')
    with log.assert_warns('m_left cannot be referenced'):
        slit.reference()
