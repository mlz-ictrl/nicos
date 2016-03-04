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

"""Class for KWS chopper control."""

from nicos.core import Moveable, Attach, Override, HasTimeout, tupleof, \
    floatrange


class Chopper(HasTimeout, Moveable):
    """Setting chopper parameters in terms of (frequency, phase)."""

    valuetype = tupleof(floatrange(0, 75), floatrange(0, 180))

    hardware_access = False

    attached_devices = {
        'motor1': Attach('The motor switch of the first chopper', Moveable),
        'motor2': Attach('The motor switch of the second chopper', Moveable),
        'freq1':  Attach('The frequency of the first chopper', Moveable),
        'freq2':  Attach('The frequency of the second chopper', Moveable),
        'phase1': Attach('The phase of the first chopper', Moveable),
        'phase2': Attach('The phase of the second chopper', Moveable),
    }

    parameter_overrides = {
        'fmtstr': Override(default='(%.1f, %.1f)'),
        'unit':   Override(mandatory=False, default=''),
    }

    def doStart(self, pos):
        if pos[0] == 0:
            self._attached_motor1.start(0)
            self._attached_motor2.start(0)
            return
        (freq, phase) = pos
        self._attached_freq1.start(freq)  # second chopper will set the same
        # calculate phases of the two choppers (they should be around 180deg)
        p0 = 90.0 - phase  # phase shift due to opening angle
        p1 = 180.0 - p0/2.0
        p2 = 180.0 + p0/2.0
        self._attached_phase1.start(p1)
        self._attached_phase2.start(p2)
        if self._attached_motor1.read(0) + self._attached_motor2.read(0) != 2:
            self._attached_motor1.start(1)
            self._attached_motor2.start(1)

    # doStatus provided by adevs is enough

    def doRead(self, maxage=0):
        if self._attached_motor1.read(maxage) == 0:
            return (0.0, 0.0)
        freq = self._attached_freq1.read(maxage)
        p1 = self._attached_phase1.read(maxage)
        p2 = self._attached_phase2.read(maxage)
        phase = 90.0 - (p2 - p1)
        return (freq, phase)
