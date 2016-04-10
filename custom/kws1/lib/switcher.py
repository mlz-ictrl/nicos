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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Switcher extensions for KWS."""

from nicos.core import Moveable, Attach, Param, Override, oneof, dictof, \
    dictwith, anytype
from nicos.devices.generic.switcher import MultiSwitcher


class SelectorSwitcher(MultiSwitcher):
    """Switcher whose mapping is determined by a list of presets."""

    parameters = {
        'presets':  Param('Presets that determine the mapping',
                          type=dictof(str, dictwith(lam=float, speed=float,
                                                    spread=float)),
                          mandatory=True),
    }


class DetectorPosSwitcher(MultiSwitcher):
    """Switcher for the detector position.

    This controls the X, Y and Z components of the detector position.  Presets
    depend on the target wavelength given by the selector.
    """

    parameters = {
        'presets':  Param('Presets that determine the mappings',
                          type=dictof(str, dictof(str, dictwith(
                              x=float, y=float, z=float))),
                          mandatory=True),
        'mappings': Param('Collection of mappings', userparam=False,
                          type=dictof(anytype, anytype))
    }

    parameter_overrides = {
        'mapping':  Override(mandatory=False, settable=True, userparam=False),
    }

    attached_devices = {
        'selector':  Attach('Selector preset device', Moveable),
    }

    def _determineMapping(self):
        sel_value = self._attached_selector.target
        return self.mappings.get(sel_value, {})

    def doUpdateMapping(self, newvalue):
        self.valuetype = oneof(*newvalue)

    def start(self, target):
        self.mapping = self._determineMapping()
        MultiSwitcher.start(self, target)

    def doPoll(self, i, maxage):
        # will use the correct mapping on the next polling cycle
        self._setROParam('mapping', self._determineMapping())
        self.doUpdateMapping(self.mapping)
