#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#
# *****************************************************************************

from nicos.core import Moveable, Override
from nicos.core.params import Attach
from nicos.devices.tango import PowerSupply


class Toellner(PowerSupply):

    attached_devices = {
        'polchange': Attach('TANGO digital input device ', Moveable),
    }

    parameter_overrides = {
        'precision':  Override(default=0.1),
        'timeout':    Override(default=4),
    }

    def _getsign(self):
        return -1 if self._attached_polchange.read() == '-' else 1

    def _set_field_polarity(self, value):
        polval = self._attached_polchange.read()
        return (value < 0 and polval == '+') or (value >= 0 and polval == '-')

    def doStart(self, value):
        polval = self._attached_polchange.read()
        target = self.target
        if self._set_field_polarity(value):
            polval = '-' if value < 0 else '+'
            self._setROParam('target', 0)
            self._dev.value = 0
            self._attached_polchange.start(polval)
        self._setROParam('target', target)
        self._dev.value = abs(value)

    def doRead(self, maxage=0):
        return self._dev.value * self._getsign()
