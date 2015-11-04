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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

""" Classes to access to the DSpec detector """

import time

from nicos.core import Measurable, Moveable, Readable, Attach, Param, status
# from nicos.devices.taco.io import DigitalOutput, DigitalInput
# from nicos.core.mixins import HasTimeout


class DSPec(Measurable):
    """The DSpec detector will be started and stopped via a digital output"""

    _lastpreset = {}

    parameters = {
        'startsleeptime': Param('Time to sleep after start command send',
                                type=float, default=2, settable=False),
    }

    attached_devices = {
        'set_ready': Attach('Device to enable the remote control',
                            Moveable),  # DigitalOutput),
        'get_ready': Attach('Device to read back the reached value',
                            Readable),  # DigitalInput),
    }

    def doStart(self):
        if self.doStatus()[0] == status.BUSY:
            self.doStop()
            self.doWait()
        self._attached_set_ready.move(0)
        time.sleep(self.startsleeptime)
        self._attached_set_ready.move(1)

    def doFinish(self):
        self._attached_set_ready.move(1)

    def doStop(self):
        self.doFinish()

    def doPreset(self, **preset):
        pass

    def doRead(self, maxage=0):
        return [self._lastpreset.get('t', 0)]

    def doStatus(self, maxage=0):
        if self._attached_get_ready.read(maxage) == 0:
            return status.BUSY, 'counting'
        else:
            return status.OK, 'stopped'

    def doSetPreset(self, **preset):
        self._lastpreset = preset
