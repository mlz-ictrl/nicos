#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Device for the Dimetix distance laser sensor."""

from nicos.core import Attach, Override, Param, Readable
from nicos.core.mixins import CanDisable, HasOffset
from nicos.core.params import floatrange, intrange


class DimetixLaser(CanDisable, HasOffset, Readable):

    attached_devices = {
        'signal': Attach('signal strength device', Readable),
        'value': Attach('value device', Readable),
    }

    parameter_overrides = {
        'unit': Override(volatile=True, mandatory=False),
    }

    parameters = {
        'signallimit': Param('minimal signal strength for valid reading',
                             type=floatrange(0.), default=8000),
        'invalidvalue': Param('value to indicate invalid value',
                              type=intrange(-2000, -2000), default=-2000),
    }

    def doRead(self, maxage=0):
        if self._attached_signal.read(maxage) < self.signallimit:
            return self.invalidvalue
        return self._attached_value.read(maxage)

    def doReadUnit(self):
        return self._attached_value.unit

    def doPoll(self, n, maxage):
        self._attached_signal.poll(n, maxage)
        self._attached_signal.poll(n, maxage)
