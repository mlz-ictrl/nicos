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

"""STRESS-SPEC specific wavelength device tests."""

from test.utils import approx, raises

from nicos.core import status
from nicos.core.errors import ConfigurationError

session_setup = 'stressi'


def test_basic(session):
    """Test basic functions."""
    # get wavelength device
    wav = session.getDevice('wav')

    # Attached devices are not at right positions device
    assert wav.plane == ''  # pylint: disable=compare-to-empty-string
    assert wav.read(0) is None
    assert wav.status(0)[0] == status.WARN
    assert wav.crystal is None
    assert raises(ConfigurationError, setattr, wav, 'plane', '311')
    assert raises(ConfigurationError, wav.maw, 1)

    # external monochromator changer will be set to a valid pos
    transm = session.getDevice('transm')
    transm.maw('Ge')
    assert transm.read(0) == 'Ge'
    assert wav.crystal == 'Ge'
    assert wav.status(0)[0] == status.WARN
    assert raises(ConfigurationError, wav.maw, 1)

    # external rotation of the monochromator will be set to valid pos
    omgm = session.getDevice('tthm')
    omgm.maw(68)
    assert wav.status(0)[0] == status.ERROR
    assert wav._crystal() is not None
    assert raises(ConfigurationError, wav.maw, 1)

    # plane setting
    assert wav.plane == ''  # pylint: disable=compare-to-empty-string
    assert raises(ValueError, setattr, wav, 'plane', '111')
    wav.plane = '311'
    assert wav.read(0) == approx(1.908, abs=0.001)

    wav.maw(1.7)
    assert wav.read(0) == 1.7


def test_init(session):
    """Test init of device if external devices at right positions."""
    # remove the existing device
    session.destroyDevice('wav')
    # set the external devices correctly
    transm = session.getDevice('transm')
    transm.maw('Ge')
    omgm = session.getDevice('tthm')
    omgm.maw(68)
    # recreate device
    wav = session.createDevice('wav', recreate=True)
    # check plane
    assert wav.crystal == 'Ge'
    assert wav.plane == '311'
    assert wav.read(0) == approx(1.908, abs=0.001)
