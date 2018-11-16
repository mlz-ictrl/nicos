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
"""PUMA special axis devices."""

from __future__ import absolute_import, division, print_function

from nicos.core import Moveable
from nicos.core.mixins import HasLimits, HasPrecision
from nicos.core.params import Attach, Override


class StackedAxis(HasLimits, HasPrecision, Moveable):
    """Device were two axes stacked.

    Both axes can be moved individually but the result of position and target
    is the sum of both position.  On of the axes (at the moment always the
    ``top`` axis) is preferred in use since it is cheaper (in time) to move it.

    ``HasPrecision`` is needed for the TAS monochromator device.
    """

    attached_devices = {
        'bottom': Attach('bottom axis', Moveable),
        'top': Attach('top axis', Moveable),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
        'unit': Override(default='deg', mandatory=False),
    }

    def doRead(self, maxage=0):
        self.log.debug('doRead: %s', maxage)
        return self._attached_bottom.read(maxage) + \
            self._attached_top.read(maxage)

    def doStart(self, target):
        targets = self._calc_targets(target)
        # The order is normally free to choose, but in the current application
        # the bottom device moves blocking
        self._attached_top.move(targets[1])
        self._attached_bottom.move(targets[0])

    def doIsAllowed(self, target):
        targets = self._calc_targets(target)
        for dev, t in zip([self._attached_bottom, self._attached_top],
                          targets):
            allowed = dev.isAllowed(t)
            if not allowed[0]:
                return allowed
        return True, ''

    def _calc_targets(self, target):
        """Calculate individual target positions from the sum target.

        Due to the limited range of movement of each individual axis the
        targets must be calculated for each axis.  Since the top axis is
        cheaper in time it will preferred in use and even the longer way
        if moving both.
        """
        targets = (0, 0)

        bpos = self._attached_bottom.read(0)
        lt = self._attached_top.userlimits

        # Simply move the top axis
        if lt[0] + bpos <= target <= lt[1] + bpos:
            targets = bpos, target - bpos
        else:
            tpos = self._attached_top.read(0)
            if target > (bpos + tpos):
                targets = target - lt[1], lt[1]
            else:
                targets = target - lt[0], lt[0]
        return targets

    def doReadAbslimits(self):
        return [sum(x) for x in zip(self._attached_bottom.abslimits,
                                    self._attached_top.abslimits)]
