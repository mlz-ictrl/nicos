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
#   Aleks Wischolit <aleks.wischolit@frm2.tum.de>
#
# *****************************************************************************

"""Readout of the Astrium selector."""

from IO import StringIO

from nicos.core import Readable, Override, Attach, status
from nicos.devices.taco.core import TacoDevice


class Selector(TacoDevice, Readable):
    """
    Device object for a astrium selector.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='rpm'),
    }

    def doRead(self, maxage=0):
        tmp = self._taco_guard(self._dev.communicate,'FDR')
        ##FDR                                             \RPM  22794
        value = tmp[-6:].strip()
        return float(value)

    def doStatus(self, maxage=0):
        return status.OK, ''


class Wavelength(Readable):

    attached_devices = {
        'selector': Attach('to calculate the wavelength', Readable),
        'tiltangle': Attach('calculation', Readable)
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default='A')
    }

    def doRead(self, maxage=0):
        I = self._attached_selector.read(maxage)
        Angle = self._attached_tiltangle.read(maxage)

        if Angle <= -7.5:
            Lambda = 9.70 - (3.9536 * (10**-4) * I + 5.2364 * (10**-9) *(I**2))
        else:
            Lambda = 14.58 - 0.00057182 * I + 7.5893 * (10**-9) * (I**2)
        return float(Lambda)

    def doStatus(self, maxage=0):
        return status.OK, ''
