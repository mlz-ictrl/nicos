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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS axis test suite."""

from time import sleep

from nicos.core import status, LimitError
from test.utils import raises, approx
from nicos.commands.basic import ClearCache


session_setup = 'axis'


def test_params(session):
    # since the axis device was used before the device should be destroyed
    # and recreated to check the initialisation of the parameters
    session.destroyDevice('axis')
    ClearCache('axis')
    axis = session.getDevice('axis')
    # drag error should be the default: 1
    assert axis.dragerror == 1

    # min/max parameters got from motor device
    assert axis.abslimits == (-100, +100)
    # usermin/usermax parameters in the config
    assert axis.userlimits == (-50, +50)
    # unit automatically from motor device
    assert axis.unit == 'mm'
    # abslimits from config
    axis2 = session.getDevice('limit_axis')
    assert axis2.abslimits == (-1, +1)
    # offset
    axis.maw(1)
    assert axis.read() == approx(1)
    axis.offset = 1
    assert axis.read() == approx(0)
    axis.offset = 0


def test_movement(session):
    axis = session.getDevice('axis')
    # moving once
    axis.maw(1)
    assert axis.read() == approx(1)
    assert axis.status()[0] == status.OK
    # moving again
    axis.maw(2)
    assert axis.read() == approx(2)
    assert axis.status()[0] == status.OK
    # moving out of limits?
    assert raises(LimitError, axis.move, 150)
    # simulate a busy motor
    axis._attached_motor.curstatus = (status.BUSY, 'busy')
    # moving while busy?
    # assert raises(NicosError, axis.move, 10)
    # forwarding of motor status by doStatus()
    assert axis.status(0)[0] == status.BUSY
    axis._attached_motor.curstatus = (status.OK, '')

    # now move for a while
    axis.maw(0)
    motor = session.getDevice('motor')
    motor.speed = 5
    try:
        axis.move(0.5)
        axis.wait()
        assert axis.read() == approx(0.5)

        axis.move(0)
        sleep(0.1)
        axis.stop()
        axis.wait()
        assert 0 <= axis.read() <= 1
    finally:
        motor.speed = 0
        motor.stop()


def test_reset(session):
    axis = session.getDevice('axis')
    axis.reset()


def test_backlash(session):
    axis = session.getDevice('backlash_axis')
    motor = session.getDevice('motor')
    motor.stop()  # if it's still moving from previous test
    axis.maw(0)
    motor.speed = 0.5
    try:
        axis.move(1)
        sleep(0.1)
        axis.stop()
        assert 0 <= axis.read() <= 1
    finally:
        motor.speed = 0


def test_obs(session):
    axis = session.getDevice('obs_axis')
    motor = session.getDevice('motor')
    motor.stop()  # if it's still moving from previous test
    obs = session.getDevice('coder2')
    obs.offset = 0.1
    axis.maw(0)
    axis.reset()
    obs.offset = 0.5
    axis.maw(1)
    axis.reset()
