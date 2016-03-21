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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Class for Keysight Technologies 34461A TrueVolt."""

from nicos.core import Measurable, CommunicationError, Override, status
from nicos.devices.tango import PyTangoDevice
from nicos.core import SIMULATION

class VoltageMeter(PyTangoDevice, Measurable):
    """
    Keysight Technologies 34461A TrueVolt.
    """

    parameter_overrides = {
        'unit':         Override(mandatory=False),
        'pollinterval': Override(default=5),
        'maxage':       Override(default=20),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._dev.Communicate('*IDN?')
        if not reply.startswith('Keysight Technologies,34461A'):
            raise CommunicationError('wrong identification: %r' % reply)

    def doRead(self, maxage=0):
        return float(self._dev.Communicate('MEASure:VOLTage:DC?'))

    def doStatus(self, maxage=0):
        return status.OK, ''
