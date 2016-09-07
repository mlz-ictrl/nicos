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
#   Aleks Wischolit <aleks.wischolit@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Readable, Override, Attach, status

class tauTwoarms(Readable):

    attached_devices = {
        'current': Attach('NSE', Readable),
        'frequency': Attach('NRSE', Readable),
        'fu0': Attach('Compare', Readable),
        'wavelength': Attach('Calculation', Readable)
    }


    parameter_overrides = {
        'unit':  Override(mandatory=False, default='ns'),
    }

    def doRead(self, maxage=0):

        b22 = self._attached_current.read(maxage)
        f0 = self._attached_frequency.read(maxage)
        fu0 = self._attached_fu0.read(maxage)
        lam = self._attached_wavelength.read(maxage)

        if fu0 <= 0.05:
            tau = 2.6196 * (10**(-4)) * b22 *(lam**3)
        else:
            tau = 3.9806 * (10**(-8)) * f0 * (lam**3)

        return tau


    def doStatus(self, maxage=0):
        return status.OK, ''




class tauMieze(Readable):

    attached_devices = {
        'length': Attach('Readed from cache', Readable),
        'frequency0': Attach('Calculation', Readable),
        'frequency1': Attach('Calculation', Readable),
        'wavelength': Attach('Calculation', Readable)
    }


    parameter_overrides = {
        'unit':  Override(mandatory=False, default='ns'),
    }

    def doRead(self, maxage=0):

        l = self._attached_length.read(maxage)
        f0 = self._attached_frequency0.read(maxage)
        f1 = self._attached_frequency1.read(maxage)
        lam = self._attached_wavelength.read(maxage)

        tau = 1.278 * (10**(-8)) * (f0-f1) * l * (lam**3)
        if tau < 0:
            tau = -tau

        return tau


    def doStatus(self, maxage=0):
        return status.OK, ''
