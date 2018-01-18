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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Astrium selector device with adoptions for RESEDA"""

from nicos.core import Param
from nicos.devices.vendor.astrium import SelectorLambda as NicosSelectorLambda

class SelectorLambda(NicosSelectorLambda):
    """
    Control selector wavelength directly, converting between speed and
    wavelength. (RESEDA version)
    """

    parameters = {
        'radius':     Param('Selector radius', mandatory=True, unit='m'),
    }

    def sel(self, maxage):
        '''Calculate wavelength in A from speed in rpm and tiltang in deg'''
        spd = self._attached_seldev.read(maxage)
        return 6.5933900e2 * (self.twistangle + self.length/self.radius * self._get_tilt(maxage)) / (spd * self.length)

    def sel_inv(self, lam,  maxage=0):
        '''Calculate rotation speed in rpm from wavelength in A and tiltang in deg'''
        return 6.5933900e2 * (self.twistangle + self.length/self.radius * self._get_tilt(maxage)) / (lam * self.length)

    def doRead(self, maxage=0):
        return self.sel(maxage)

    def doStart(self, value):
        speed = int(self.sel_inv(value))
        self.log.debug('moving selector to %d rpm', speed)
        self._attached_seldev.start(speed)
