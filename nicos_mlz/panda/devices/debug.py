#  -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from time import sleep

from nicos.core import status
from nicos.core.device import Readable
from nicos.core.params import Attach
from nicos.devices.tango import Motor
from nicos_mlz.jcns.devices.motor import InvertableMotor


class PollMotor(Motor):

    attached_devices = {
        "polldevs": Attach("Devices polled during movement at same interval",
                           Readable, multiple=True, optional=True),
    }

    def _getWaiters(self):
        return []

    def doRead(self, maxage=0):
        for d in self._attached_polldevs:
            d.read(maxage)
        return Motor.doRead(self, maxage)


class InvertablePollMotor(InvertableMotor, PollMotor):
    """Tango motor with offset, invert and polldevs polled at same interval."""

    def doStart(self, target):
        if self.status(0)[0] == status.ERROR:
            self.log.info('resetting before start...')
            self.doReset()
        InvertableMotor.doStart(self, target)

    def doRead(self, maxage=0):
        PollMotor.doRead(self, maxage)
        return InvertableMotor.doRead(self, maxage)

    def doReset(self):
        InvertableMotor.doReset(self)
        # wait for reset to finish up
        while self.status(0)[0] == status.UNKNOWN:
            sleep(0.1)
