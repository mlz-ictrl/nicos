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
#   Michael Wedel <michael.wedel@esss.se>
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michael Hart <michael.hart@stfc.ac.uk>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
from nicos.core import Attach, Override, Readable, multiStatus, status
from nicos.devices.abstract import MappedMoveable


class EssChopperController(MappedMoveable):
    """Handles the status and hardware control for an ESS chopper system"""

    attached_devices = {
        'state': Attach('Current state of the chopper', Readable),
        'command': Attach('Command PV of the chopper', MappedMoveable)
    }

    parameter_overrides = {
        'fmtstr': Override(default='%s'),
        'unit': Override(mandatory=False),
        'mapping': Override(mandatory=False, settable=False, userparam=False,
                            volatile=True)
    }

    hardware_access = False
    valuetype = str

    def doRead(self, maxage=0):
        return self._attached_state.read()

    def doStart(self, value):
        self._attached_command.move(value)

    def doStop(self):
        # Ignore - stopping the chopper is done via the move command.
        pass

    def doReset(self):
        # Ignore - resetting the chopper is done via the move command.
        pass

    def doStatus(self, maxage=0):
        attached = [self._attached_command, self._attached_state]
        stat, msg = multiStatus(attached, maxage)
        if stat != status.OK:
            return stat, msg
        return status.OK, ''

    def doReadMapping(self):
        return self._attached_command.mapping
