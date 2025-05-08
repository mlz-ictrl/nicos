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
# Module author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

session_setup = 'lpa_kompass'


def test_guide_field(session):

    gf = session.getDevice('gf4')
    alpha = session.getDevice('alphastorage')

    assert gf.read(0) is None

    gf.maw('0')
    assert gf.read(0) == '0'

    gf.maw('off')
    assert gf.read(0) == 'off'

    alpha.maw(10)
