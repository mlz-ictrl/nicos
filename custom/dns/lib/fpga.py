# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

# standard library

# local library
import nicos.core.status as status
from nicos.core.params import Param, Override, oneof
from nicos.devices.tango import PyTangoDevice
from nicos.devices.generic.detector import Channel

__author__ = "Christian Felder <c.felder@fz-juelich.de>"
__date__ = "2014-04-28"
__version__ = "0.1.0"


class FPGAChannelBase(PyTangoDevice, Channel):
    """Basic Tango Device for ZEA-2 Counter Card."""

    MODE_NORMAL = "normal"
    MODE_PRESELECTION = "preselection"

    parameter_overrides = {
                           "mode": Override(type=oneof(MODE_NORMAL,
                                                       MODE_PRESELECTION)),
                           }

    def doStart(self):
        raise NotImplementedError

    def doStop(self):
        self._dev.DevFPGACountStop()

    def doRead(self, maxage=0):
        raise NotImplementedError

    def doStatus(self, maxage=0, mapping=None):
        # Workaround self._dev.State() does not return DevState.MOVING
        if self._dev.DevFPGACountGateStatus():
            res = (status.BUSY, "counting.")
        else:
            res = (status.OK, '')
        return res

    def doReset(self):
        if self.status(0)[0] == status.BUSY:
            self.stop()
        self._dev.DevFPGACountReset()


class FPGATimerChannel(FPGAChannelBase):
    """FPGATimerChannel implements one time channel for ZEA-2 counter card."""

    parameter_overrides = {
                           "unit": Override(default='s', mandatory=False),
                           }

    def doStart(self):
        self._dev.DevFPGACountReset()
        if self.mode == FPGAChannelBase.MODE_PRESELECTION:
            # preselection has to be set here and  not in doWritePreset
            # because `DevFPGACountReset()` resets also the values below.
            millis = int(self.preselection * 1000)
            self._dev.DevFPGACountSetTimeLimit(millis)
            self._dev.DevFPGACountSetMinTime(millis)
        self._dev.DevFPGACountStart()

    def doRead(self, maxage=0):
        return self._dev.DevFPGACountReadTime() / 1000.

    def doPause(self):
        self.stop()
        self.log.debug("FPGA pause")

    def doResume(self):
        self._dev.DevFPGACountStart()
        self.log.debug("FPGA resume")

    def doIsCompleted(self):
        if self.status(0)[0] == status.BUSY:
            return False
        return True

class FPGACounterChannel(FPGATimerChannel):
    """FPGACounterChannel implements one monitor channel for ZEA-2 counter card."""

    parameters = {
                  "channel": Param("Channel number", type=oneof(0, 1, 2, 3),
                                   settable=False, mandatory=True)
                 }

    parameter_overrides = {
                           "unit": Override(default="cts", mandatory=False),
                          }

    def doRead(self, maxage=0):
        return self._dev.DevFPGACountReadCount(self.channel)
