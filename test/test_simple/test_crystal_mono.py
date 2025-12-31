# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

import pytest

from nicos.core.errors import LimitError

session_setup = 'monotest'


@pytest.fixture
def mono(session):
    """Create a common set up at the start the crystal monochromator test."""

    monodev = session.getDevice('mono')
    monodev.theta.maw(40)
    monodev.ttheta.maw(80)

    yield monodev

    del monodev


def test_mono_device(session, mono):

    assert mono.material == 'Ge'
    assert mono.reflection == (3, 3, 1)
    assert mono.d == 1.299194
    assert mono.abslimits == (pytest.approx(1.098, abs=1e-3),
                              pytest.approx(2.542, abs=1e-3))
    assert mono.read(0) == pytest.approx(1.670, abs=1e-3)

    mono.theta.maw(67.5)
    mono.ttheta.maw(135)
    assert mono.read(0) == pytest.approx(2.401, abs=1e-3)

    mono.maw(2.53446)
    assert mono.theta.read(0) == pytest.approx(77.26, abs=1e-2)
    assert mono.ttheta.read(0) == pytest.approx(77.26 * 2, abs=1e-2)

    mono.theta.maw(40)
    mono.ttheta.maw(80)
    mono.reflection = (3, 1, 1)
    assert mono.d == 1.7058
    assert mono.read(0) == pytest.approx(2.193, abs=1e-3)

    pytest.raises(ValueError, setattr, mono, 'reflection', (0, 0, 0))

    mono.material = 'Si'
    assert mono.reflection == (1, 1, 1)
    assert mono.d == 3.13
    assert mono.read(0) == pytest.approx(4.024, abs=1e-3)


def test_mono_device_movements(session, mono):

    assert mono.read(0) == pytest.approx(1.670, abs=1e-3)
    mono.maw(1.68)

    pytest.raises(LimitError, mono.maw, 1)
