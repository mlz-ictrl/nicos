# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core.params import Param
from nicos.devices.vendor.astrium import SelectorLambda as _SelectorLambda


class SelectorLambda(_SelectorLambda):

    parameters = {
        'delta': Param('Maximum deviation between requested rpm and limits',
                       unit='rpm', default=10)
    }

    def _adjustValue(self, value):
        speed = int(self._constant() / value)
        amin, amax = self._attached_seldev.abslimits
        if speed > amax and (speed - amax) <= self.delta:
            value = self._constant() / amax
        elif speed < amin and (amin - speed) <= self.delta:
            value = self._constant() / amin
        return value

    def doStart(self, value):
        return _SelectorLambda.doStart(self, self._adjustValue(value))

    def doIsAllowed(self, value):
        return _SelectorLambda.doIsAllowed(self, self._adjustValue(value))
