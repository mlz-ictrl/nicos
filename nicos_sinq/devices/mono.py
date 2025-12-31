# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.core.errors import LimitError
from nicos.devices.generic.mono import to_k
from nicos.devices.tas.mono import Monochromator, thetaangle


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
        session.delay(5)
        absmin, absmax = self._attached_theta.abslimits
        self._attached_theta.userlimits = absmin - off, absmax - off

    def _calc_angles(self, k):
        try:
            angle = thetaangle(self.dvalue, self.order, k)
        except ValueError:
            raise LimitError(
                self, 'wavelength not reachable with d=%.3f A and n=%s' % (
                    self.dvalue, self.order)) from None
        tt = 2.0 * angle * self.scatteringsense  # twotheta with correct sign
        th = angle * self.scatteringsense  # absolute theta with correct sign
        return th, tt

    def _get_angles(self, maxage):
        tt = self._attached_twotheta.read(maxage)
        th = self._attached_theta.read(maxage)
        return tt * self.scatteringsense, th*self.scatteringsense
