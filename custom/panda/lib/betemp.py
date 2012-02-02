#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""PANDA Beryllium filter readout."""

__version__ = "$Revision$"

from nicos.core import Param, Override, status, none_or, oneof
from nicos.taco import AnalogInput


class I7033Temp(AnalogInput):

    taco_class = AnalogInput

    parameters = {
        'warnlevel': Param('temperature that should not be exceeded',
                           type=none_or(float), settable=True),
    }

    parameter_overrides = {
        'unit': Override(type=oneof('K', 'Ohm')),
    }

    def doReadUnit(self):
        return 'K'

    def doRead(self):
        r = self._taco_guard(self._dev.read)
        t = self._temperature(r)
        if self.unit == 'K':
            return t
        return r

    def doStatus(self):
        t = self._temperature(self._taco_guard(self._dev.read))
        if self.warnlevel and t > self.warnlevel:
            return (status.ERROR, 'filter temperature (%6.1f K) too high' % t)
        return (status.OK, '')

    def _temperature(self, r):
        return (r - 1000) / 3.85 + 273.25  # linear approx.
