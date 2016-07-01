# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""FPGA Counter Card module

This module provides classes for controlling the ZEA-2 FPGA Counter Card using
their own interface. The current implementation does _not_ support multiple
masters, e.g. counting on time and count rate.

"""

from nicos.core import status, Param, Override, Value, intrange, UsageError, \
    Readable, MASTER
from nicos.devices.tango import PyTangoDevice
from nicos.devices.generic import ActiveChannel, TimerChannelMixin, \
    CounterChannelMixin

# XXX: implement doReadIsmaster to determine which channel is actually the
# current master.


class FPGAChannelBase(PyTangoDevice, ActiveChannel):
    """Basic Tango Device for ZEA-2 Counter Card."""

    parameters = {
        'extmode': Param('Arm for external start instead of starting',
                         type=bool, default=False, settable=True),
        'extmask': Param('Bitmask of the inputs to use for external start',
                         type=int, default=0),
        'extwait': Param('If true, we are waiting for external start',
                         type=bool, default=False, settable=True,
                         userparam=False),
    }

    def _setPreselection(self):
        """This method must be present and should set the the preselection
        value for the card before start."""
        raise NotImplementedError

    def doStart(self):
        self._dev.DevFPGACountReset()
        if self.ismaster:
            # preselection has to be set here and not in doWritePreset
            # because `DevFPGACountReset()` resets all values.
            self._setPreselection()
        if self.extmode:
            self.extwait = True
            self._dev.DevFPGACountArmForExternalStart(self.extmask)
        else:
            self._dev.DevFPGACountStart()

    def doFinish(self):
        self.extwait = False
        self._dev.DevFPGACountStop()

    def doStop(self):
        self.doFinish()

    def doPause(self):
        if self.extmode:
            return False
        self.finish()
        return True

    def doResume(self):
        self._dev.DevFPGACountStart()

    def doRead(self, maxage=0):
        raise NotImplementedError

    def doStatus(self, maxage=0):
        # Workaround self._dev.State() does not return DevState.MOVING
        if self._dev.DevFPGACountGateStatus():
            return (status.BUSY, 'counting')
        else:
            return (status.OK, '')

    def doReset(self):
        if self.status(0)[0] == status.BUSY:
            self.finish()
        self._dev.DevFPGACountReset()


class FPGATimerChannel(TimerChannelMixin, FPGAChannelBase):
    """FPGATimerChannel implements one time channel for ZEA-2 counter card."""

    def _setPreselection(self):
        millis = int(self.preselection * 1000)
        self._dev.DevFPGACountSetTimeLimit(millis)
        self._dev.DevFPGACountSetMinTime(millis)

    def doStatus(self, maxage=0):
        # Normal mode: Gate is active
        if self._dev.DevFPGACountGateStatus():
            if self.extmode and self.extwait and self._mode == MASTER:
                self.log.info('external signal arrived, counting...')
                self.extwait = False
            return (status.BUSY, 'counting')
        elif self.extmode and self.extwait:
            # External mode: there is no status indication of "waiting",
            # so use the time as an indication of wait/done
            if self._dev.DevFPGACountReadTime() > 0:
                return (status.OK, '')
            return (status.BUSY, 'waiting for external start')
        else:
            return (status.OK, '')

    def doRead(self, maxage=0):
        return [self._dev.DevFPGACountReadTime() / 1000.]


class FPGACounterChannel(CounterChannelMixin, FPGAChannelBase):
    """FPGACounterChannel implements one monitor channel for ZEA-2 counter
    card.
    """

    parameters = {
        'channel': Param('Channel number', type=intrange(0, 4),
                         settable=False, mandatory=True)
    }

    def _setPreselection(self):
        self._dev.DevFPGACountSetMinTime(0)
        self._dev.DevFPGACountSetTimeLimit(3600*24)
        self._dev.DevFPGACountSetCountLimit([self.channel,
                                             int(self.preselection)])

    def doRead(self, maxage=0):
        return self._dev.DevFPGACountReadCount(self.channel)


class FPGAFrequencyChannel(TimerChannelMixin, FPGAChannelBase):
    """FPGAFrequencyChannel implements the frequency channel for ZEA-2 counter
    card.
    """

    is_timer = False

    parameter_overrides = {
        'unit':   Override(default='Hz'),
        'fmtstr': Override(default='%.2f'),
    }

    def _setPreselection(self):
        raise UsageError(self, 'this channel cannot be preselected')

    def doRead(self, maxage=0):
        return [self._dev.DevFPGACountReadFreq()]

    def valueInfo(self):
        return Value(self.name, unit='Hz', type='other', fmtstr=self.fmtstr),


class FPGARate(PyTangoDevice, Readable):
    """Determines the instantaneous count rate of a counter card channel."""

    parameters = {
        'channel': Param('Channel number', type=intrange(0, 4),
                         settable=False, mandatory=True)
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False, default='cps'),
    }

    _last = None

    def doRead(self, maxage=0):
        cur = (self._dev.DevFPGACountReadCount(self.channel),
               self._dev.DevFPGACountReadTime() / 1000.)
        if cur[1] == 0:
            res = 0.0
        elif self._last is None or self._last[1] > cur[1]:
            res = cur[0] / cur[1]
        elif self._last[1] == cur[1]:
            res = 0.0
        else:
            res = (cur[0] - self._last[0]) / (cur[1] - self._last[1])

        self._last = cur
        return res
