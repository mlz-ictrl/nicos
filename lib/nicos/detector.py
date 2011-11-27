#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

import IOCommon
import TACOStates
from IO import Timer, Counter

from nicos import status
from nicos.taco import TacoDevice
from nicos.utils import oneof, oneofdict
from nicos.device import Measurable, Param, Value


class FRMChannel(TacoDevice, Measurable):
    """
    One channel of the FRM-II counter card.
    """

    parameters = {
        'mode': Param('Channel mode: normal, ratemeter, or preselection',
                      type=oneofdict({
                          IOCommon.MODE_NORMAL: 'normal',
                          IOCommon.MODE_RATEMETER: 'ratemeter',
                          IOCommon.MODE_PRESELECTION: 'preselection'}),
                      default='preselection', settable=True),
        'ismaster':     Param('If this channel is a master', type=bool,
                              settable=True),
        'preselection': Param('Preselection for this channel', settable=True),
    }

    def doInit(self):
        self.__stopMode = status.OK

    def doStart(self):
        self.__stopMode = status.OK
        self._taco_guard(self._dev.start)

    def doPause(self):
        self._taco_guard(self._dev.stop)
        self.__stopMode = status.BUSY

    def doResume(self):
        self._taco_guard(self._dev.resume)
        self.__stopMode = status.OK

    def doStop(self):
        self._taco_guard(self._dev.stop)
        self.__stopMode = status.OK

    def doRead(self):
        return self._taco_guard(self._dev.read)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.PRESELECTION_REACHED:
            return (status.OK, 'preselection reached')
        elif state == TACOStates.STOPPED:
            if self.__stopMode == status.OK:
                return (status.OK, 'idle')
            else:
                return (status.BUSY, 'paused')
        else:
            return (status.BUSY, TACOStates.stateDescription(state))

    def doIsCompleted(self):
        return self.doStatus()[0] == status.OK

    def doReset(self):
        if self._taco_guard(self._dev.deviceState) != TACOStates.STOPPED:
            self._taco_guard(self._dev.stop)
        self._taco_guard(self._dev.deviceReset)
        if self._taco_guard(self._dev.isDeviceOff):
            self._taco_guard(self._dev.deviceOn)

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
        return modes[self._taco_guard(self._dev.mode)]

    def doWriteMode(self, value):
        modes = {'normal': IOCommon.MODE_NORMAL,
                 'ratemeter': IOCommon.MODE_RATEMETER,
                 'preselection': IOCommon.MODE_PRESELECTION}
        self._taco_guard(self._dev.setMode, modes[value])


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
        return (self.preselection,)


class FRMCounterChannel(FRMChannel):
    taco_class = Counter

    parameters = {
        'type': Param('Type of channel: monitor or counter',
                      type=oneof(str, 'monitor', 'counter'), mandatory=True),
    }

    def doRead(self):
        # convert long to int if it fits
        return int(self._taco_guard(self._dev.read))

    def doReadUnit(self):
        return 'cts'

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt',
                     type=self.type, fmtstr='%d'),


class FRMDetector(Measurable):
    """
    The standard detector at FRM-II, using the FRM-II counter card.
    """

    attached_devices = {
        't':  FRMChannel,
        'm1': FRMChannel,
        'm2': FRMChannel,
        'm3': FRMChannel,
        'z1': FRMChannel,
        'z2': FRMChannel,
        'z3': FRMChannel,
        'z4': FRMChannel,
        'z5': FRMChannel,
    }

    hardware_access = False

    def __getMasters(self):
        """Internal method to get the masters from the card."""
        self.__masters = []
        self.__slaves = []
        for counter in self.__counters:
            if counter.ismaster:
                self.__masters.append(counter)
            else:
                self.__slaves.append(counter)

    def doPreinit(self):
        self.__counters = []

        for name in ['t', 'm1', 'm2', 'm3', 'z1', 'z2', 'z3', 'z4', 'z5']:
            if self._adevs[name] is not None:
                self.__counters.append(self._adevs[name])

        self.__getMasters()

    def doReadFmtstr(self):
        return ', '.join('%s %%s' % ctr.name for ctr in self.__counters)

    def doSetPreset(self, **preset):
        for master in self.__masters:
            master.ismaster = False
            master.mode = 'normal'
        for name in preset:
            if name in self.attached_devices and self._adevs[name]:
                self._adevs[name].ismaster = True
                self._adevs[name].mode = 'preselection'
                self._adevs[name].preselection = preset[name]
        self.__getMasters()

    def doStart(self, **preset):
        self.doStop()
        if preset:
            for master in self.__masters:
                master.ismaster = False
                master.mode = 'normal'
            for name in preset:
                if name in self.attached_devices and self._adevs[name]:
                    self._adevs[name].ismaster = True
                    self._adevs[name].mode = 'preselection'
                    self._adevs[name].preselection = preset[name]
            self.__getMasters()
        for slave in self.__slaves:
            slave.start()
        for master in self.__masters:
            master.start()

    def doPause(self):
        for master in self.__masters:
            master.doPause()
        return True

    def doResume(self):
        for master in self.__masters:
            master.doResume()

    def doStop(self):
        for master in self.__masters:
            master.stop()

    def doRead(self):
        return sum((ctr.read() for ctr in self.__counters), [])

    def doStatus(self):
        for master in self.__masters:
            masterstatus = master.status(0)
            if masterstatus[0] == status.BUSY:
                return masterstatus
        return (status.OK, 'idle')

    def doIsCompleted(self):
        for master in self.__masters:
            if master.isCompleted():
                return True
        return False

    def doReset(self):
        for counter in self.__counters:
            counter.reset()

    def valueInfo(self):
        return sum((ctr.valueInfo() for ctr in self.__counters), ())
