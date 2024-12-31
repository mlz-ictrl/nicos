# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Attach, Readable, status
from nicos.core.params import Param
from nicos.devices.entangle import VectorInput


class D8(Readable):

    hardware_access = False

    register_mapping = {
        # (register index, bit number, bit_value): msg_txt
        (0, 0, True): 'X-Ray Generator alarm pending',
        (0, 1, True): 'Goniometer not mounted',
        (0, 2, True): 'Rear panel not mounted',
        # ignore this error, as it will always be present when the generator is
        # off
        # (0, 4, False): 'X-Ray display faulty',
        (0, 7, False): 'Right door switches faulty',
        (1, 0, False): 'Left door switches faulty',
        (1, 1, False): 'Tube window switches faulty',
        (1, 2, False): 'Tube window open dispaly faulty',
        (1, 3, False): 'X-Ray on display faulty',
        (2, 0, True): 'Primary optics not mounted',
        (2, 1, True): 'Tube mount not mounted',
    }

    attached_devices = {
        'registers': Attach('Access to D8 registers', VectorInput),
    }

    parameters = {
        'ldoor': Param('Status of the left door', type=str, volatile=True),
        'rdoor': Param('Status of the right door', type=str, volatile=True),
    }

    def _reg(self, maxage=0):
        return list(map(int, self._attached_registers.read(maxage)))

    def doRead(self, maxage=0):
        return ','.join(self._errors(maxage))

    def _errors(self, maxage=0):
        reg = self._reg(maxage)
        s = []
        for key, msg in self.register_mapping.items():
            idx, bit, val = key
            if bool(reg[idx] & (1 << bit)) == val:
                s.append(msg)
        return s

    def doReadLdoor(self):
        reg = self._reg()
        if reg[2] & (1 << 3) > 0:
            return 'locked'
        elif reg[1] & (1 << 5) == 0:
            return 'closed'
        return 'open'

    def doReadRdoor(self):
        reg = self._reg()
        if reg[2] & (1 << 2) > 0:
            return 'locked'
        elif reg[1] & (1 << 4) == 0:
            return 'closed'
        return 'open'

    def doStatus(self, maxage=0):
        er = self._errors(maxage)
        if len(er) > 0:
            return status.ERROR, 'components faulty: %s' % er
        return status.OK, 'idle'

    def doPoll(self, n, maxage):
        self._pollParam('ldoor', 1)
        self._pollParam('rdoor', 1)
