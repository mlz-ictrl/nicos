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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************

import pytest

from nicos.core.errors import NicosError
from nicos.core.utils import multiWait

session_setup = 'sinq_stopo'


def test_stored_positions(session):

    v1 = session.getDevice('v1')
    v1.precision = .1
    v3 = session.getDevice('v3')
    v3.precision = .1

    stopo = session.getDevice('stopo')

    v1.start(3.3)
    v3.start(7.7)
    multiWait([v1, v3])

    stopo.define_position('p1', ('v1', 2.2), ('v3', 5.5))
    stopo.define_position('p2', v1, v3)
    stopo.define_position('p3', v1=1.7, v3=8.4)

    stopo.maw('p1')
    assert(abs(v1.read(0)-2.2) < v1.precision)
    assert(abs(v3.read(0)-5.5) < v3.precision)
    assert(stopo.read(0) == 'p1')

    stopo.maw('p2')
    assert(abs(v1.read(0)-3.3) < v1.precision)
    assert(abs(v3.read(0)-7.7) < v3.precision)
    assert(stopo.read(0) == 'p2')

    stopo.maw('p3')
    assert(abs(v1.read(0)-1.7) < v1.precision)
    assert(abs(v3.read(0)-8.4) < v3.precision)
    assert(stopo.read(0) == 'p3')

    with pytest.raises(NicosError):
        stopo.maw('gurke')

    stopo.delete('p1')
    with pytest.raises(NicosError):
        stopo.maw('p1')

    stopo.clear()
    with pytest.raises(NicosError):
        stopo.maw('p2')
