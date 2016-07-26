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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Haake/Julabo thermostat Protocol NICOS driver."""

from IO import StringIO

from nicos import session
from nicos.core import status, intrange, oneof, Moveable, \
    Param, Override, HasWindowTimeout, HasLimits
from nicos.devices.taco.core import TacoDevice

# TODO: split into two classes for the TWO used protocols.


class Controller(TacoDevice, HasWindowTimeout, HasLimits, Moveable):
    """The Julabo temperature controller."""
    taco_class = StringIO

    parameters = {
        'thermostat_type': Param('Type of thermostat',
                                 type=oneof('JulaboF32HD', 'HaakeDC50'),
                                 default='JulaboF32HD'),
        'intern_extern': Param('internal(0) or external(1) temperature sensor',
                               type=intrange(0, 1), default=1),
    }

    parameter_overrides = {
        'timeout':   Override(mandatory=False, default=600),
        'precision': Override(mandatory=False, default=0.02),
    }

    def _comm(self, cmd):
        return self._taco_guard(self._dev.communicate, cmd)

    def _write(self, cmd):
        return self._taco_guard(self._dev.writeLine, cmd)

    def doStart(self, pos):
        if self.thermostat_type == "JulaboF32HD":
            # switch thermostat on if it is off
            if self._comm("in_mode_05") == "0":
                self._write("out_mode_05 1")
                session.delay(2)  # ???
            # set correct external sensor setting
            if self._comm("in_mode_04") != str(self.intern_extern):
                self._write("out_mode_04 %d" % self.intern_extern)
                session.delay(2)  # ???
            # set correct setpoint (T1)
            if self._comm("in_mode_01") != "0":
                self._write("out_mode_01 0")
                session.delay(2)  # ???
        if self.thermostat_type == "JulaboF32HD":
            self._write("out_sp_00 %s" % pos)
        elif self.thermostat_type == "HaakeDC50":
            self._write("W S0 %f" % (pos,))
        session.delay(1)  # ???

    def doRead(self, maxage=0):
        # return current temperature
        if self.thermostat_type == "JulaboF32HD":
            if self.intern_extern == 0:
                temp = self._comm("in_pv_00")
            else:
                temp = self._comm("in_pv_02")
        elif self.thermostat_type == "HaakeDC50":
            temp = self._comm("R T3")
        return float(temp)

    def doStop(self):
        # stop ramp/step immediately
        if self.thermostat_type == "JulaboF32HD":
            self.start(self.doRead())
            # self._write("out_sp_00 %s" % self.doRead())

    def doStatus(self, maxage=0):
        # no HW status available.
        return status.OK, ''
