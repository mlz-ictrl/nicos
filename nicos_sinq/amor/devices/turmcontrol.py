# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Attach, Device, IsController, Moveable


class DetectorController(IsController, Device):
    """
    COM and COZ shall not be moved when the detector is in parking position
    """

    attached_devices = {
        'com': Attach('detector tilt', Moveable),
        'coz': Attach('detector offset', Moveable),
        'park': Attach('detector park motor', Moveable),
    }

    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev in [self._attached_com, self._attached_coz]:
            if self._attached_park.read(0) < -90:
                return False, "Cannot move %s when in park position"\
                    % (adev.name)
        return True, ''
