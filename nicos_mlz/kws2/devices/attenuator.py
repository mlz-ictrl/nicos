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

"""Class for controlling the KWS2 attenuator."""

from nicos.core import HasTimeout, Moveable, Readable, Attach, Override, \
    status, oneof

OUT = 1
IN = 2


class Attenuator(HasTimeout, Moveable):
    """Controlling the attenuator."""

    valuetype = oneof('out', 'in')

    attached_devices = {
        'output':    Attach('output bits', Moveable),
        'input':     Attach('input bits', Readable),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='%s'),
        'timeout':    Override(default=10),
        'unit':       Override(mandatory=False, default=''),
    }

    def doStatus(self, maxage=0):
        inputstatus = self._attached_input.read(maxage)
        if inputstatus == OUT:
            if self.target == 'out':
                return status.OK, 'idle'
            else:
                return status.WARN, 'out, but target=in'
        elif inputstatus == IN:
            if self.target == 'in':
                return status.OK, 'idle'
            else:
                return status.WARN, 'in, but target=out'
        # HasTimeout will check for target reached
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        inputstatus = self._attached_input.read(maxage)
        if inputstatus == OUT:
            return 'out'
        elif inputstatus == IN:
            return 'in'
        return 'unknown'

    def doStart(self, target):
        if target == 'out':
            self._attached_output.start(OUT)
        else:
            self._attached_output.start(IN)
