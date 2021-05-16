#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""Combination devices for KWS 3."""

from nicos.core import Attach, Moveable, Override, tupleof


class Mirror(Moveable):
    """Combination device for the mirror axes."""

    valuetype = tupleof(float, float, float)

    attached_devices = {
        'x': Attach('X motor', Moveable),
        'y': Attach('Y motor', Moveable),
        'tilt': Attach('Tilt motor', Moveable),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default='mm'),
        'fmtstr': Override(default='%.0f, %.0f, %.1f'),
    }

    def doRead(self, maxage=0):
        return (self._attached_x.read(maxage),
                self._attached_y.read(maxage),
                self._attached_tilt.read(maxage))

    def doIsAllowed(self, pos):
        for (i, name, dev) in [(0, 'x', self._attached_x),
                               (1, 'y', self._attached_y),
                               (2, 'tilt', self._attached_tilt)]:
            ok, why = dev.isAllowed(pos[i])
            if not ok:
                return False, name + ': ' + why
        return True, ''

    def doStart(self, pos):
        self._attached_x.start(pos[0])
        self._attached_y.start(pos[1])
        self._attached_tilt.start(pos[2])


class Detector(Moveable):
    """Combination device for the detector axes."""

    valuetype = tupleof(float, float, float)

    attached_devices = {
        'x': Attach('X motor', Moveable),
        'y': Attach('Y motor', Moveable),
        'z': Attach('Z motor', Moveable),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False, default='mm'),
        'fmtstr': Override(default='%.1f, %.2f, %.0f'),
    }

    def doRead(self, maxage=0):
        return (self._attached_x.read(maxage),
                self._attached_y.read(maxage),
                self._attached_z.read(maxage))

    def doIsAllowed(self, pos):
        for (i, name, dev) in [(0, 'x', self._attached_x),
                               (1, 'y', self._attached_y),
                               (2, 'z', self._attached_z)]:
            ok, why = dev.isAllowed(pos[i])
            if not ok:
                return False, name + ': ' + why
        return True, ''

    def doStart(self, pos):
        self._attached_x.start(pos[0])
        self._attached_y.start(pos[1])
        self._attached_z.start(pos[2])
