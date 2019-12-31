#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, IsController, Moveable, Override, status
from nicos.core.errors import LimitError
from nicos.core.mixins import HasLimits
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep
from nicos.pycompat import number_types


class SeqSampleMotor(SeqDev):
    """Special SeqDev item for the sample changer motor."""

    def check(self):
        if isinstance(self, HasLimits):
            limits = self.dev.userlimits
            if isinstance(self.target, number_types):
                if not limits[0] <= self.target <= limits[1]:
                    raise LimitError(self.dev, 'limits are [%s, %s]' % limits)
        if hasattr(self, 'doIsAllowed'):
            res = self.doIsAllowed(self.target)
            if not res[0]:
                raise LimitError(self.dev, res[1])


class SampleChanger(IsController, BaseSequencer):
    """The PGAA sample changer device."""

    attached_devices = {
        'motor': Attach('Stage rotation', Moveable),
        'push': Attach('Moving sample to rotation stage', Moveable),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%.f'),
    }

    def isAdevTargetAllowed(self, dev, target):
        if dev == self._attached_motor:
            if not self._attached_push._attached_sensort.read(0):
                return False, '"push" is not in top position or moving'
        elif dev == self._attached_push:
            if self._attached_motor.status(0)[0] == status.BUSY:
                return False, 'motor moving'
            if self._attached_motor.read(0) not in (1., 2., 3., 4., 5., 6., 7.,
                                                    8., 9., 10., 11., 12., 13.,
                                                    14., 15., 16.):
                return False, 'invalid motor position'
        return True, ''

    def _generateSequence(self, target):
        seq = []
        if target != self.doRead(0):
            seq.append(SeqDev(self._attached_push, 'up', stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqSampleMotor(self._attached_motor, target,
                                      stoppable=False))
            seq.append(SeqSleep(2))
            seq.append(SeqDev(self._attached_push, 'down', stoppable=False))
        return seq

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage)
