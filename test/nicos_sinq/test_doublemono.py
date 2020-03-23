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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************

import pytest

from nicos.core import NicosError, PositionError

session_setup = 'sinq_doublemono'


def test_doublemono(session):
    wl = session.getDevice('wavelength')
    mth1 = session.getDevice('mth1')
    mth2 = session.getDevice('mth2')
    mtx = session.getDevice('mtx')

    wl.maw(2.55)

    assert(abs(mth1.read(0)-22.4768) < mth1.precision)
    assert(abs(mth2.read(0)-22.4768) < mth2.precision)
    assert(abs(mtx.read(0)-100.1623) < mtx.precision)

    wl.maw(4.33)
    assert(abs(mth1.read(0)-40.4795) < mth1.precision)
    assert(abs(mth2.read(0)-40.4795) < mth2.precision)
    assert(abs(mtx.read(0)-15.9119) < mtx.precision)

    wl._checkArrival()

    mth1.maw(42.)
    with pytest.raises(PositionError):
        wl._checkArrival()

    mth2.maw(42.)
    with pytest.raises(PositionError):
        wl._checkArrival()

    wl.maw(4.33)

    with pytest.raises(NicosError):
        mtx.maw(17.)
