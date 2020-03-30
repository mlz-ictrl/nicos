#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

import pytest

from nicos.core import status
from nicos.core.errors import LimitError

from test.utils import raises

session_setup = 'refsans'


def test_slits(session):
    zb1 = session.getDevice('zb1')
    zb3 = session.getDevice('zb3')
    assert zb1.read(0) == 0.
    assert zb1.mode == 'slit'

    assert zb3.read(0) == [12., 0.]
    assert zb3.mode == 'slit'

    assert zb3.height.read(0) == 12.
    assert zb3.center.read(0) == 0.

    assert zb3.height.isAllowed(12.)[0]
    assert zb3.height.isAllowed(0.)[0]

    zb3.center.maw(10)
    assert zb3.read(0) == [12., 10]

    zb3.mode = 'point'
    assert zb3.read(0) == [12., 10]

    assert not zb3.height.isAllowed(20)[0]

    zb3.stop()


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


def test_skewmotor(session):
    bg = session.getDevice('backguard')
    assert bg.skew == 2
    assert bg.precision == 0.1
    assert bg.read(0) == 0
    bg.maw(1)
    assert bg.read(0) == 1
    assert bg._attached_motor_1.read(0) == 0
    assert bg._attached_motor_2.read(0) == 2
    assert bg._attached_motor_1.isAtTarget(0)
    assert bg._attached_motor_2.isAtTarget(2)
    assert bg.isAtTarget(1)


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


def test_resolution(session):
    rfp = session.getDevice('real_flight_path')
    res = session.getDevice('resolution')
    assert rfp.read(0) == 11.153
    assert res.read(0) == 6.168


class TestDevices(object):
    """Test class for the 'simple' REFSANS devices."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        pass

    def test_analog_encoder(self, session):
        dev = session.getDevice('acoder')
        raw = session.getDevice('rawcoder')
        assert dev.read(0) == 1
        raw.maw(1)
        assert dev.read(0) == 3
        raw.maw(-1)
        assert dev.read(0) == -1


class TestChopper(object):
    """Test class for the REFSANS chopper device."""

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        chopper = session.getDevice('chopper')
        chopper1 = session.getDevice('chopper_speed')
        chopper2 = session.getDevice('chopper2')

        # test configuration
        assert chopper1.read(0) == 1200
        assert chopper1.read(0) == chopper2.read(0)
        assert chopper2.pos == 5
        assert chopper1.current == 3.2

        assert chopper.read(0) == {'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0,
                                   'wlmax': 21.0, 'wlmin': 3.0}
        yield

        chopper.maw({'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0, 'wlmax': 21.0,
                     'wlmin': 3.0})
        chopper1.maw(1200)

    def test_change_chopper2_pos(self, session):
        chopper1 = session.getDevice('chopper_speed')
        chopper2 = session.getDevice('chopper2')

        # not allowed due to chopper speed isn't zero
        assert raises(LimitError, setattr, chopper2, 'pos', 4)

        # all choppers should follow chopper1 in speed
        chopper1.maw(1000)
        assert chopper2.read() == 1000

        # moving speed to zero and allow chopper2 position change
        chopper1.maw(0)
        chopper2.pos = 4
        assert chopper1.current == 0
        chopper1.maw(1000)

    def test_full_chopper_change(self, session):
        chopper = session.getDevice('chopper')
        chopper2 = session.getDevice('chopper2')

        chopper.maw({'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0, 'wlmax': 21.0,
                     'wlmin': 0.0})
        assert chopper.read(0) == {'D': 22.8, 'chopper2_pos': 5, 'gap': 0.0,
                                   'wlmax': 21.0, 'wlmin': 0.0}
        assert chopper2.phase == 0
        assert chopper.mode == 'normal_mode'

        # check 'chopper_pos == 6' move
        chopper.maw({'D': 22.8, 'chopper2_pos': 6, 'gap': 0.0, 'wlmax': 21.0,
                     'wlmin': 0.0})
        assert chopper.read(0) == {'D': 22.8, 'chopper2_pos': 6, 'gap': 0.0,
                                   'wlmax': 21.0, 'wlmin': 0.0}
        assert chopper2.phase == 300
        assert chopper.mode == 'virtual_disc2_pos_6'
