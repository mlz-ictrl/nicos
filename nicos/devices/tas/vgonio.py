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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Virtual goniometers that sit along the orientation reflexes, at an angle
to the real goniometers."""

from numpy import sin, cos, arcsin, pi

from nicos.core import Moveable, Param, Attach, oneof
from nicos.devices.tas.cell import Cell

D2R = pi / 180
R2D = 180 / pi

# The calculations here come from the equation
#
#   Xrot(x2) * Yrot(y2) = Zrot(psi) * Xrot(x1) * Yrot(y1) * Zrot(-psi)
#
# where x1, y1 and x2, y2 are either the gonio angles along the crystal axes
# or the angles of the physical gonios, and Xrot etc. are rotation matrices
# around the specified axis (with the sign as in sxtal posutils).
#
# This results in 9 equations, 2 of which are used here:
#
#   sin(x2)         = cos(x1)*sin(y1)*sin(psi) + cos(psi)*sin(x1)
#   cos(x2)*sin(y2) = cos(x1)*sin(y1)*cos(psi) - sin(psi)*sin(x1)


class VirtualGonio(Moveable):
    """Provides a virtual goniometer that sits along one of the sample's
    orientation reflexes, at an angle to the real goniometers.

    Two instances of this device should be created, one with axis 1 and
    one with axis 2.  Then the scattering plane can be adjusted independent
    of the orientation of the real gonios.
    """

    attached_devices = {
        'gx': Attach('Real x axis gonio', Moveable),
        'gy': Attach('Real y axis gonio', Moveable),
        'cell': Attach('TAS sample cell object', Cell),
    }

    parameters = {
        'axis': Param('Virtual axis for this gonio (along orient1 '
                      'or orient2)', type=oneof(1, 2)),
    }

    def _transform(self, x1, y1, psi):
        """Transform angles (in radians) ax and ay by a Z rotation by psi."""
        x2 = arcsin(cos(x1)*sin(y1)*sin(psi) + cos(psi)*sin(x1))
        tmp = cos(x1)*sin(y1)*cos(psi) - sin(psi)*sin(x1)
        return x2, arcsin(tmp / cos(x2))

    def _calcVirtual(self, maxage=0):
        gx = self._attached_gx.read(maxage) * D2R
        gy = self._attached_gy.read(maxage) * D2R
        psi0 = self._attached_cell.psi0 * D2R
        vx, vy = self._transform(gx, gy, psi0)
        return vx * R2D, vy * R2D

    def _calcReal(self, target):
        target *= D2R
        gx = self._attached_gx.target * D2R
        gy = self._attached_gy.target * D2R
        psi0 = self._attached_cell.psi0 * D2R
        # get current virtual angles
        vx, vy = self._transform(gx, gy, psi0)
        # substitute the one we want to drive
        vx, vy = (target, vy) if self.axis == 1 else (vx, target)
        # transform back to real (note the -psi0)
        gx, gy = self._transform(vx, vy, -psi0)
        return gx * R2D, gy * R2D

    def doRead(self, maxage=0):
        vx, vy = self._calcVirtual(maxage)
        return vx if self.axis == 1 else vy

    def doIsAllowed(self, target):
        gx, gy = self._calcReal(target)
        ok, msg = self._attached_gx.isAllowed(gx)
        if not ok:
            return False, 'real X gonio cannot move to %.3f: %s' % (gx, msg)
        ok, msg = self._attached_gy.isAllowed(gy)
        if not ok:
            return False, 'real Y gonio cannot move to %.3f: %s' % (gy, msg)
        return True, ''

    def doStart(self, target):
        gx, gy = self._calcReal(target)
        self._attached_gx.start(gx)
        self._attached_gy.start(gy)
