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
#   Matthias Pomm <Matthias.Pomm@hzg.de>
#
# ****************************************************************************

"""Temperature controlled device."""

import operator
from time import monotonic as currenttime

from nicos import session
from nicos.core import SIMULATION, Moveable, NicosError, NicosTimeoutError, \
    Readable, status
from nicos.core.params import Attach, Param, floatrange, oneof
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SequenceItem


class SeqWaitConditional(SequenceItem):

    def __init__(self, dev, timeout, limit=40, limittype='max', reason=''):
        oneof('min', 'max')(limittype)
        SequenceItem.__init__(self, dev=dev, limit=limit, reason=reason,
                              timeout=timeout, limittype=limittype)
        self.opmap = {
            'max': ('<', operator.lt),
            'min': ('>', operator.gt),
        }

        self.stopflag = False
        self.endtime = 0
        self.waiting = False

    def run(self):
        self.stopflag = False
        self.waiting = False
        self.endtime = currenttime() + self.timeout

    def isCompleted(self):
        if session.mode == SIMULATION:
            return True
        value = self.dev.read(0)
        if self.opmap[self.limittype][1](value, self.limit):
            log = self.dev.log if self.waiting else self.dev.debug
            log('%s %s %s continue', self.dev.format(value),
                self.opmap[self.limittype][0],
                self.dev.format(self.limit, True))
            return True
        if self.stopflag:
            raise NicosError('Stop received: Waiting aborted')
        if currenttime() < self.endtime:
            compstr = '<=' if self.limittype == 'max' else '>='
            self.dev.log.info(
                '%s %s %s, timeout in: %.1f min', self.dev.format(value),
                compstr, self.dev.format(self.limit, True),
                (self.endtime - currenttime()) / 60)
            session.delay(1)
            self.waiting = True
            return False
        raise NicosTimeoutError(
            f'{self.reason} after {self.timeout/60:.1f} min')

    def stop(self):
        self.stopflag = True


class TemperatureControlled(BaseSequencer):

    attached_devices = {
        'device': Attach('main device', Moveable),
        'temperature': Attach('temperature reading device', Readable),
    }

    parameters = {
        'maxtemp': Param('maximum temperature to move device',
                         type=floatrange(0), default=40),
        'timeout': Param('Time limit for the device to reach its target'
                         ', or None', unit='min', fmtstr='%.1f',
                         type=floatrange(0), default=20,
                         settable=True, mandatory=False, chatty=True),
    }

    def doRead(self, maxage=0):
        return self._attached_device.read(maxage)

    def doStatus(self, maxage=0):
        state = BaseSequencer.doStatus(self, maxage)
        if state[0] != status.OK:
            return state
        return self._attached_device.status(maxage)

    def doIsAllowed(self, target):
        return self._attached_device.isAllowed(target)

    def _generateSequence(self, target):
        return [
            SeqWaitConditional(self._attached_temperature, self.timeout * 60,
                               limit=self.maxtemp, reason='HW still HOT'),
            SeqDev(self._attached_device, target, True),
        ]
