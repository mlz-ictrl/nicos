# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <Matthias.Pomm@hzg.de>
#
# ****************************************************************************
"""
Support code for any encoder with analog signal, like poti laser distance etc
"""

from nicos.core import status
from nicos.core.params import Param, Override, oneof
from nicos.devices.generic.analog import CalculatedReadable


class Accuracy(CalculatedReadable):

    parameters = {
        'absolute': Param('Value is absolute or signed.', type=bool,
                          settable=True, default=True),
    }

    parameter_overrides = {
        'op': Override(type=oneof('sub', '-'), settable=False, default='sub',
                       mandatory=False),
    }

    def doRead(self, maxage=0):
        dif = -CalculatedReadable.doRead(self, maxage)
        return abs(dif) if self.absolute else dif

    def doStatus(self, maxage=0):
        return status.OK, ''
