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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for kompass primary beamstop"""


from nicos.core import Attach, Param, Moveable, tupleof, anytype, limits
from nicos.devices.generic.sequence import BaseSequencer, SeqDev


class SttWithPBS(BaseSequencer, Moveable):
    valuetype = float

    attached_devices = {
        'pbs': Attach('primary beamstop', Moveable),
        'stt': Attach('axis of stt', Moveable),
    }

    parameters = {
        # XXX: rename (too much similarity to user/abslimits)
        'limits':     Param('Range with a lowered pbs', type=limits,
                            settable=False, default=(-21, 21)),
        'pbs_values': Param('Values for the pbs for down, up',
                            type=tupleof(anytype, anytype),
                            settable=False, default=('down', 'up')),
    }

    def doRead(self, maxage=0):
        return self._attached_stt.read(maxage)

    def doIsAllowed(self, target):
        return self._attached_stt.isAllowed(target)

    def _generateSequence(self, target):
        curpos = self.read(0)
        seq = []
        pbs_down, pbs_up = self.pbs_values
        # handle all 9 cases
        if curpos < self.limits[0]:
            if target >= self.limits[0]:
                seq.append(SeqDev(self._attached_stt, self.limits[0], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_down))
            if target > self.limits[1]:
                seq.append(SeqDev(self._attached_stt, self.limits[1], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_up))
            seq.append(SeqDev(self._attached_stt, target, stoppable=True))
        elif curpos <= self.limits[1]:
            if target < self.limits[0]:
                seq.append(SeqDev(self._attached_stt, self.limits[0], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_up))
            if target > self.limits[1]:
                seq.append(SeqDev(self._attached_stt, self.limits[1], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_up))
            seq.append(SeqDev(self._attached_stt, target, stoppable=True))
        else:  # curpos > self.limits[1]:
            if target <= self.limits[1]:
                seq.append(SeqDev(self._attached_stt, self.limits[1], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_down))
            if target < self.limits[0]:
                seq.append(SeqDev(self._attached_stt, self.limits[0], stoppable=True))
                seq.append(SeqDev(self._attached_pbs, pbs_up))
            seq.append(SeqDev(self._attached_stt, target, stoppable=True))
        return seq
