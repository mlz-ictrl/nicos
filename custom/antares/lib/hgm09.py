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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""
Devices for the HGM09 gaussmeter.
"""

from IO import StringIO

from nicos.core import Readable, Override, CommunicationError, NicosError, \
    SIMULATION

from nicos.devices.taco import TacoDevice


class HGM09(TacoDevice, Readable):
    """Class for the HGM09 gaussmeter.

    Uses a taco StringIO device to communicate directly with the hardware.
    """

    taco_class = StringIO
    valuetype = float

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._communicate('*IDN?')
        if not reply.startswith('MAGSYS-MAGNET-SYSTEME,HGM09'):
            raise CommunicationError('wrong identification: %r' % reply)

    def doRead(self, maxage=0):
        try:
            value = HGM09.valuetype(self._communicate('READ?'))
        except (NicosError, ValueError):
            # retry communication/handle error
            value = HGM09.valuetype(self._communicate('READ?'))
        return value

    def doReadUnit(self):
        return self._communicate('UNIT?')

    def _communicate(self, msg):
        return self._taco_guard(self._dev.communicate, msg).strip()
