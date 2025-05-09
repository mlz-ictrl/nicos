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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""IPC (Institut für Physikalische Chemie, Göttingen) hardware classes."""

from nicos.core import SIMULATION
from nicos.devices.tango import PyTangoMixin

from .base import IPCModBusRS232


class IPCModBusTango(PyTangoMixin, IPCModBusRS232):

    def doInit(self, mode):
        IPCModBusRS232.doInit(self, mode)
        if mode != SIMULATION:
            self._dev.communicationTimeout = self.bustimeout

    def _transmit(self, request, retlen, last_try=False):
        reply = self._dev.BinaryCommunicate([retlen] + [ord(x) for x in request])
        return ''.join(map(chr, reply))
