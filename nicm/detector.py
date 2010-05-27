#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id $
#
# Description:
#   Detector classes for NICOS
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Detector classes for NICOS."""

__author__  = "$Author $"
__date__    = "$Date $"
__version__ = "$Revision $"

from time import sleep

import IOCommon
import TACOStates
from IO import Timer, Counter

from nicm import status
from nicm.device import Measurable
from nicm.errors import ConfigurationError
from nicm.taco.base import TacoDevice


class FRMChannel(TacoDevice, Measurable):
    """
    One channel of the FRM-II counter card.
    """

    parameters = {
        'mode': (0, False, 'Channel mode: normal, ratemeter, or preselection.'),
        'ismaster': (False, False, 'If this channel is a master.'),
        'preselection': (0, False, 'Preselection for this channel.'),
    }

    def doInit(self):
        self.preselection = self._taco_guard(self._dev.preselection)
        self.ismaster = self._taco_guard(self._dev.isMaster)
        self.mode = self._taco_guard(self._dev.mode)
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
            return status.OK
        elif state == TACOStates.STOPPED:
            # either OK or BUSY
            return self.__stopMode
        else:
            return status.BUSY

    def doIsCompleted(self):
        return self.doStatus() == status.OK

    def doReset(self):
        if self._taco_guard(self._dev.deviceState) != TACOStates.STOPPED:
            self._taco_guard(self._dev.stop)
        self._taco_guard(self._dev.deviceReset)
        if self._taco_guard(self._dev.isDeviceOff):
            self._taco_guard(self._dev.deviceOn)

    def doSetPreselection(self, value):
        self._taco_guard(self._dev.setPreselection, value)
        self._params['preselection'] = value

    def doSetIsmaster(self, value):
        value = bool(value)
        self._taco_guard(self._dev.enableMaster, value)
        self._params['ismaster'] = value

    def doSetMode(self, value):
        for s, i in [('normal', IOCommon.MODE_NORMAL),
                     ('ratemeter', IOCommon.MODE_RATEMETER),
                     ('preselection', IOCommon.MODE_PRESELECTION)]:
            if value == s or value == i:
                smode = s
                imode = i
        else:
            raise ConfigurationError(self, 'invalid value for the '
                                     'mode parameter: %s' % value)
        self._taco_guard(self._dev.setMode, imode)
        self._params['mode'] = smode


class FRMTimerChannel(FRMChannel):
    taco_class = Timer

    def valueInfo(self):
        return [self.name], ['s']


class FRMCounterChannel(FRMChannel):
    taco_class = Counter

    def valueInfo(self):
        return [self.name], ['cts']


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

    def __getMasters(self):
        """Internal method to get the masters from the card."""
        self.__masters = []
        self.__slaves = []
        for counter in self.__counters:
            if counter.getPar('ismaster'):
                self.__masters.append(counter)
            else:
                self.__slaves.append(counter)

    def doInit(self):
        self.__counters = []

        for name in ['t', 'm1', 'm2', 'm3', 'z1', 'z2', 'z3', 'z4', 'z5']:
            if self._adevs[name] is not None:
                self.__counters.append(self._adevs[name])

        self.__getMasters()

    def doStart(self, **preset):
        self.doStop()
        if preset:
            for master in self.__masters:
                master.setPar('ismaster', False)
                master.setPar('mode', 'normal')
            for name in preset:
                if name in self.attached_devices and self._adevs[name]:
                    self._adevs[name].setPar('ismaster', True)
                    self._adevs[name].setPar('mode', 'preselection')
                    self._adevs[name].setPar('preselection', preset[name])
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
        ret = []
        for counter in self.__counters:
            ret.extend(counter.read())
        return ret

    def doStatus(self):
        for master in self.__masters:
            if master.status() == status.BUSY:
                return status.BUSY
        return status.OK

    def doIsCompleted(self):
        for master in self.__masters:
            if not master.isCompleted():
                return False
        return True

    def doReset(self):
        for counter in self.__counters:
            counter.reset()

    def format(self, value):
        # XXX provisory
        return str(value)

    def valueInfo(self):
        names, units = [], []
        for counter in self.__counters:
            ret = counter.valueInfo()
            names.extend(ret[0])
            units.extend(ret[1])
        return names, units
