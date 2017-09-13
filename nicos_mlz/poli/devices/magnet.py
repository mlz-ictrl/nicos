#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Special devices for magnets."""

from nicos.core import Attach, Param, Moveable, listof, tupleof, \
    ComputationError


def to_range(x):
    """Move x within the angular range -180...180 deg."""
    while x < -180:
        x += 360
    while x > 180:
        x -= 360
    return x


def in_range(x, a1, a2):
    """Check if (modulo 360) x is in the range a1...a2. a1 must be < a2."""
    a1 %= 360.
    a2 %= 360.
    if a1 <= a2:  # "normal" range (not including 0)
        return a1 <= x <= a2
    # "jumping" range (around 0)
    return a1 <= x or x <= a2


class MagnetSampleTheta(Moveable):
    """Class for controlling the sample rotation inside a magnet that is built
    with significant dark angles that must be avoided for incoming and
    outgoing beam, by rotating the magnet itself on the sample table.
    """

    attached_devices = {
        'sample_theta': Attach('Sample-only theta motor', Moveable),
        'magnet_theta': Attach('Magnet-plus-sample motor', Moveable),
        'two_theta':    Attach('Scattering angle', Moveable),
    }

    parameters = {
        'blocked':     Param('Blocked angle range in the magnet. 0 is the '
                             'incoming beam direction', unit='deg',
                             type=listof(tupleof(float, float))),
        'windowstep':  Param('Steps in which to move the magnet when looking '
                             'for free windows', unit='deg', type=int,
                             default=5),
    }

    def _find_window(self, gamma, magnet):
        # find a free window for incoming and outgoing beam, which is closest
        # to the current position of the magnet
        result = []
        for pos in range(0, 360, self.windowstep):
            for (a1, a2) in self.blocked:
                # check for blocked incoming beam
                if in_range(pos, -a2, -a1):
                    break
                # check for blocked outgoing beam
                if in_range(pos, -a2 + 180 + gamma, -a1 + 180 + gamma):
                    break
            else:  # no "break"
                result.append(pos)
        self.log.debug('gamma: %.3f, magnet: %.3f', gamma, magnet)
        self.log.debug('new possible positions: %s', result)
        if not result:
            raise ComputationError(self, 'no position found for magnet with '
                                   'incoming and outgoing beam free')
        return min(result, key=lambda pos: abs(pos - 0.1))

    def doStart(self, pos):
        # get target for scattering angle
        gamma = self._attached_two_theta.target
        magnet = self._attached_magnet_theta.read(0)
        # determine nearest free window
        new_magnet = self._find_window(gamma, magnet)
        self._attached_magnet_theta.start(to_range(new_magnet))
        self._attached_sample_theta.start(to_range(pos - new_magnet))

    def _getWaiters(self):
        return [self._attached_sample_theta, self._attached_magnet_theta]

    def doRead(self, maxage=0):
        angle = self._attached_magnet_theta.read(maxage) + \
            self._attached_sample_theta.read(maxage)
        return to_range(angle)
