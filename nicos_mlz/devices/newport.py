# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""Special devices for the Newport Hexapod."""

from nicos.core import Param, Readable
from nicos.devices.abstract import CanReference
from nicos.devices.entangle import MotorAxis
from nicos.devices.tango import PyTangoDevice


class HexapodMaster(PyTangoDevice, CanReference, Readable):
    """Newport hexapod device for configuration.

    The speed and acceleration settings can only be done global for all axes.

    The ``reset`` and ``reference`` action can only be executed on the device.
    """

    parameters = {
        'speed': Param('Master speed',
                       type=float, settable=True, userparam=True,
                       volatile=True,
                       ),
        'accel': Param('Master acceleration',
                       type=float, settable=True, userparam=True,
                       volatile=True,
                       ),
    }

    def doReadSpeed(self):
        return self._dev.speed

    def doWriteSpeed(self, value):
        self._dev.speed = value

    def doReadAccel(self):
        return self._dev.accel

    def doWriteAccel(self, value):
        self._dev.accel = value
        self._dev.decel = value

    def doReference(self):
        self._dev.Reference()
        self.wait()

    def doReset(self):
        self._dev.Reset()

    def doRead(self, maxage=0):
        return ''


class HexapodAxis(MotorAxis):
    """Special axis device which allows to set the coordinate system offset.

    It allows to switch between the tool and work coordinate system.
    """

    parameters = {
        'coordsystem': Param('Hexapod coordinate offset',
                             type=float, settable=True, userparam=True,
                             volatile=True,
                             ),
    }

    def doReadCoordsystem(self):
        return self._dev.CoordinateSystems

    def doWriteCoordsystem(self, value):
        self._dev.CoordinateSystems = value
