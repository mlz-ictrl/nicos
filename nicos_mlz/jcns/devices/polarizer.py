# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.core.device import Readable, Waitable
from nicos.core.params import Attach
from nicos.devices.tango import NamedDigitalOutput


class DOFlipper(NamedDigitalOutput, Waitable):
    """Flipper controlled via one digital output monitoring power supplies
    status."""

    attached_devices = {
        "powersupplies": Attach("Monitored power supplies", Readable,
                                multiple=True),
    }

    def doStatus(self, maxage=0):
        tangoState, tangoStatus = NamedDigitalOutput.doStatus(self, maxage)
        state, status = Waitable.doStatus(self, maxage)
        if tangoState > state:
            state = tangoState
        status = tangoStatus + ', ' + status
        return state, status
