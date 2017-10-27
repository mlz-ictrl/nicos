# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI x-ray tube conditioner"""

from nicos import session
from nicos.devices.tango import PyTangoDevice, AnalogInput
from nicos.core.device import Moveable
from nicos.core.params import Attach
from nicos.core import status


class TubeConditioner(PyTangoDevice, Moveable):
    """TANGO device to control tube conditioning"""

    attached_devices = {
        'interval': Attach('Time between two conditionings', AnalogInput),
        'time':     Attach('Time since last conditioning', AnalogInput)
    }

    def doStatus(self, maxage=0):
        stat = self._dev.value
        if stat == 'RUNNING':
            return status.BUSY, 'CONDITIONING'
        else:
            return status.OK, 'ON'

    def doRead(self, maxage=0):
        return self._dev.value

    def doStart(self, value):
        interval = self._attached_interval.read()
        if value < 0 or value > interval:
            self.log.warning('Value must be in [0; %.3f]', interval)
        elif self._attached_time.read(0) + value > interval:
            self.log.debug('Start cond')
            self._dev.StartCond()
            session.delay(5.0)
