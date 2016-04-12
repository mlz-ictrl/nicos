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

"""Class for controlling the collimation."""

from nicos.core import HasTimeout, Moveable, Readable, Attach, Override, \
    status, intrange, dictof, listof, tupleof, oneof, HasLimits, Param, \
    PositionError, ConfigurationError
from nicos.devices.generic.slit import TwoAxisSlit
from nicos.devices.tango import Motor as TangoMotor


class SlitMotor(TangoMotor):
    """Overridden motor to round off the read values from the slit motors,
    because they use resolvers and change on every read.
    """

    def doRead(self, maxage=0):
        value = TangoMotor.doRead(self, maxage)
        return round(value, 1)


class CollimationSlit(TwoAxisSlit):
    """Two-axis slit with an additional parameter for the "open" position."""

    parameters = {
        'openpos':   Param('position to move slit completely open',
                           type=tupleof(float, float), default=(50.0, 50.0)),
    }

    parameter_overrides = {
        'fmtstr':    Override(default='%.1f x %.1f'),
    }


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


class Collimation(Moveable):
    """Controlling the collimation guides and slits together."""

    hardware_access = False

    attached_devices = {
        'guides':  Attach('guides', Moveable),
        'slits':   Attach('slit devices', CollimationSlit, multiple=True),
    }

    parameters = {
        'slitpos': Param('positions of the attached slits', unit='m',
                         type=listof(int), mandatory=True),
        'mapping': Param('maps position name to guide and slit w/h',
                         type=dictof(str, tupleof(int, float, float)),
                         mandatory=True),
    }

    parameter_overrides = {
        'fmtstr':  Override(default='%s'),
        'unit':    Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        self.valuetype = oneof(*self.mapping)
        if len(self._attached_slits) != len(self.slitpos):
            raise ConfigurationError(self, 'number of elements in slitpos '
                                     'parameter must match number of attached '
                                     'slit devices')

    def doRead(self, maxage=0):
        def matches(v1, v2):
            return abs(v1 - v2) < 1.0

        guidelen = self._attached_guides.read(maxage)
        if guidelen not in self.slitpos:
            raise PositionError(self, 'collimation length %d m not at slit '
                                'position' % guidelen)
        slitvals = [slit.read(maxage) for slit in self._attached_slits]
        for (posname, (pos_guidelen, pos_w, pos_h)) in self.mapping.items():
            if pos_guidelen != guidelen:
                continue
            ok = True
            for (slitpos, slit, (w, h)) in zip(self.slitpos,
                                               self._attached_slits, slitvals):
                if slitpos == pos_guidelen:
                    ok &= matches(w, pos_w) and matches(h, pos_h)
                else:
                    ok &= matches(w, slit.openpos[0]) and \
                        matches(h, slit.openpos[1])
            if ok:
                return posname

        raise PositionError(self, 'current slit position is not a preset for '
                            'collimation length %d m' % guidelen)

    def doStart(self, target):
        pos_guidelen, pos_w, pos_h = self.mapping[target]
        self._attached_guides.start(pos_guidelen)
        for (slitpos, slit) in zip(self.slitpos, self._attached_slits):
            if slitpos == pos_guidelen:
                slit.start((pos_w, pos_h))
            else:
                slit.start(slit.openpos)
