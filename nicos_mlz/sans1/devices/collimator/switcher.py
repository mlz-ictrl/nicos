# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

"""Switcher for the SANS-1 collimation system."""

from nicos.core import Override, PositionError
from nicos.devices.generic import Switcher as BaseSwitcher


class Switcher(BaseSwitcher):
    """Switcher, specially adapted to Sans1 needs"""
    parameter_overrides = {
        'precision':    Override(default=0.1, mandatory=False),
        'fallback':     Override(default='Unknown', mandatory=False),
        'blockingmove': Override(default=False, mandatory=False),
    }

    def _mapReadValue(self, value):
        """Override default inverse mapping to allow a deviation <= precision"""
        prec = self.precision

        def myiter(mapping):
            # use position names beginning with P as last option
            for name, value in mapping.items():
                if name[0] != 'P':
                    yield name, value
            for name, value in mapping.items():
                if name[0] == 'P':
                    yield name, value
        for name, pos in myiter(self.mapping):
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        if self.relax_mapping:
            return self._attached_moveable.format(value, True)
        raise PositionError(self, 'unknown position of %s' %
                            self._attached_moveable)
