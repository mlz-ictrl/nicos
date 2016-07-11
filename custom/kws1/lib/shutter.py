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

"""Class for controlling the KWS shutter."""

from nicos.core import HasTimeout, Moveable, Readable, Attach, Override, \
    status, oneof

# TODO: check if this can be a FZJDP BioShutter device!

READ_CLOSED = 1
READ_OPEN = 2
WRITE_CLOSED = 1
WRITE_OPEN = 7


class Shutter(HasTimeout, Moveable):
    """Controlling the shutter."""

    valuetype = oneof('closed', 'open')

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
        if inputstatus == READ_OPEN:
            if self.target == 'open':
                return status.OK, 'idle'
            else:
                return status.WARN, 'open, but target=closed'
        elif inputstatus == READ_CLOSED:
            if self.target == 'closed':
                return status.OK, 'idle'
            else:
                return status.WARN, 'closed, but target=open'
        # HasTimeout will check for target reached
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        inputstatus = self._attached_input.read(maxage)
        if inputstatus == READ_OPEN:
            return 'open'
        elif inputstatus == READ_CLOSED:
            return 'closed'
        return 'unknown'

    def doStart(self, target):
        if target == 'open':
            self._attached_output.start(WRITE_OPEN)
        else:
            self._attached_output.start(WRITE_CLOSED)
