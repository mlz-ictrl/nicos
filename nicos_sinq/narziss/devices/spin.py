# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Moveable, Param
from nicos.core.errors import ProgrammingError
from nicos.core.params import Attach, oneof
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class NarzissSpin(BaseSequencer):
    parameters = {
        'spinup_field': Param('Magnetic field value for spin-up state holding',
                         type=float,
                         default=0.04, userparam=True, settable=True),
        'spindown_field': Param('Magnetic field value for spin-down state holding',
                         type=float,
                         default=1.0, userparam=True, settable=True),
	}

    attached_devices = {
        'pom': Attach('Polariser rotation', Moveable),
        'pmag': Attach('Polariser magnet', Moveable),
    }

    valuetype = oneof('+', '-', '0', 'undefined')

    def _generateSequence(self, target):
        seq = []

        if target == '+':
            seq.append((SeqDev(self._attached_pom, 0.8),
                       SeqDev(self._attached_pmag, -2.5)))
            seq.append(SeqSleep(2.))
            seq.append(SeqDev(self._attached_pmag, self.spinup_field))
            seq.append(SeqSleep(2.))
            seq.append(SeqDev(self._attached_pmag, self.spinup_field))
        elif target == '-':
            seq.append((SeqDev(self._attached_pom, 0.8),
                       SeqDev(self._attached_pmag, 2.5)))
            seq.append(SeqSleep(2.))
            seq.append(SeqDev(self._attached_pmag, self.spindown_field))
            seq.append(SeqSleep(2.))
            seq.append(SeqDev(self._attached_pmag, self.spindown_field))
        elif target == '0':
            seq.append((SeqDev(self._attached_pom, 3),
                       SeqDev(self._attached_pmag, 0)))
        else:
            raise ProgrammingError('Invalid value requested')

        return seq

    def doRead(self, maxage=0):
        val = self._attached_pmag.read(maxage)
        if abs(val - self.spinup_field) < .02:
            return '+'
        if abs(val - self.spindown_field) < .05:
            return '-'
        if abs(val) < .05:
            return '0'
        return 'undefined'
