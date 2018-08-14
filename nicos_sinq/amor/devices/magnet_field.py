#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos.core import Moveable, Override, Attach


class MagneticFieldDevice(Moveable):
    """Represents the field of an electro-magnet
    """

    parameter_overrides = {
        'unit': Override(mandatory=False, default='T'),
        'fmtstr': Override(userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False)
    }

    attached_devices = {
        'magnet': Attach('Actual magnet device', Moveable)
    }

    _factor = 150.0 / 10000.0

    @property
    def magnet(self):
        return self._attached_magnet

    def doRead(self, maxage):
        return self.magnet.doRead(maxage) / self._factor

    def doStart(self, value):
        self.magnet.doStart(value * self._factor)

    def doStatus(self, maxage=0):
        return self.magnet.doStatus(maxage)
