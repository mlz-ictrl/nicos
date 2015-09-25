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
# *****************************************************************************

"""Devices for the SANS-1 oxford magnet (ccmsans)."""

from nicos.core import Param, oneof, status, HasTimeout, Override
from nicos.devices.taco.power import CurrentSupply


class AsymmetricMagnet(HasTimeout, CurrentSupply):
    """Class for the asymmetric ccmsans.

    Provides the ability to set the current field, and the asymmetry ratio.
    """

    parameters = {
        'asymmetry': Param('Asymmetry ratio',
                           type=oneof(0.0, 0.11, 0.25, 0.39, 0.53, 0.70),
                           settable=True,
                           volatile=True),
    }

    parameter_overrides = {
        # default timeout: doTime() + 5 mins
        'timeout': Override(mandatory=False, default=300),
    }

    parameter_overrides = {
        'timeout': Override(mandatory=False, default=5400 + 300) # max range * max ramp + 5'
    }

    busystates = (status.BUSY, status.ERROR)
    valuetype = float

    def doReadAsymmetry(self):
        return float(self._taco_guard(self._dev.deviceQueryResource, 'asymmetry'))

    def doWriteAsymmetry(self, value):
        self._taco_update_resource('asymmetry', str(value))
