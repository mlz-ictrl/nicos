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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF safety system readout."""

from time import sleep

from nicos.core import Readable, Moveable, Override, Attach, status, oneofdict
from nicos.devices.taco import DigitalInput, DigitalOutput

from nicos.toftof.safety_desc import bit_description


class SafetyInputs(Readable):
    """The input devices for the safety system.

    The safety system has a lot of status lines which are connected to a
    separate input which is integrated into the NICOS system.
    """
    attached_devices = {
        'i7053': Attach('three 7053 modules', DigitalInput, multiple=3),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False),
        'fmtstr': Override(default='%d'),
        'maxage': Override(default=0),
    }

    def _readHWState(self, maxage=0):
        state = 0
        for i, sdev in enumerate(self._attached_i7053):
            state |= (sdev.read(maxage) << (16 * i))
        return state

    def doRead(self, maxage=0):
        state = self._readHWState(maxage)
        self.log.info('val description')
        for i, bit in enumerate(bin(state)[2:][::-1]):
            self.log.info('%s   %s' % (bit, bit_description[i]))
        return state

    def doStatus(self, maxage=0):
        # XXX define which bits may be active for normal state
        state = self._readHWState(maxage)
        return status.OK, str(state)


class Shutter(Moveable):
    """TOFTOF Shutter Control."""

    attached_devices = {
        'open':   Attach('Shutter open button device', DigitalOutput),
        'close':  Attach('Shutter close button device', DigitalOutput),
        'status': Attach('Shutter status device', DigitalOutput),
    }

    parameter_overrides = {
        'unit':   Override(mandatory=False),
        'fmtstr': Override(default='%s'),
    }

    valuetype = oneofdict({0: 'closed', 1: 'open'})

    def doStart(self, target):
        if target == 'open':
            self._attached_open.start(1)
            sleep(0.01)
            self._attached_open.start(0)
        else:
            self._attached_close.start(1)
            sleep(0.01)
            self._attached_close.start(0)

    def doStop(self):
        self.log.info('note: shutter collimator does not use stop() anymore, '
                      'use move(%s, "closed")' % self)

    def doRead(self, maxage=0):
        ret = self._attached_status.read(maxage)
        if ret == 1:
            return 'closed'
        else:
            return 'open'

    def doStatus(self, maxage=0):
        return status.OK, ''
