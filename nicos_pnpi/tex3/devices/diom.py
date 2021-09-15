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
#   Kirill Pshenichnyi <pshcyrill@mail.ru>
#
# *****************************************************************************

"""Class for virtual DIOM PhyMotion module"""

from nicos.core import Override, Param, intrange, status
from nicos.core.device import Moveable


class DIOMVirtual(Moveable):
    """Virtual module DIOM PhyMotion controller"""
    valuetype = intrange(0,255)
    parameters = {
        'units': Param('units', type=str, default=''),
        'curvalue':  Param('Current value',
                           type=intrange(0, 255),
                           internal=True, default=0,
                           settable=True
                           ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
    }

    def doInit(self, mode):
        self.log.debug('Init DIOM class, mode = %s', mode)

    def doStart(self, val):
        self.curvalue = val

    def doRead(self, maxage = 0):
        return self.curvalue

    def doStatus(self, maxage = 0):
        return status.OK, ''
