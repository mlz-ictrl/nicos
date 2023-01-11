#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

"""STRESS-SPEC specific wavelength device tests."""

import pytest

from nicos.core import status
from nicos.core.errors import ConfigurationError, InvalidValueError

from test.utils import approx, raises

session_setup = 'spodi'

pytest.importorskip('dataparser')


def test_basic(session):
    """Test basic functions."""
    # get wavelength device
    wav = session.getDevice('wav')

    # Attached devices are not at right positions device
    assert wav.plane == '551'  # pylint: disable=compare-to-empty-string
    assert wav.read(0) == approx(1.548, abs=0.001)
    assert wav.status(0)[0] == status.OK
    assert wav.crystal is 'Ge'
    assert raises(ValueError, setattr, wav, 'plane', '311')
    assert raises(InvalidValueError, wav.maw, 1)

    # external rotation of the monochromator will be set to valid pos
    tthm = session.getDevice('tthm')
    tthm.maw(155)
    assert wav.status(0)[0] == status.OK
    assert wav._crystal(0) is not None

    # plane setting
    assert wav.plane == '551'
    assert wav.crystal is 'Ge'
    wav.plane = '771'
    assert wav.read(0) == approx(1.111, abs=0.001)
    wav.plane = '551'
    assert wav.read(0) == approx(1.548, abs=0.001)
    wav.plane = '331'
    assert wav.read(0) == approx(2.537, abs=0.001)


def test_init(session):
    """Test init of device if external devices at right positions."""
    # remove the existing device
    session.destroyDevice('wav')
    # set the external devices correctly
    # transm = session.getDevice('transm')
    # transm.maw('Ge')
    omgm = session.getDevice('tthm')
    omgm.maw(155)
    # recreate device
    wav = session.createDevice('wav', recreate=True)
    # check plane
    assert wav.crystal == 'Ge'
    assert wav.plane == '551'
    assert wav.read(0) == approx(1.548, abs=0.001)
