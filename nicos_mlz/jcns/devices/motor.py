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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

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
        limits = [self._invertPosition(l)
                  for l in TangoMotor.doReadAbslimits(self)]
        return min(limits), max(limits)

    def doSetPosition(self, pos):
        return TangoMotor.doSetPosition(
            self, self._invertPosition(pos + self.offset))


class MasterSlaveMotor(Moveable):
    """Combined master slave motor with possibility to apply a scale to the
    slave motor."""

    attached_devices = {
        "master": Attach("Master motor controlling the movement", Moveable),
        "slave": Attach("Slave motor following master motor movement",
                        Moveable),
    }

    parameters = {
        "scale": Param("Factor applied to master target position as slave "
                       "position", type=float, default=1),
    }

    parameter_overrides = {
        "unit": Override(mandatory=False),
        "fmtstr": Override(default="%.3f %.3f"),
    }

    def _slavePos(self, pos):
        return self.scale * pos

    def doRead(self, maxage=0):
        return [self._attached_master.read(maxage),
                self._attached_slave.read(maxage)]

    def doStart(self, target):
        self._attached_master.move(target)
        self._attached_slave.move(self._slavePos(target))

    def doIsAllowed(self, pos):
        faultmsgs = []
        messages = []
        for dev in [self._attached_master, self._attached_slave]:
            allowed, msg = dev.isAllowed(pos)
            msg = dev.name + ': ' + msg
            messages += [msg]
            if not allowed:
                faultmsgs += [msg]
        if faultmsgs:
            return False, ', '.join(faultmsgs)
        return True, ', '.join(messages)

    def doReadUnit(self):
        return self._attached_master.unit

    def valueInfo(self):
        return Value(self._attached_master.name, unit=self.unit,
                     fmtstr=self._attached_master.fmtstr), \
               Value(self._attached_slave.name, unit=self.unit,
                     fmtstr=self._attached_slave.fmtstr)
