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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Class for controlling the collimation."""

from nicos.core import HasTimeout, Moveable, Readable, Attach, Override, \
    status, intrange, listof, HasLimits, Param
from nicos.devices.generic.slit import TwoAxisSlit


class CollimationGuides(HasTimeout, HasLimits, Moveable):
    """Controlling the collimation guide elements."""

    valuetype = intrange(2, 20)

    attached_devices = {
        'output':    Attach('output setter', Moveable),
        'input_in':  Attach('input for limit switch "in" position', Readable),
        'input_out': Attach('input for limit switch "out" position', Readable),
        'sync_bit':  Attach('sync bit output', Moveable),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%d'),
        'timeout':    Override(default=10),
        'unit':       Override(mandatory=False, default='m'),
        'abslimits':  Override(mandatory=False, default=(2, 20)),
    }

    def doStatus(self, maxage=0):
        # XXX: overlap with lenses
        is_in = self._attached_input_in.read(maxage)
        is_out = self._attached_input_out.read(maxage)
        # check individual bits
        for i in range(18):
            mask = 1 << i
            if is_in & mask == is_out & mask:
                # inconsistent state, check switches
                if is_in & mask:
                    # both switches on?
                    return status.ERROR, 'both switches on for element ' \
                        'at %d m' % (i + 2)
                return status.BUSY, 'elements moving'
        # HasTimeout will check for target reached
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        is_in = self._attached_input_in.read(maxage)
        # extract the lowest set bit (element)
        for i in range(18):
            if is_in & (1 << i):
                return i + 2
        return 20

    def doStart(self, target):
        # there are 18 bits for the collimation elements at 2..19 meters
        # bit 0 is the element at 2m, bit 17 is at 19m
        # move in all elements from 19m to target (20m = all open)
        bits = ((1 << (20 - target)) - 1) << (target - 2)
        self._attached_output.start(bits)
        # without this bit, no outputs will be changed
        self._attached_sync_bit.start(1)


class CollimationSlits(HasTimeout, HasLimits, Moveable):
    """Controlling the collimation slits."""

    valuetype = intrange(2, 20)

    attached_devices = {
        'slits': Attach('slit devices', TwoAxisSlit, multiple=True),
    }

    parameters = {
        'slitpositions': Param('positions of the attached slits',
                               type=listof(float), mandatory=True),
        'openpos': Param('position for "slit open"', default=43.0,
                         settable=True),
    }

    def doRead(self, maxage=0):
        for _i in range(len(self.slitpositions)):
            # XXX unfinished
            pass
