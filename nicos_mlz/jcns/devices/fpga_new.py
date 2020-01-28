# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""
This module provides classes for controlling the FZJ FPGA counter card using
the Entangle server with MLZ interface.
"""

from __future__ import absolute_import, division, print_function

from time import time as currenttime

from nicos.core import MASTER, Param, status, MoveError
from nicos.devices.tango import TimerChannel


class FPGATimerChannel(TimerChannel):
    """FPGATimerChannel implements the time channel for ZEA-2 counter card,
    and handles external start triggering for the counter card.
    """

    parameters = {
        'extmode':    Param('Arm for external start instead of starting',
                            type=bool, default=False, settable=True),
        'extmask':    Param('Bitmask of the inputs to use for external start',
                            type=int, default=0),
        'exttimeout': Param('Timeout for waiting for external start',
                            type=float, unit='s', default=600),
        'extwait':    Param('If nonzero, we are waiting for external start '
                            'since that timestamp',
                            type=float, default=0, settable=True,
                            internal=True),
    }

    def doStart(self):
        if self.extmode:
            self.extwait = currenttime()
        TimerChannel.doStart(self)

    def doStatus(self, maxage=0):
        st = TimerChannel.doStatus(self, maxage)
        # Normal mode: Gate is active
        if st[0] == status.BUSY:
            if self.extmode and self.extwait and self._mode == MASTER:
                self.log.info('external signal arrived, counting...')
                self.extwait = 0
            return st
        elif self.extmode and self.extwait > 0:
            # External mode: there is no status indication of "waiting",
            # so use the time as an indication of wait/done
            if self._dev.value > 0:
                return (status.OK, '')
            elif currenttime() > self.extwait + self.exttimeout:
                raise MoveError(self, 'timeout waiting for external start')
            return (status.BUSY, 'waiting for external start')
        else:
            return (status.OK, '')

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self.extwait = 0
        self._dev.Stop()

    def doPause(self):
        if self.extmode:
            return False
        self.finish()
        return True

    def doWriteExtmode(self, value):
        self._dev.externalStart = self.extmask if value else 0
