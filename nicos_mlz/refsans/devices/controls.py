#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <Matthias.Pomm@hzg.de>
#
# ****************************************************************************

"""Temperature controlled device."""

from nicos import session
from nicos.core import Moveable, NicosTimeoutError, Readable
from nicos.core.params import Attach, Param, floatrange
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod


class TemperatureControlled(BaseSequencer):

    attached_devices = {
        'device': Attach('main device', Moveable),
        'temperature': Attach('temperature reading device', Readable),
    }

    parameters = {
        'maxtemp': Param('maximum temperature to move device',
                        type=floatrange(0), default=40),
        'timeout': Param('Time limit for the device to reach its target'
                         ', or None', unit='s', fmtstr='%.1f',
                         type=floatrange(0), default=20,
                         settable=True, mandatory=False, chatty=True),
    }

    def doRead(self, maxage=0):
        return self._attached_device.read(maxage)

    def doStatus(self, maxage=0):
        return self._attached_device.status(maxage)

    def doIsAllowed(self, target):
        return self._attached_device.isAllowed(target)

    def _HW_wait_while_HOT(self):
        sd = 6.5
        waittime = self.timeout * 60
        waiting = False
        while waittime > 0:
            temp = self._attached_temperature.read(0)
            if temp < self.maxtemp:
                if waiting:
                    self.log.info('%d degC continue', temp)
                else:
                    self.log.debug('%d degC continue', temp)
                break
            waiting = True
            self.log.info('%d degC, timeout in: %.1f min', temp, waittime / 60)
            session.delay(sd)
            waittime -= sd
        else:
            raise NicosTimeoutError(
                'HW still HOT after {0:.1f} min'.format(self.timeout))

    def _generateSequence(self, target):
        return [
            SeqMethod(self, '_HW_wait_while_HOT'),
            SeqDev(self._attached_device, target, True),
        ]
