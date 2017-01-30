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

from nicos.refsans.params import motoraddress

from test.utils import raises


def test_refsans():
    assert motoraddress(0x3020) == 0x3020
    assert motoraddress(0x302a) == 0x302a
    assert motoraddress(0x4020) == 0x4020
    assert motoraddress(0x47f0) == 0x47f0
    assert raises(ValueError, motoraddress, 0x2000)
    assert raises(ValueError, motoraddress, 0x3000)
    assert raises(ValueError, motoraddress, 0x4000)
    assert raises(ValueError, motoraddress, 0x4021)
    assert raises(ValueError, motoraddress, 0x4800)
    assert raises(ValueError, motoraddress, 0x47fa)
