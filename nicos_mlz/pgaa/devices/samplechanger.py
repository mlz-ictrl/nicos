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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""Class for the sample changer."""

from __future__ import absolute_import, division, print_function

from nicos.core import Attach, Moveable, Override
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep


class SampleChanger(BaseSequencer):
    """The PGAA sample changer device."""

    attached_devices = {
        'motor': Attach('Stage rotation', Moveable),
        'push': Attach('Moving sample to rotation stage', Moveable),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%.f'),
    }

    def _generateSequence(self, target):
        seq = []
        if target != self.doRead(0):
            seq.append(SeqDev(self._attached_push, 'up', stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqDev(self._attached_motor, target, stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqDev(self._attached_push, 'down', stoppable=False))
        return seq

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage)
