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
from nicos.core.errors import ConfigurationError, LimitError

session_setup = 'refsans'


def test_nok(session):
    nok2 = session.getDevice('nok2')
    assert nok2.read(0) == [0, 0]

    # nok2.reference()
    nok2.maw((1, 1))
    assert nok2.read(0) == [1, 1]

    assert raises(LimitError, nok2.maw, (0, 20))
    assert raises(LimitError, nok2.maw, (-30, -20))


def test_single_nok(session):
    nok1 = session.getDevice('nok1')
    assert nok1.read(0) == 0

    nok1.maw(1)
    assert nok1.read(0) == 1

    # nok1.reference()

def test_nok_pos(session):
    obs = session.getDevice('obs')
    assert obs.read(0) == 459.
    obs.reset()


def test_nok_inclination_failed(session):
    assert raises(ConfigurationError, session.getDevice, 'nok_inc_failed')
