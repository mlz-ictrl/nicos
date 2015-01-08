#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, Override, Value, oneof, oneofdict
from nicos.devices.taco.core import TacoDevice
from nicos.devices.generic.detector import Channel, MultiChannelDetector


class FRMChannel(TacoDevice, Channel):
    """Base class for one channel of the FRM-II counter card.

    Use one of the concrete classes `FRMTimerChannel` or `FRMCounterChannel`.
    """

    parameter_overrides = {
        'mode': Override(type=oneofdict({
                             IOCommon.MODE_NORMAL: 'normal',
                             IOCommon.MODE_RATEMETER: 'ratemeter',
                             IOCommon.MODE_PRESELECTION: 'preselection'})),
    }

    def doStart(self):
        self._taco_guard(self._dev.start)

    def doPause(self):
        self._taco_guard(self._dev.stop)

    def doResume(self):
        self._taco_guard(self._dev.resume)

    def doStop(self):
        self._taco_guard(self._dev.stop)

    def doRead(self, maxage=0):
        return self._taco_guard(self._dev.read)

    def doIsCompleted(self):
        state = self._taco_guard(self._dev.deviceState)
        return state in [TACOStates.PRESELECTION_REACHED, TACOStates.DEVICE_NORMAL]

    def doReset(self):
        if self._taco_guard(self._dev.deviceState) != TACOStates.STOPPED:
            self._taco_guard(self._dev.stop)
        TacoDevice.doReset(self)

    def doReadPreselection(self):
        return self._taco_guard(self._dev.preselection)

    def doWritePreselection(self, value):
        self._taco_guard(self._dev.setPreselection, value)

    def doReadIsmaster(self):
        return self._taco_guard(self._dev.isMaster)

    def doWriteIsmaster(self, value):
        self._taco_guard(self._dev.enableMaster, value)

    def doReadMode(self):
        modes = {IOCommon.MODE_NORMAL: 'normal',
                 IOCommon.MODE_RATEMETER: 'ratemeter',
                 IOCommon.MODE_PRESELECTION: 'preselection'}
        mode = self._taco_guard(self._dev.mode)
        if mode not in modes:
            self.log.warning('Unknown mode %r encountered!' % mode)
            mode = IOCommon.MODE_NORMAL
        return modes[mode]

    def doWriteMode(self, value):
        modes = {'normal': IOCommon.MODE_NORMAL,
                 'ratemeter': IOCommon.MODE_RATEMETER,
                 'preselection': IOCommon.MODE_PRESELECTION}
        self._taco_guard(self._dev.setMode, modes[value])

    def doPrepare(self):
        self._taco_guard(self._dev.clear)


class FRMTimerChannel(FRMChannel):
    taco_class = Timer

    def doReadUnit(self):
        return 's'

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),

    def doTime(self, preset):
        if self.ismaster:
            return self.preselection
        else:
            return 0

    def doSimulate(self, preset):
        if self.ismaster:
            return [self.preselection]
        return [0.0]


class FRMCounterChannel(FRMChannel):
    taco_class = Counter

    parameters = {
        'type': Param('Type of channel: monitor or counter',
                      type=oneof('monitor', 'counter'), mandatory=True),
    }

    def doRead(self, maxage=0):
        # convert long to int if it fits
        return int(self._taco_guard(self._dev.read))

    def doReadUnit(self):
        return 'cts'

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt',
                     type=self.type, fmtstr='%d'),

    def doSimulate(self, preset):
        if self.ismaster:
            return [int(self.preselection)]
        return [0]


# backwards compatibility alias
FRMDetector = MultiChannelDetector
