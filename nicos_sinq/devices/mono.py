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
#   Mark.Koennecke@psi.ch
#   Michele.Brambilla@psi.ch
#
# *****************************************************************************

"""
SINQ  monochromator

SINQ uses a different way to calculate monochromator focusing
"""

import math

from nicos.devices.generic.mono import to_k
from nicos.devices.tas.mono import Monochromator


class SinqMonochromator(Monochromator):
    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        focusv = self._attached_focusv
        th, _ = self._calc_angles(to_k(self.target, self.unit))
        if focusv:
            vcurve = vfocuspars[0] + \
                     vfocuspars[1] / math.sin(math.radians(abs(th)))
            focusv.move(vcurve)
        focush = self._attached_focush
        if focush:
            hcurve = hfocuspars[0] + \
                     hfocuspars[1]*math.sin(math.radians(abs(th)))
            focush.move(hcurve)


class TasAnalyser(SinqMonochromator):
    """
    This adds the offset magic for a5(theta) required at SINQ TAS analysers
    """
    def doWriteScatteringsense(self, value):
        off = self._attached_theta.offset
        if self.scatteringsense == -1 and value == 1:
            off += 180
        elif self.scatteringsense == 1 and value == -1:
            off -= 180
        if off > 180:
            off -= 360
        elif off < -180:
            off += 360
        self._attached_theta.offset = off
