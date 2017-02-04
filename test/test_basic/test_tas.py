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

"""NICOS tests for session-less TAS code."""

from nicos.core import UsageError, NicosError
from nicos.commands.tas import Q
from nicos.devices.tas import spacegroups

from test.utils import raises


def test_Q_object():
    assert all(Q() == Q(0, 0, 0, 0))
    assert all(Q(1) == Q(1, 0, 0, 0))
    assert all(Q(1, 1) == Q(1, 1, 0, 0))
    assert all(Q(1, 1, 1) == Q(1, 1, 1, 0))
    q1 = Q(1, 2, 3, 4)
    for q2 in [
        Q(Q(1, 4, 3, 0), k=2, e=4),
        Q(1, 2, 3, e=4),
        Q(h=1, k=2, l=3, e=4),
        Q(H=1, K=2, L=3, E=4)
    ]:
        assert all(q2 == q1)
    assert raises(UsageError, Q, 1, 2, 3, 4, 5)
    assert repr(Q()) == '[ 0.  0.  0.  0.]'


def test_getspacegroup():
    # Good cases
    assert spacegroups.get_spacegroup(1) == \
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert spacegroups.get_spacegroup('Pbca') == \
        [3, 2, 2, 1, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    # Error cases
    assert raises(NicosError, spacegroups.get_spacegroup, 'Pbbb')
    assert raises(NicosError, spacegroups.get_spacegroup, 300)


def test_canreflect():
    # P1 all reflection types are allowed
    sg = spacegroups.get_spacegroup('P1')
    assert spacegroups.can_reflect(sg, 0, 0, 0)
    assert spacegroups.can_reflect(sg, 1, 0, 0)
    assert spacegroups.can_reflect(sg, 0, 1, 0)
    assert spacegroups.can_reflect(sg, 0, 0, 1)
    assert spacegroups.can_reflect(sg, 1, 1, 1)
