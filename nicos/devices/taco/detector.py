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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Detector classes for NICOS."""

import IOCommon
import TACOStates
from IO import Timer, Counter

from nicos.core import Param, UsageError, oneofdict
from nicos.devices.taco.core import TacoDevice
from nicos.devices.generic import ActiveChannel, TimerChannelMixin, \
    CounterChannelMixin


class BaseChannel(TacoDevice):
    """Base class for channels using the Taco Counter and Timer interfaces."""

    def doPrepare(self):
        self._taco_guard(self._dev.clear)

    def doStart(self):
        self._taco_guard(self._dev.start)

    def doPause(self):
        self.doStop()
        return True

    def doResume(self):
        self._taco_guard(self._dev.resume)

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doRead(self, maxage=0):
        return [self._taco_guard(self._dev.read)]

    def doReset(self):
        if self._taco_guard(self._dev.deviceState) != TACOStates.STOPPED:
            self.doStop()
        TacoDevice.doReset(self)

    def doReadPreselection(self):
        return self._taco_guard(self._dev.preselection)

    def doWritePreselection(self, value):
        self.doStop()
        self._taco_guard(self._dev.setPreselection, value)

    def doReadIsmaster(self):
        return self._taco_guard(self._dev.isMaster)

    def doWriteIsmaster(self, value):
        self.doStop()
        self._taco_guard(self._dev.enableMaster, value)


class FRMChannel(BaseChannel, ActiveChannel):
    """Base class for one channel of the FRM II counter card.

    Use one of the concrete classes `FRMTimerChannel` or `FRMCounterChannel`.
    """

    parameters = {
        'mode':  Param('Channel mode: normal, ratemeter, or preselection',
                       type=oneofdict(
                           {IOCommon.MODE_NORMAL: 'normal',
                            IOCommon.MODE_RATEMETER: 'ratemeter',
                            IOCommon.MODE_PRESELECTION: 'preselection'}),
                       default='preselection', settable=True),
    }

    def doReadMode(self):
        modes = {IOCommon.MODE_NORMAL: 'normal',
                 IOCommon.MODE_RATEMETER: 'ratemeter',
                 IOCommon.MODE_PRESELECTION: 'preselection'}
        mode = self._taco_guard(self._dev.mode)
        if mode not in modes:
            self.log.warning('Unknown mode %r encountered!', mode)
            mode = IOCommon.MODE_NORMAL
        return modes[mode]

    def doWriteMode(self, value):
        modes = {'normal': IOCommon.MODE_NORMAL,
                 'ratemeter': IOCommon.MODE_RATEMETER,
                 'preselection': IOCommon.MODE_PRESELECTION}
        self._taco_guard(self._dev.setMode, modes[value])

    def doWriteIsmaster(self, value):
        if self.mode == 'ratemeter':
            if value:
                raise UsageError(self, 'ratemeter channel cannot be master')
            return
        self.doStop()
        self.mode = 'preselection' if value else 'normal'
        self._taco_guard(self._dev.enableMaster, value)


class FRMTimerChannel(TimerChannelMixin, FRMChannel):
    taco_class = Timer

    def doRead(self, maxage=0):
        return [self._taco_guard(self._dev.read)]


class FRMCounterChannel(CounterChannelMixin, FRMChannel):
    taco_class = Counter

    def doRead(self, maxage=0):
        # convert long to int if it fits
        return [int(self._taco_guard(self._dev.read))]
