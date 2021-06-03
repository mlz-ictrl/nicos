#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
from nicos.core.params import Attach, oneof
from nicos.devices.generic import BaseSequencer
from nicos.devices.generic.sequence import SeqDev, SeqSleep


class NarzissSpin(BaseSequencer):

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
            seq.append(SeqSleep(4.))
            seq.append(SeqDev(self._attached_pmag, .15))
        elif target == '-':
            seq.append((SeqDev(self._attached_pom, 0.8),
                       SeqDev(self._attached_pmag, 2.5)))
            seq.append(SeqSleep(4.))
            seq.append(SeqDev(self._attached_pmag, 1.))
        elif target == '0':
            seq.append((SeqDev(self._attached_pom, 3),
                       SeqDev(self._attached_pmag, 0)))
        else:
            raise ProgrammingError('Invalid value requested')

        return seq

    def doRead(self, maxage=0):
        val = self._attached_pmag.read(maxage)
        if abs(val - .15) < .02:
            return '+'
        if abs(val - 1.) < .05:
            return '-'
        if abs(val - 0) < .05:
            return '0'
        return 'undefined'
