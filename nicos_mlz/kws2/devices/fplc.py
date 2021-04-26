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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Support for measuring in-situ with the FPLC system."""

from time import time as currenttime, sleep

from nicos.core import Attach, HasTimeout, Moveable, Override, Param, \
    Readable, oneof, status, MASTER
from nicos.devices.tango import AnalogInput


class FPLCTrigger(HasTimeout, Moveable):
    """Trigger the FPLC flow and then wait for the sample to be
    ready inside the cell.

    Used as a sample environment device in kwscount().
    """

    valuetype = oneof('triggered', 'waiting')

    hardware_access = True

    attached_devices = {
        'output': Attach('start output to FPLC', Moveable),
        'input':  Attach('trigger input from FPLC', Readable),
    }

    parameters = {
        'started':   Param('Time when device was started',
                           internal=True, settable=True),
        'triggered': Param('Time when input was triggered after a start',
                           internal=True, settable=True),
    }

    parameter_overrides = {
        'fmtstr':    Override(default='%s'),
        'timeout':   Override(default=120),
        'unit':      Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        if mode == MASTER:
            self.triggered = self.started = 0

    def doStart(self, target):
        if target == 'triggered':
            self._attached_output.start(1)
            sleep(0.1)
            self._attached_output.start(0)
            self.started = currenttime()

    def doStatus(self, maxage=0):
        if self.started:
            if self.mode == MASTER and self._attached_input.read(maxage):
                self.started = 0
                self.triggered = currenttime()
                return status.OK, 'triggered'
            else:
                return status.BUSY, 'waiting'
        elif self.triggered:
            if self.mode == MASTER and currenttime() > self.triggered + 5:
                self.triggered = 0
            return status.OK, 'triggered'
        return status.OK, ''

    def doRead(self, maxage=0):
        if self.started:
            return 'waiting'
        return 'triggered'


class FPLCRate(AnalogInput):
    """Forward the current detector countrate to the FPLC."""

    attached_devices = {
        'rate':   Attach('device to read countrate', Readable),
    }

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        rate = self._attached_rate.read(maxage)[1]
        self._dev.value = rate
        return rate
