# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.commands.device import maw
from nicos.core.errors import LimitError

session_setup = 'brslit'


def test_left_right(session):
    brle = session.getDevice('brle')
    brri = session.getDevice('brri')
    # This seems to be necessary to load the slit
    # and have the devices attached and thus controlled.
    session.getDevice('slit')

    # normal operation
    maw(brri, -10, brle, -10)

    # crash prevented
    with pytest.raises(LimitError):
        brle.maw(-12)


def test_top_bottom(session):
    brto = session.getDevice('brto')
    brbo = session.getDevice('brbo')
    # This seems to be necessary to load the slit
    # and have the devices attached and thus controlled.
    session.getDevice('slit')

    # normal operation
    maw(brto, -20, brbo, -20)

    # crash prevented
    with pytest.raises(LimitError):
        brto.maw(-38)
