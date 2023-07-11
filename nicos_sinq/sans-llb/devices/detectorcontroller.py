# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Attach, Device, IsController, Moveable, Param


class DetectorController(IsController, Device):
    """
    The high Q detector in the SANS-LLB tank could potentially crash
    into a rail. This class is supposed to prevent this. It allows z only to be
    moved when x is beyond a certain threshold. X can only be moved beyond the
    threshold when z is lower then a threshold value. The latter case serves
    the parking position use case for the detector.
    """

    parameters = {
        'xthreshold': Param('Threshold for x when driving z',
                            type=float),
        'zthreshold': Param('Threshold for z when driving x',
                            type=float),
    }

    attached_devices = {
        'z': Attach('Motor moving z', Moveable),
        'x': Attach('Motor for moving x', Moveable),
    }

    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev == self._attached_z:
            if self._attached_x.read(0) < self.xthreshold and \
                    adevtarget > self.zthreshold:
                return False, 'Move would crash into the rail'
        if adev == self._attached_x:
            if self._attached_z.read(0) > self.zthreshold and \
                    adevtarget < self.xthreshold:
                return False, 'Move would crash into the rail'
        return True, ''
