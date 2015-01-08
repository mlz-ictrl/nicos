#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""NICOS commands tests."""

from nicos import session
from nicos.core import UsageError

from nicos.commands.sample import activation

from test.utils import raises


def test_01wronginput():
    assert raises(UsageError, activation)  # session has no formula up to now
    assert raises(UsageError, activation, formula='H2O')
    assert raises(UsageError, activation, formula='H2O', flux=1e7)
    assert session.testhandler.warns(activation, warns_clear=True,
                                     formula='H2', instrument='XXX', mass=1)


def test_02function():
    data = activation(formula='H2', flux=20, mass=1, getdata=True)
    assert data['curr'] == 'Manual'
    assert data['flux']['fluence'] == 20
    assert data['result']['activation'] is None
    data = activation(formula='Au', flux=1e7, mass=1, getdata=True)
    assert data['result']['activation'] is not None
