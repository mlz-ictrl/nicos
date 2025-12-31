# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.core.errors import HardwareError
from nicos.core.params import Attach
from nicos.devices.entangle import NamedDigitalOutput

from nicos_mlz.labs.physlab.devices.d8 import D8


class Shutter(NamedDigitalOutput):
    """Shutter device checking the state of the door states before opening.

    Since the HV generator goes into a state, where only a restart of complete
    hardware (power off-on cycle) brings it up again, if one of the doors is
    not properly closed, the devices checks the state of the doors before it
    tries to open the shutter.

    The power off-on cycle requires a full realignment of the instrument!
    """

    attached_devices = {
        'd8': Attach('D8 hardware controller', D8),
    }

    def doStart(self, target):
        if target not in (0, 'closed'):
            if self._attached_d8.ldoor != 'locked':
                raise HardwareError(self, 'Left door is OPEN, please check it')
            if self._attached_d8.rdoor != 'locked':
                raise HardwareError(self, 'Right door is OPEN, please check it')
        NamedDigitalOutput.doStart(self, target)
