# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.core.constants import SIMULATION
from nicos.core.device import Device
from nicos.core.errors import ConfigurationError
from nicos.core.params import Param, tupleof, listof
from nicos.devices.tango import PyTangoDevice


class HexapodSpecial(PyTangoDevice, Device):
    """Ohe Hexapod Device for Workspace Configuration."""

    parameters = {
        "workspaces": Param("Hexapod workspaces list containing tuples of "
                            "(id, [xn, xp, yn, yp, zn, zp, rzn, rzp, ryn, ryp, "
                            "rxn, rxp, tx, ty, tz, rz, ry, rx])",
                            type=listof(tupleof(int, listof(float))),
                            mandatory=True, settable=False)
    }

    def doInit(self, mode):
        if any(idx < 10 or idx > 19 for idx, _ in self.workspaces):
            raise ConfigurationError("Workspace ids muste be in 10..19 "
                                     "(Jülich workspace range)")
        if mode != SIMULATION:
            workspaces = self._dev.workspaces  # Tango get workspaces
            for wsid, ws in self.workspaces:
                workspaces[wsid] = ws
            self._dev.workspaces = workspaces  # Tango set workspaces
