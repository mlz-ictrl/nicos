#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.core import HasOffset, Param, Value
from nicos.core.device import Moveable
from nicos.core.params import Attach, Override
from nicos.devices.tango import Motor as TangoMotor


class InvertableMotor(HasOffset, TangoMotor):
    """Tango motor with offset and the possibility to invert the axis.

    In order to invert axes which can't be inverted on controller level this
    class additionally provides the ``invert`` parameter.
    """

    parameters = {
        "invert": Param("Invert axis", type=bool, settable=True,
                        default=False),
    }

    def _invertPosition(self, pos):
        return -pos if self.invert else pos

    def doRead(self, maxage=0):
        pos = TangoMotor.doRead(self, maxage)
        res = self._invertPosition(pos) - self.offset
        self.log.debug("[read]  raw: %.3f  res: %.3f    offset: %.3f",
                       pos, res, self.offset)
        return res

    def doStart(self, target):
        pos = self._invertPosition(target + self.offset)
        self.log.debug("[start] raw: %.3f  res: %.3f    offset: %.3f",
                       target, pos, self.offset)
        return TangoMotor.doStart(self, pos)

    def doReadRefpos(self):
        return self._invertPosition(TangoMotor.doReadRefpos(self))

    def doReadAbslimits(self):
        limits = map(self._invertPosition, TangoMotor.doReadAbslimits(self))
        return min(limits), max(limits)

    def doSetPosition(self, value):
        return TangoMotor.doSetPosition(self,
                                        self._invertPosition(value +
                                                             self.offset))


class MainSubordinateMotor(Moveable):
    """Combined main subordinate motor with possibility to apply a scale to the
    subordinate motor."""

    attached_devices = {
        "main": Attach("Main motor controlling the movement", Moveable),
        "subordinate": Attach("Subordinate motor following main motor movement",
                        Moveable),
    }

    parameters = {
        "scale": Param("Factor applied to main target position as subordinate "
                       "position", type=float, default=1),
    }

    parameter_overrides = {
        "unit": Override(mandatory=False),
        "fmtstr": Override(default="%.3f %.3f"),
    }

    def _subordinatePos(self, pos):
        return self.scale * pos

    def doRead(self, maxage=0):
        return [self._attached_main.read(maxage),
                self._attached_subordinate.read(maxage)]

    def doStart(self, pos):
        self._attached_main.move(pos)
        self._attached_subordinate.move(self._subordinatePos(pos))

    def doIsAllowed(self, pos):
        faultmsgs = []
        messages = []
        for dev in [self._attached_main, self._attached_subordinate]:
            allowed, msg = dev.isAllowed(pos)
            msg = dev.name + ': ' + msg
            messages += [msg]
            if not allowed:
                faultmsgs += [msg]
        if faultmsgs:
            return False, ', '.join(faultmsgs)
        return True, ', '.join(messages)

    def doReadUnit(self):
        return self._attached_main.unit

    def valueInfo(self):
        return Value(self._attached_main.name, unit=self.unit,
                     fmtstr=self._attached_main.fmtstr), \
               Value(self._attached_subordinate.name, unit=self.unit,
                     fmtstr=self._attached_subordinate.fmtstr)
