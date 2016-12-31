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
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

from nicos.core import oneof, HasLimits, Moveable, HasPrecision, Param, Override, \
    multiStatus, multiReset, multiWait, Attach
from nicos.devices.abstract import CanReference


class CenteredDistanceDevice(HasLimits, CanReference, Moveable):
    """
    Device that controls the distance between attached devices A and B that can be moved
    symmetrically with respect to their center.

    It is assumed that the distance between A and B is 0 when both devices are at 0. When
    the coordinates parameter is 'opposite', when both devices' coordinates increase with distance from
    the center. For 'equal', device A is assumed to move in negative direction from the center,
    device B in the positive direction.

    This borrows heavily from Slit, essentially it is a one-axis slit in centered mode.
    """

    attached_devices = {
        'a': Attach('Device A', HasPrecision),
        'b': Attach('Device B', HasPrecision),
    }

    parameters = {
        'coordinates': Param('Coordinate convention for device A and B', default='equal',
                             type=oneof('equal', 'opposite')),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
        'abslimits': Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        self._axes = [self._attached_a, self._attached_b]
        self._axnames = ['A', 'B']

    def doReadAbslimits(self):
        limits_a = self._attached_a.abslimits
        limits_b = self._attached_b.abslimits

        if self.coordinates == 'equal':
            return limits_b[0] - limits_a[1], limits_b[1] - limits_a[0]

        return limits_b[0] + limits_a[0], limits_b[1] + limits_a[1]

    def doStart(self, target):
        self._doStartPositions(self._getPositions(target))

    def _doStartPositions(self, positions):
        for ax, pos in zip(self._axes, positions):
            ax.move(pos)

    def _getPositions(self, target):
        half_distance = target / 2.

        if self.coordinates == 'equal':
            return (-half_distance, half_distance)

        return (half_distance, half_distance)

    def doReset(self):
        multiReset(self._axes)
        multiWait(self._axes)

    def doReference(self):
        for ax in self._axes:
            if isinstance(ax, CanReference):
                self.log.info('referencing %s...', ax)
                ax.reference()
            else:
                self.log.warning('%s cannot be referenced', ax)

    def doRead(self, maxage=0):
        pos_a = self._attached_a.read(maxage)
        pos_b = self._attached_b.read(maxage)

        if self.coordinates == 'equal':
            return pos_b - pos_a

        return pos_b + pos_a

    def doStatus(self, maxage=0):
        return multiStatus(list(zip(self._axnames, self._axes)))

    def doReadUnit(self):
        return self._attached_a.unit
