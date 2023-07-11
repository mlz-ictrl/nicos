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

from math import fabs

from nicos.core import Attach, Device
from nicos.core.errors import ProgrammingError
from nicos.core.mixins import HasPrecision, IsController


class BRSlit(IsController, Device):
    """
    This class makes sure that the slit blades of the HRPT br*
    slit do not crash. The motor controller goes into an undesirable
    state when this happens.
    """
    _targets = [0, 0, 0, 0]

    attached_devices = {
        'left': Attach('Left blade', HasPrecision),
        'right': Attach('Right blade', HasPrecision),
        'bottom': Attach('Bottom blade', HasPrecision),
        'top': Attach('Top blade', HasPrecision),
    }

    def doInit(self, mode):
        self._initTargets()

    def _initTargets(self):
        self._targets[0] = self._attached_right.read()
        self._targets[1] = self._attached_left.read()
        self._targets[2] = self._attached_bottom.read()
        self._targets[3] = self._attached_top.read()

    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev == self._attached_right:
            self._targets[0] = adevtarget
        elif adev == self._attached_left:
            self._targets[1] = adevtarget
        elif adev == self._attached_top:
            self._targets[3] = adevtarget
        elif adev == self._attached_bottom:
            self._targets[2] = adevtarget
        else:
            raise ProgrammingError('Cannot recognise %s ' % adev.name)
        status, reason = self._doIsAllowedPositions(self._targets)
        if not status:
            self._stop()
            self._initTargets()
        return status, reason

    def _stop(self):
        for dev in self._adevs.values():
            dev.stop()

    def _doIsAllowedPositions(self, positions):
        if fabs(positions[0]) + fabs(positions[1]) >= 21.71:
            return False, 'Horizontal blades would crash'
        if fabs(positions[2]) + fabs(positions[3]) >= 57:
            return False, 'Vertical blades would crash'
        return True, ''
