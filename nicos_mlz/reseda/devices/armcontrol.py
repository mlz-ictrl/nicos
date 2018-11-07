#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
"""Controller to avoid arm collisions."""

from __future__ import absolute_import, division, print_function

from nicos.core.device import Device, Moveable
from nicos.core.mixins import IsController
from nicos.core.params import Attach, Override, Param, floatrange


class ArmController(IsController, Device):

    parameters = {
        'minangle': Param('Minimum angle between two arms',
                          type=floatrange(0, None), settable=False,
                          userparam=False, default=50.),
    }

    attached_devices = {
        'arm1': Attach('Arm 1 device', Moveable),
        'arm2': Attach('Arm 2 device', Moveable),
    }

    parameter_overrides = {
        'lowlevel': Override(default=True),
    }

    def isAdevTargetAllowed(self, adev, adevtarget):
        self.log.debug('%s: %s', adev, adevtarget)
        if adev == self._attached_arm1:
            target = self._attached_arm2.target
            if target is None:
                target = self._attached_arm2.read(0)
            absdiff = target - adevtarget
        else:
            target = self._attached_arm1.target
            if target is None:
                target = self._attached_arm1.read(0)
            absdiff = adevtarget - target
        if absdiff < 0:
            return False, 'Arms will cross.'
        dist = abs(absdiff)
        if dist >= self.minangle:
            return True, ''
        return False, 'Arms become too close to each other: %.3f deg, min. ' \
            'dist is %.3f' % (dist, self.minangle)
