#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS TACO counter/timer definition
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

"""
Implementation of TACO Timer and Counter devices.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

import IOCommon
import TACOStates
from IO import Timer as IOTimer, Counter as IOCounter

from nicm import status
from nicm.device import Countable, Param
from nicm.errors import ConfigurationError
from nicm.taco.base import TacoDevice


class TacoCountable(TacoDevice, Countable):
    """Base class for TACO countables."""

    parameters = {
        'ismaster':     Param('Whether the device is the master counter',
                              type=bool),
        'preselection': Param('Default preselection register value', default=1),
        'mode':         Param('Run mode for the countable', type=int),
        'loopdelay':    Param('Wait loop delay', unit='s', default=0.3),
    }

    def doInit(self):
        TacoDevice.doInit(self)
        # flag to distinguish pause from stop
        self.__stopped = False

    def doStart(self, preset=None):
        self.__stopped = False
        if preset is not None:
            self.preselection = preset
        self._taco_guard(self._dev.start)

    def doStop(self):
        self.__stopped = True
        self._taco_guard(self._dev.stop)

    def doResume(self):
        self.__stopped = False
        self._taco_guard(self._dev.resume)

    def doWait(self):
        while self.status()[0] == status.BUSY:
            sleep(self.loopdelay)

    def doClear(self):
        self.__stopped = False
        self._taco_guard(self._dev.stop)
        self._taco_guard(self._dev.clear)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state == TACOStates.PRESELECTION_REACHED:
            return (status.OK, 'preselection reached')
        elif state == TACOStates.STOPPED:
            if self.__stopped:
                return (status.OK, 'idle')
            else:
                return (status.PAUSED, 'paused')
        elif state == TACOStates.COUNTING:
            return (status.BUSY, 'counting')
        return (status.ERROR, TACOStates.stateDescription(state))

    def doReadPreselection(self):
        return self._taco_guard(self._dev.preselection)

    def doWritePreselection(self, value):
        self._taco_guard(self._dev.setPreselection, value)

    def doReadIsmaster(self):
        return self._taco_guard(self._dev.isMaster)

    def doWriteIsmaster(self, value):
        self._taco_guard(self._dev.enableMaster, bool(value))

    def doReadMode(self):
        mode = self._taco_guard(self._dev.mode)
        return {
            IOCommon.MODE_NORMAL: 'normal',
            IOCommon.MODE_RATEMETER: 'ratemeter',
            IOCommon.MODE_PRESELECTION: 'preselection',
        }[mode]

    def doWriteMode(self, value):
        try:
            newmode = {'normal': IOCommon.MODE_NORMAL,
                       'ratemeter': IOCommon.MODE_RATEMETER,
                       'preselection': IOCommon.MODE_PRESELECTION,
                       }[value]
        except KeyError:
            raise ConfigurationError(self, 'mode %r invalid' % (value,))
        self._taco_guard(self._dev.setMode, newmode)


class Timer(TacoCountable):
    taco_class = IOTimer


class Counter(TacoCountable):
    taco_class = IOCounter
