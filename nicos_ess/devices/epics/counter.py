#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
from collections.abc import Iterable

from nicos.core import Override, Param, Value, oneof, status
from nicos.devices.epics.pva import EpicsReadable
from nicos.devices.generic import CounterChannelMixin, PassiveChannel


class EpicsCounter(CounterChannelMixin, EpicsReadable, PassiveChannel):
    """Counter channel that sums the values of a PV as it changes."""

    parameters = {
        'total':
            Param('The total amount summed so far',
                  type=float,
                  settable=True,
                  internal=True),
        'started':
            Param('Whether a collection is in progress',
                  type=bool,
                  settable=True,
                  default=False,
                  internal=True),
    }

    parameter_overrides = {
        # Must run in monitor mode
        'monitor': Override(default=True, settable=False, type=oneof(True)),
        'type': Override(default='counter', settable=False, mandatory=False),
    }

    def value_change_callback(self, name, param, value, units, severity,
                              message, **kwargs):
        if self.started:
            value = sum(value) if isinstance(value, Iterable) else value
            self._setROParam('total', self.total + value)

    def doStart(self):
        self.total = 0
        self.started = True

    def doFinish(self):
        self.started = False

    def doStop(self):
        self.started = False

    def doStatus(self, maxage=0):
        if self.started:
            return status.BUSY, 'counting'
        return status.OK, ''

    def doRead(self, maxage=0):
        return self.total

    def valueInfo(self):
        return Value(self.name, unit=self.unit, fmtstr=self.fmtstr),
