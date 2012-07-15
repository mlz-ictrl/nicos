#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for i7000 input/output modules."""

__version__ = "$Revision$"

import IO

from nicos.core import Moveable, Param, status
from nicos.taco import TacoDevice


class Output(Moveable, TacoDevice):
    taco_class = IO.StringIO

    parameters = {
        'address': Param('Address of unit', type=int, mandatory=True),
    }

    def doStatus(self, maxage=0):
        #self._query('*IDN?')
        return status.OK, 'idle'

    def doRead(self, maxage=0):
        res = self._taco_guard(self._dev.communicate, '$%02X6' % self.address)
        return int(res[3:5], 16) | (int(res[5:7], 16) << 8)

    def doStart(self, value):
        lower = value & 0xff
        upper = value >> 8
        self._taco_guard(self._dev.communicate, '#%02X0A%02X' % (self.address, lower))
        self._taco_guard(self._dev.communicate, '#%02X0B%02X' % (self.address, upper))
