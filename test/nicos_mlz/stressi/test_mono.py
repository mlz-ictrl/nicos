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

"""STRESS-SPEC specific monochromator tests."""

import time

from test.utils import raises

from nicos.core import status
from nicos.core.errors import ConfigurationError, InvalidValueError, \
    PositionError

import pytest

session_setup = 'stressi'


@pytest.yield_fixture(scope='function', autouse=True)
def fcleanup(session):
    yield

    if session is not None:
        devices = list(session.devices.keys())
        for dev in devices:
            session.destroyDevice(dev)
        if session.cache is not None:
            session.cache.clear_all()


def test_wavelength(session):
    transm = session.getDevice('transm')
    wav = session.getDevice('wav')

    # values of the transm and wav devices not correctly initialised
    assert raises(PositionError, transm.read, 0)
    assert wav.read(0) is None
    assert wav.status(0)[0] == status.WARN

    assert wav._attached_omgm.status()[0] == status.OK
    assert wav._attached_base.status()[0] == status.WARN
    assert wav._attached_crystal.status()[0] == status.NOTREACHED

    tthm = session.getDevice('tthm')
    assert tthm.read(0) == 0
    tthm.maw(69)
    assert tthm.read(0) == 69

    assert wav.read(0) is None
    assert wav.crystal is None

    # raises due to not defined crystal
    assert raises(ConfigurationError, wav.start, 1.7)
    assert raises(ConfigurationError, setattr, wav, 'plane', '100')
    transm.maw('Ge')

    assert wav.crystal == 'Ge'
    assert wav.plane == ''  # pylint: disable=compare-to-empty-string
    assert wav.status(0)[0] == status.ERROR
    # raises due to not defined plane
    assert raises(ConfigurationError, wav.start, 1.7)

    # Simulate the following state:
    # crystal changing device is properly initialised and has valid 'crystal'
    # plane is not defined
    # in demo mode it could be created by:
    # ClearCache('wav')
    # NewSetup()
    # ideas to simulate it are welcome

    session.destroyDevice(wav)
    session.cache.clear('wav')
    wav = session.getDevice('wav')
    assert wav.crystal == 'Ge'
    assert wav.plane == ''  # pylint: disable=compare-to-empty-string

    wav.plane = '311'
    assert wav.plane == '311'
    assert wav.status(0)[0] == status.OK
    assert raises(ValueError, setattr, wav, 'plane', '100')

    wav.maw(1.7)
    assert wav.read(0) == 1.7

    omgm = session.getDevice('omgm')
    tthm.speed = 0.1
    omgm.speed = 0.1

    wav.move(1.6)
    time.sleep(0.1)
    wav.stop()
    assert 1.6 < wav.read() < 1.7


def test_param_setting(session):
    wav = session.getDevice('wav')

    assert wav.crystal is None
    wav.crystal = 'Ge'
    assert wav.crystal == 'Ge'

    assert raises(InvalidValueError, setattr, wav, 'crystal', 'H')
