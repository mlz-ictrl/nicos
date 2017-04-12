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

"""Module to test custom specific modules."""

from test.utils import raises
from nicos.core.errors import LimitError

session_setup = 'puma'


def test_comb_axis(session):
    phi = session.getDevice('phi')
    assert phi.iscomb is False

    # test in normal operation mode
    assert phi.read(0) == 0
    for t in [10, 0]:
        phi.maw(t)
        assert phi.read(0) == t

    assert phi._attached_fix_ax.read(0) == 0

    # test in combined mode
    assert phi._fixpos is None

    phi.iscomb = True
    assert phi.iscomb is True
    assert phi._fixpos == 0

    phi.maw(10)
    assert phi.read(0) == 10
    assert phi._attached_fix_ax.read(0) == -10

    assert raises(LimitError, phi.move, 20)
