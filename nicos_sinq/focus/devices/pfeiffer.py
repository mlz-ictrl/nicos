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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core import Attach, Readable
from nicos.devices.epics import EpicsDevice

from nicos_ess.devices.epics.extensions import HasDisablePv


class PfeifferReadable(HasDisablePv, EpicsDevice, Readable):
    """
    The pfeiffer vacuum reading device at FOCUS has four sensors. It must
    be switched on before reading and switches itself off after a certain
    period of time has passed. This in order to reduce wear on the vacuum
    sensors.
    """

    attached_devices = {
        'sensors': Attach('Sensors to read',
                          Readable,
                          multiple=True)
    }

    def valueInfo(self):
        return tuple(sen.valueInfo() for sen in self._attached_sensors)

    def doRead(self, maxage=0):
        if not self.isEnabled:
            session.log.warning('Pfeiffer must be switched on before use')
            return [0, 0, 0, 0]
        return [sen.read(maxage) for sen in self._attached_sensors]
