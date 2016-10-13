#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Tango motor with offset and the possibility to invert the axis."""

from nicos.core import HasOffset, Param
from nicos.devices.tango import Motor as TangoMotor


class Motor(HasOffset, TangoMotor):

    parameters = {
        "invert": Param("Invert axis", type=bool, settable=True, default=False),
    }

    def _invertPosition(self, pos):
        return -pos if self.invert else pos

    def doRead(self, maxage=0):
        pos = TangoMotor.doRead(self, maxage)
        return self._invertPosition(pos - self.offset)

    def doStart(self, target):
        pos = self._invertPosition(target) + self.offset
        return TangoMotor.doStart(self, pos)

    def doWriteOffset(self, value):
        HasOffset.doWriteOffset(self, value)
        return self._invertPosition(value)
