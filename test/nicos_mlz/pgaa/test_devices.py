#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

import pytest

from nicos.core.errors import InvalidValueError, LimitError

from test.utils import raises

session_setup = 'pgaa'


def test_ellcol(session):
    ellipse = session.getDevice('ellipse')
    collimator = session.getDevice('collimator')
    assert [ellipse.read(0), collimator.read(0)] == [0, 0]

    # Create a not allowed state for the changer and force a reset on changer
    ellipse.maw(1)
    collimator.maw(1)
    assert [ellipse.read(0), collimator.read(0)] == [1, 1]

    ellcol = session.getDevice('ellcol')
    assert ellcol.read(0) is None

    ellcol.maw('Col')
    assert ellcol.read(0) == 'Col'
    assert ellcol._attached_collimator.read(0) == 1
    assert ellcol._attached_ellipse.read(0) == 0

    ellcol.maw('Ell')
    assert ellcol.read(0) == 'Ell'
    assert ellcol._attached_collimator.read(0) == 0
    assert ellcol._attached_ellipse.read(0) == 1

    # Test code path, that device is on target
    ellcol.maw('Ell')
    assert ellcol.read(0) == 'Ell'

    assert raises(InvalidValueError, ellcol.move, 'abc')

    # Force an error when call another move when moving
    # TODO: This test needs a better setup to create a more realistic time
    #       handling to slow down the change!
    # ellcol.move('Col')
    # session.delay(0.1)
    # assert raises(LimitError, ellcol.maw, 'Ell')
    # ellcol.wait()


class TestSampleChanger:

    @pytest.fixture(scope='function', autouse=True)
    def prepare(self, session):
        # this is needed to make the init of the controllers in motor and
        # push
        sc = session.getDevice('sc')
        motor = sc._attached_motor
        push = sc._attached_push

        motor.curvalue = 1
        push.maw('down')
        yield
        motor.curvalue = 1
        push.maw('down')

    def test_move(self, session):
        sc = session.getDevice('sc')
        assert sc.read(0) == 1
        assert sc._attached_push.read() == 'down'
        sc.maw(2)
        assert sc.read(0) == 2
        assert raises(InvalidValueError, sc.maw, 0)

    def test_block_pusher(self, session):
        sc = session.getDevice('sc')
        assert sc.read(0) == 1
        push = session.getDevice('push')
        push.maw('up')
        assert push.read(0) == 'up'
        sc._attached_motor.maw(1.5)
        assert raises(LimitError, push.move, 'down')

    def test_block_motor(self, session):
        motor = session.getDevice('samplemotor')
        push = session.getDevice('push')
        assert motor.read(0) == 1
        assert push.read(0) == 'down'
        assert raises(LimitError, motor.move, 2)

    def test_pusher(self, session):
        push = session.getDevice('push')
        assert push.read(0) == 'down'
        for v in ['up', 'down']:
            push.maw(v)
            assert push.read(0) == v


class TestAttenuator:

    def test_move(self, session):
        att = session.getDevice('att')
        assert att.read(0) == 100
        att.maw(47.)
        assert att.read(0) == 47
        assert session.getDevice('att2').read(0) == 'in'
