# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS axis test suite."""

from time import sleep

import pytest
from pytest import approx

from nicos.core import LimitError, status

session_setup = 'axis'


def test_params(session):
    axis = session.getDevice('axis')
    # drag error should be the default: 1
    assert axis.dragerror == 1

    # min/max parameters got from motor device
    assert axis.abslimits == (-100, +100)
    # usermin/usermax got from motor device
    assert axis.userlimits == (-50, +50)
    # unit automatically from motor device
    assert axis.unit == 'mm'
    # abslimits from config
    axis2 = session.getDevice('limit_axis')
    assert axis2.abslimits == (-1, +1)
    # offset
    axis2.maw(1)
    assert axis2.read() == approx(1)
    axis2.offset = 1
    assert axis2.read() == approx(0)


def test_motor_limits(session):
    axis = session.getDevice('nolimit_axis')
    motor = session.getDevice('nolimit_motor')

    assert axis.offset == 0
    assert axis.abslimits == motor.abslimits == (-100, 100)
    assert axis.userlimits == motor.userlimits == (-50, 50)

    # test userlimits propagation
    newul = (-60, 60)
    axis.userlimits = newul
    assert axis.userlimits == motor.userlimits == newul

    # test for correct offset handling
    offset = 20
    axis.offset = offset
    # axis userlimits should be shifted by offset
    assert axis.userlimits == (newul[0] - offset, newul[1] - offset)
    # motor userlimits should be unaffected
    assert motor.userlimits == newul

    # same after setting new userlimits
    newul = (-120, 70)
    axis.userlimits = newul
    # axis userlimits should be given limits
    assert axis.userlimits == newul
    # motor userlimits should differ by offset
    assert motor.userlimits == (newul[0] + offset, newul[1] + offset)

    # now we must be able to move to the limits
    axis.maw(-120)
    axis.maw(70)


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
    pytest.raises(LimitError, axis.move, 150)
    # simulate a busy motor
    axis._attached_motor.curstatus = (status.BUSY, 'busy')
    # moving while busy?
    # pytest.raises(NicosError, axis.move, 10)
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
        motor.stop()


def test_reset(session):
    axis = session.getDevice('axis')
    axis.reset()


def test_backlash(session):
    axis = session.getDevice('backlash_axis')
    motor = session.getDevice('motor')
    axis.maw(0)
    motor.speed = 0.5
    axis.move(1)
    sleep(0.1)
    axis.stop()
    assert 0 <= axis.read() <= 1


def test_obs(session):
    axis = session.getDevice('obs_axis')
    obs = session.getDevice('coder2')
    obs.offset = 0.1
    axis.maw(0)
    axis.reset()
    obs.offset = 0.5
    axis.maw(1)
    axis.reset()
