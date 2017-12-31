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

"""Class for controlling lenses."""

from nicos.core import HasTimeout, Moveable, Readable, Param, Attach, oneof, \
    listof, intrange, Override, status


LENS_CONFIGS = ['%s-%s-%s' % (l1, l2, l3)
                for l1 in ('out', 'in')
                for l2 in ('out', 'in')
                for l3 in ('out', 'in')]


class Lenses(Moveable):
    """High-level lens control."""

    valuetype = oneof(*LENS_CONFIGS)

    hardware_access = False

    attached_devices = {
        'io':  Attach('Lens I/O device', Moveable),
    }

    parameters = {
        'values': Param('Possible values (for GUI)', userparam=False,
                        type=listof(str), default=LENS_CONFIGS),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%s'),
        'unit':       Override(mandatory=False, default=''),
    }

    def doRead(self, maxage=0):
        lens_read = int(self._attached_io.read(maxage))
        configs = [('in' if lens_read & (1 << i) else 'out')
                   for i in range(3)]
        return '-'.join(configs)

    def doStart(self, target):
        configs = [(v == 'in') for v in target.split('-')]
        bits = configs[0] + 2 * configs[1] + 4 * configs[2]
        self._attached_io.start(bits)


class LensControl(HasTimeout, Moveable):
    """Control the 3 lenses."""

    valuetype = intrange(0, 7)

    attached_devices = {
        'output':    Attach('output setter', Moveable),
        'input_in':  Attach('input for limit switch "in" position', Readable),
        'input_out': Attach('input for limit switch "out" position', Readable),
        'sync_bit':  Attach('sync bit output', Moveable),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%d'),
        'timeout':    Override(default=10),
        'unit':       Override(mandatory=False, default=''),
    }

    def doStatus(self, maxage=0):
        is_in = self._attached_input_in.read(maxage)
        is_out = self._attached_input_out.read(maxage)
        # check individual bits
        for i in range(3):
            mask = 1 << i
            if is_in & mask == is_out & mask:
                # inconsistent state, check switches
                if is_in & mask:
                    # both switches on?
                    return status.ERROR, 'both switches on for lens ' \
                        '%d' % (i + 1)
                return status.BUSY, 'lenses moving'
        # HasTimeout will check for target reached
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        return self._attached_input_in.read(maxage)

    def doStart(self, target):
        self._attached_output.start(target)
        # without this bit, no outputs will be changed
        self._attached_sync_bit.start(1)
