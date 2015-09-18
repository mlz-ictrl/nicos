#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for MIRA beam elements."""

from nicos.core import HasTimeout, Moveable, Readable, Attach, oneof, \
    multiReset, Override, status


class BeamElement(HasTimeout, Moveable):
    """
    Class for readout of the MIRA shutter via digital input card, and closing
    the shutter via digital output (tied into Pilz security system).
    """

    valuetype = oneof('in', 'out')

    attached_devices = {
        'valve':      Attach('in/out pressure valve', Moveable),
        'switch_in':  Attach('limit switch for "in" position', Readable),
        'switch_out': Attach('limit switch for "out" position', Readable),
    }

    parameter_overrides = {
        'timeout':    Override(default=10),
        'unit':       Override(mandatory=False, default=''),
    }

    def doStatus(self, maxage=0):
        is_in = self._adevs['switch_in'].read(maxage)
        is_out = self._adevs['switch_out'].read(maxage)
        valvepos = self._adevs['valve'].read(maxage)
        if (is_in and valvepos == 'in') or (is_out and valvepos == 'out'):
            return status.OK, 'idle'
        return status.BUSY, 'moving'

    def doRead(self, maxage=0):
        return self._adevs['valve'].read(maxage)

    def doStart(self, target):
        self._adevs['valve'].start(target)

    def doReset(self):
        multiReset(self._adevs)
