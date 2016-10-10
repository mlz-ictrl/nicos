#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

"""Motor device via the CARESS device service."""

from nicos import session
from nicos.core import HasOffset, Override, POLLER, Param
from nicos.devices.abstract import Motor as AbstractMotor
from nicos.devices.vendor.caress.base import Driveable

EKF_44520_ABS = 114  # EKF 44520 motor control, abs. encoder, VME
EKF_44520_INCR = 115  # EKF 44520 motor control, incr. encoder, VME


class Motor(HasOffset, Driveable, AbstractMotor):
    """Device accessing the CARESS axes with and without encoder."""

    parameters = {
        'coderoffset': Param('Encoder offset',
                             type=float, default=0., unit='main',
                             settable=True, category='offsets', chatty=True,
                             ),
        'gear': Param('Ratio between motor and encoder',
                      type=float, default=1.0, settable=False,
                      ),
    }

    parameter_overrides = {
        'precision': Override(default=0.01)
    }

    def doInit(self, mode):
        Driveable.doInit(self, mode)

    def doStart(self, target):
        Driveable.doStart(self, target + (self.coderoffset + self.offset))

    def doRead(self, maxage=0):
        raw = Driveable.doRead(self, maxage)
        if raw is None and session.sessiontype == POLLER:
            return None
        return raw - (self.coderoffset + self.offset)

    def doSetPosition(self, pos):
        pass

    def doReadSpeed(self):
        tmp = self.config.split()
        # The  7th entry is the number of motor steps and the  6th entry the
        # number of encoder steps.  The ratio between both gives the speed of
        # the axis. It must be multiplied by the gear.
        if len(tmp) > 1:
            if int(tmp[1]) == EKF_44520_ABS:
                return self.gear * float(tmp[6]) / float(tmp[5])
        # in all other cases give the configured parameter back
        if 'speed' in self._params:
            return self._params['speed']
        return 0.0
