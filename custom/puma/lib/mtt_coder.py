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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special Class for coders that don't support reading of the confbyte."""

from nicos.utils import lazy_property
from nicos.devices.vendor.ipc import Coder as IPC_Coder
from nicos.core import SIMULATION


class SpecialCoder(IPC_Coder):
    def doInit(self, mode):
        bus = self._adevs['bus']
        if mode != SIMULATION:
            bus.ping(self.addr)
        self._lasterror = None

    def doReadConfbyte(self):
        return 16

    def doWriteConfbyte(self, byte):
        return

    def doUpdateConfbyte(self, byte):
        self._type = self._getcodertype(16)
        self._resolution = 16

    @lazy_property
    def _hwtype(self):
        return 'digital'

    def _getcodertype(self, byte):
        return 'special codertype'
