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

"""REFSANS specific parameter definition helpers."""


def motoraddress(address=0x3020):
    """The motor address should start either at addresses 0x3020 or 0x4020
    and must have an offset of the multiple of 10 words (each motor control
    block is 20 bytes = 10 words). There are only 200 allowed addresses for one
    address offset.
    """
    if not (address & 0xF000) in (0x3000, 0x4000) or \
       not (0x20 <= (address & 0xFFF) <= 0x7f0) or \
       ((address & 0xFFF) - 0x20) % 10 != 0:
        raise ValueError('Invalid motor address: %0x04x!' % address)
    return address
