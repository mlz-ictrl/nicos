#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

session_setup = 'pgaa'


def test_ellcol(session):
    ellipse = session.getDevice('ellipse')
    collimator = session.getDevice('collimator')
    assert [ellipse.read(0), collimator.read(0)] == [0, 0]

    # Create a not allowed state for the changer and force a reset on changer
    ellipse.maw(1)
    collimator.maw(1)
    assert [ellipse.read(0), collimator.read(0)] == [1, 1]

    ellcol = session.getDevice('ellcol')
    assert ellcol.read(0) is None

    ellcol.maw('Col')
    assert ellcol.read(0) == 'Col'
    assert ellcol._attached_collimator.read(0) == 1
    assert ellcol._attached_ellipse.read(0) == 0

    ellcol.maw('Ell')
    assert ellcol.read(0) == 'Ell'
    assert ellcol._attached_collimator.read(0) == 0
    assert ellcol._attached_ellipse.read(0) == 1

    # Test code path, that device is on target
    ellcol.maw('Ell')
    assert ellcol.read(0) == 'Ell'

    assert raises(LimitError, ellcol.move, 'abc')

    # Force an error when call another move when moving
    ellcol.move('Col')
    session.delay(0.1)
    assert raises(LimitError, ellcol.maw, 'Ell')
    ellcol.wait()
