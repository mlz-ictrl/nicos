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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************


from nicos.core import Readable, status
from nicos.core.params import Attach, Param, anytype, floatrange, oneof
from nicos.devices.generic import BaseSequencer, Pulse
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class Shutter(BaseSequencer):

    hardware_access = False

    valuetype = oneof('closed', 'open')

    attached_devices = {
        'opener': Attach('Device to trigger shutter opening', Pulse),
        'closer': Attach('Device to trigger shutter closing', Pulse),
        'open_signal': Attach('Input to signal shutter is open', Readable),
        'closed_signal': Attach('Input to signal shutter is closed', Readable),
    }

    parameters = {
        'fullopening_time': Param('Time until the shutter is fully open',
                                  type=floatrange(1), unit='s', settable=True,
                                  userparam=False, default=60),
        'signal_value': Param('Value to indicate a signal is ON',
                              type=anytype, settable=False, userparam=False,
                              default=1),
    }

    def _generateSequence(self, target):
        if target == 'open':
            return [
                SeqDev(self._attached_opener, self._attached_opener.onvalue),
                SeqSleep(self.fullopening_time - self._attached_opener.ontime,
                         'wait until shutter is open')
            ]
        return [
            SeqDev(self._attached_closer, self._attached_closer.onvalue),
            SeqSleep(self.fullopening_time - self._attached_closer.ontime,
                     'wait until shutter is closed')
        ]

    def doStatus(self, maxage=0):
        stat, msg = BaseSequencer.doStatus(self, maxage)
        if stat == status.BUSY:
            return stat, msg
        if self._attached_closed_signal.read(maxage) == \
           self._attached_open_signal.read(maxage):
            return status.ERROR, f'Shutter neither {self.valuetype.vals[0]!r}' \
                f' nor {self.valuetype.vals[1]!r}'

    def doRead(self, maxage=0):
        if self._attached_closed_signal.read(maxage) == self.signal_value:
            return 'closed'
        if self.doStatus(maxage)[0] == status.BUSY:
            return 'intermediate'
        if self._attached_open_signal.read(maxage) == self.signal_value:
            return 'open'
        return 'error'
