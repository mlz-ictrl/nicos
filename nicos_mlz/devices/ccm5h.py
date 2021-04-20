#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Devices for the SANS-1 oxford magnet (ccm5h)."""

from nicos.core import HasTimeout, Override, Param, oneof
from nicos.devices.entangle import Actuator


class AsymmetricMagnet(HasTimeout, Actuator):
    """Class for the asymmetric ccmsans.

    Provides the ability to set the current field, and the asymmetry ratio.
    """

    parameters = {
        'asymmetry': Param('Asymmetry ratio',
                           type=oneof(0, 11, 25, 39, 53, 70),
                           settable=True,
                           volatile=True),
    }

    parameter_overrides = {
        # max range * max ramp + 5'
        'timeout': Override(mandatory=False, default=5400 + 300)
    }

    def doReadAsymmetry(self):
        return self._dev.asymmetry

    def doWriteAsymmetry(self, value):
        self._dev.asymmetry = value
