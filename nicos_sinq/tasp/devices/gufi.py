# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos.core import Moveable
from nicos.core.errors import ProgrammingError
from nicos.core.params import Attach, Param, oneof
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class GuideField(BaseSequencer):
    """
    This is for controlling the TASP guide field. It has to be run
    to a high value and wait a little while in order to change the
    polarisation, then drive to a hold value.
    """

    attached_devices = {
        'magnet': Attach('Guide field magnet', Moveable),
    }

    parameters = {
        'hold_value': Param('Holding value', type=float, default=1.2,
                            settable=True),
    }

    valuetype = oneof('+', '-')

    def _generateSequence(self, target):
        seq = []

        if target == '+':
            seq.append((SeqDev(self._attached_magnet, 17.9)))
            seq.append(SeqSleep(1.))
            seq.append(SeqDev(self._attached_magnet, self.hold_value))
        elif target == '-':
            seq.append(SeqDev(self._attached_magnet, -17.9))
            seq.append(SeqSleep(1.))
            seq.append(SeqDev(self._attached_magnet, self.hold_value))
        else:
            raise ProgrammingError('Invalid value requested')

        return seq

    def doRead(self, maxage=0):
        # There is no way to read the polarisation
        return self.target
