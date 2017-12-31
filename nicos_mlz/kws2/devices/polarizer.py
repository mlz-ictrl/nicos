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

"""Class for controlling the KWS2 polarizer."""

from nicos.core import Moveable, Readable, Param, Override, Attach, \
    HasTimeout, status, oneof, listof

POL_SETTINGS = ['out', 'up', 'down']


class Polarizer(HasTimeout, Moveable):
    """Controls both the position of the polarizer and the spin flipper.
    """

    valuetype = oneof(*POL_SETTINGS)

    hardware_access = True

    attached_devices = {
        'output':    Attach('output setter', Moveable),
        'input_in':  Attach('input for limit switch "in" position', Readable),
        'input_out': Attach('input for limit switch "out" position', Readable),
        'flipper':   Attach('3He flipper', Moveable),
    }

    parameter_overrides = {
        'fmtstr':    Override(default='%s'),
        'timeout':   Override(default=10),
        'unit':      Override(mandatory=False, default=''),
    }

    parameters = {
        'values':   Param('Possible values (for GUI)', userparam=False,
                          type=listof(str), default=POL_SETTINGS),
    }

    def doStatus(self, maxage=0):
        is_in = self._attached_input_in.read(maxage)
        is_out = self._attached_input_out.read(maxage)
        # check individual bits
        if is_in ^ is_out != 3:
            # inconsistent state, check switches
            if ((is_in & 2) and (is_out & 2)) or \
               ((is_in & 1) and (is_out & 1)):
                # both switches on?
                return status.ERROR, 'both switches on for element(s)'
            return status.BUSY, 'elements moving'
        # HasTimeout will check for target reached
        return self._attached_flipper.status(maxage)

    def doRead(self, maxage=0):
        is_in = self._attached_input_in.read(maxage)
        if is_in == 3:
            return self._attached_flipper.read()
        elif is_in > 0:
            return 'inconsistent'
        return 'out'

    def doStart(self, target):
        if target == 'out':
            self._attached_output.start(0)
        else:
            self._attached_output.start(3)
            self._attached_flipper.start(target)
