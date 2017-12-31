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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Beamstop switcher for KWS 3."""

from nicos.core import Param, oneof, dictof, anytype, MoveError, Moveable, \
    Override, Attach, HasPrecision, status
from nicos.devices.generic import MultiSwitcher


class Resolution(MultiSwitcher):
    """Switcher for the resolution."""

    parameters = {
        'presets': Param('Available presets', type=dictof(anytype, anytype)),
    }


class Beamstop(Moveable):
    """Switcher for the beamstop position.

    This switches the beamstop in or out; the "out" value is determined by
    the current resolution preset.
    """

    valuetype = oneof('out', 'in')

    attached_devices = {
        'moveable':   Attach('Beamstop motor', HasPrecision),
        'resolution': Attach('Resolution device', Resolution),
    }

    parameters = {
        'outpos': Param('Position for "out"'),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default=''),
    }

    def doRead(self, maxage=0):
        movpos = self._attached_moveable.read(maxage)
        if abs(movpos - self.outpos) <= self._attached_moveable.precision:
            return 'out'
        respos = self._attached_resolution.read(maxage)
        if respos != 'unknown':
            inpos = self._attached_resolution.presets[respos]['beamstop_x_in']
            if abs(movpos - inpos) <= self._attached_moveable.precision:
                return 'in'
        return 'unknown'

    def doStatus(self, maxage=0):
        code, text = Moveable.doStatus(self, maxage)
        if code == status.OK and self.read(maxage) == 'unknown':
            return status.NOTREACHED, 'unknown position'
        return code, text

    def _getWaiters(self):
        return [self._attached_moveable]

    def doStart(self, pos):
        if pos == 'out':
            self._attached_moveable.start(self.outpos)
            return
        respos = self._attached_resolution.target
        if respos != 'unknown':
            inpos = self._attached_resolution.presets[respos]['beamstop_x_in']
            self._attached_moveable.start(inpos)
        else:
            raise MoveError('no position for beamstop, resolution is unknown')
