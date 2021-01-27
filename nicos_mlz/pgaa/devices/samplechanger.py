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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""Class for the sample changer."""

from nicos.core import Attach, IsController, Moveable, Override, Param, status
from nicos.core.errors import LimitError
from nicos.core.mixins import HasLimits
from nicos.core.params import floatrange, intrange
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqSleep
from nicos.utils import number_types


class SeqSampleMotor(SeqDev):
    """Special SeqDev item for the sample changer motor."""

    def check(self):
        if isinstance(self.dev, HasLimits):
            limits = self.dev.userlimits
            if isinstance(self.target, number_types):
                if not limits[0] <= self.target <= limits[1]:
                    raise LimitError(self.dev, 'limits are [%s, %s]' % limits)
        if hasattr(self.dev, 'doIsAllowed'):
            allowed, remark = self.dev.doIsAllowed(self.target)
            if not allowed:
                raise LimitError(self.dev, remark)


class SampleChanger(IsController, BaseSequencer):
    """The PGAA sample changer device."""

    hardware_access = False

    valuetype = intrange(1, 16)

    attached_devices = {
        'motor': Attach('Stage rotation', Moveable),
        'push': Attach('Moving sample to rotation stage', Moveable),
    }

    parameters = {
        'delay': Param('Time to wait until the push device is finished',
                       type=floatrange(0, 2), default=2, settable=False,
                       unit='s'),
    }

    parameter_overrides = {
        'unit': Override(default=''),
        'fmtstr': Override(default='%.0f'),
    }

    def isAdevTargetAllowed(self, dev, target):
        if dev == self._attached_motor:
            if self._attached_push._attached_sensort.read(0) in ['down', 0]:
                return False, '"push" is not in top position or moving'
        elif dev == self._attached_push:
            if self._attached_motor.status(0)[0] == status.BUSY:
                return False, 'motor moving'
            if self._attached_motor.read(0) not in list(range(1, 17)):
                return False, 'invalid motor position'
        return True, ''

    def _generateSequence(self, target):
        seq = []
        if target != self.doRead(0):
            seq.append(SeqDev(self._attached_push, 'up', stoppable=False))
            seq.append(SeqSleep(self.delay))
            seq.append(SeqSampleMotor(self._attached_motor, target,
                                      stoppable=False))
            seq.append(SeqSleep(self.delay))
            seq.append(SeqDev(self._attached_push, 'down', stoppable=False))
        return seq

    def doRead(self, maxage=0):
        return round(self._attached_motor.read(maxage))
