#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Devices for the Refsans expertvibro."""

from nicos.core import Attach, Override, Param, Readable, status
from nicos.devices.tango import PyTangoDevice


class Base(PyTangoDevice, Readable):
    """
    Basic IO Device object for devices in refsans' expertvibro rack
    contains common things for all devices.
    """

    hardware_access = True

    parameters = {
        'firmware': Param('Firmware version',
                          type=float, settable=False, volatile=True,
                          fmtstr='%.1f'),
    }

    def _readBuffer(self):
        return tuple(self._dev.ReadOutputFloats((0, 16)))

    #
    # Nicos Methods
    #

    def doRead(self, maxage=0):
        return self._readBuffer()

    def doReadFirmware(self):
        return 0

    def doStatus(self, maxage=0):
        return status.OK, ''


class AnalogValue(Readable):
    attached_devices = {
        'iodev': Attach('IO Device', Base),
    }

    parameters = {
        'channel': Param('Channel for readout', type=int, settable=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True, settable=False),
    }

    def doReadUnit(self):
        return 'foo'

    def doRead(self, maxage=0):
        return self._attached_iodev._readBuffer()[self.channel]

    def doStatus(self, maxage=0):
        return status.OK, ''
