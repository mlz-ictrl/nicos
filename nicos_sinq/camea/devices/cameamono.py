# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

import math

import numpy as np

from nicos.core import Attach, Moveable, Param, tupleof
from nicos.devices.tas.mono import to_k

from nicos_sinq.devices.mono import SinqMonochromator


class CameaMono(SinqMonochromator):
    """
    Camea needs to drive translations as well with the monochromator
    """

    parameters = {
        'upper_trans': Param('Parameters mta, mtb for controlling the '
                             'monochromator translation',
                             type=tupleof(float, float), default=[0, 3.5]),
        'lower_trans': Param('Parameters mta, mtb for controlling the '
                             'monochromator translation',
                             type=tupleof(float, float), default=[0, 3.5]),
    }

    attached_devices = {
        'upper': Attach('Upper monochromator translation', Moveable),
        'lower': Attach('Lower monochromator translation', Moveable),
    }

    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        focusv = self._attached_focusv
        th, _ = self._calc_angles(to_k(self.target, self.unit))
        vcurve = vfocuspars[0] +\
            vfocuspars[1]/math.sin(math.radians(abs(th)))
        focusv.move(vcurve)
        focush = self._attached_focush
        hcurve = hfocuspars[0] + \
            hfocuspars[1]*math.sin(math.radians(abs(th)))
        focush.move(hcurve)

        # Extra translations
        # Translations are forced to be in the limits (-7.5, 7.5)
        tum = self.upper_trans[0]*th + self.upper_trans[1]
        tum = np.sign(tum)*min(abs(tum), 7.5)
        self._attached_upper.move(tum)

        tlm = self.lower_trans[0]*th + self.lower_trans[1]
        tlm = np.sign(tlm)*min(abs(tlm), 7.5)
        self._attached_lower.move(tlm)
