# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Param, Readable, listof, tupleof
from nicos.devices.generic import VirtualMotor


class VSForbiddenMoveable(VirtualMotor):
    """
    Velocity selectors have forbidden regions in which they are
    not supposed to run for reason of excessive vibration. This class
    checks for this
    """

    parameters = {
        'forbidden_regions': Param('List of forbidden regions',
                                   type=listof(tupleof(int, int)),
                                   mandatory=True)
    }

    valuetype = int

    def doStop(self):
        pass

    def doIsAllowed(self, value):
        for region in self.forbidden_regions:
            if region[0] <= value < region[1]:
                return False, \
                       'Desired value value is within ' \
                       'forbidden region %f to %f' \
                       % (region[0], region[1])
        return True, ''


class VSTiltMotor(VirtualMotor):
    """
    The tilt motor for a velocity selector can only be moved when
    the selector is standing. This class ensures just that.
    """
    attached_devices = {
        'vs_rotation': Attach('Velocity Selector Rotation', Readable),
    }

    parameters = {
        'limit': Param('Limit below which the rotation is considered standing',
                       type=float, mandatory=True)
    }

    def doIsAllowed(self, target):
        if self._attached_vs_rotation.read(0) <= self.limit:
            return True, ''
        return False, 'Velocity Selector must be stopped before moving tilt'
