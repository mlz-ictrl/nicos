#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""CCR switch device classes."""

from nicos.core import Moveable, Override, Attach, status, oneofdict
from nicos.devices.taco import DigitalInput, DigitalOutput


class CCRSwitch(Moveable):
    """Class for FRM-II sample environment CCR box switches (gas/vacuum).
    """

    attached_devices = {
        'write':    Attach('TACO digital output device', DigitalOutput),
        'feedback': Attach('TACO digital input device (feedback)', DigitalInput),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'unit'  : Override(default='', mandatory=False),
    }

    valuetype = oneofdict({'on': 1, 'off': 0})

    def doStart(self, target):
        if self.read(0) != target:
            self._attached_write.start(1)

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doRead(self, maxage=0):
        return self._attached_feedback.read(maxage)
