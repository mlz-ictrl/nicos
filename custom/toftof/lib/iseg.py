#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""ISEG power supply support."""

from nicos.core.params import Override
from nicos.devices.taco.power import VoltageSupply as BaseVoltageSupply

class VoltageSupply(BaseVoltageSupply):
    """ISEG hardware switches back to maximum ramp after switching off/on.

    The ramp should give back the right value for the ramp, not a cached one.
    """

    parameter_overrides = {
        'ramp': Override(volatile='True'),
    }
