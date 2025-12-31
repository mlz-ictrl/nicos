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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core import Attach
from nicos.devices.abstract import MappedMoveable

from nicos_sinq.devices.epics.extensions import EpicsCommandReply


class PicoSwitch(MappedMoveable):
    """
    A very small class for switching the spin flipper on/off via
    a I/O on the motor controller
    """

    attached_devices = {
        'directmcu': Attach('Direct connection to MCU',
                            EpicsCommandReply),
    }

    def _startRaw(self, target):
        self._attached_directmcu.execute('M596=%d', target)

    def doRead(self, maxage=0):
        # Cannot read that
        return self.target
