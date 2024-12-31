# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

import numpy as np

from nicos.core.params import Param, listof

from nicos_sinq.sxtal.instrument import EulerSXTal, LiftingSXTal
from nicos_sinq.sxtal.singlexlib import calcTheta, z1ToNormalBeam


class SinqEuler(EulerSXTal):
    """
    This class adds Romain's polynomial scan width calculation
    """

    parameters = {
        'use_polynom': Param('Flag for using the polynomial for scan '
                             'width calculation', type=bool, settable=True,
                             userparam=True),
        'scan_polynom': Param('The coefficients for the scan width '
                              'calculation polynom', type=listof(float),
                              userparam=True, settable=True)}

    def getScanWidthFor(self, hkl):
        if self.use_polynom:
            cpos = self._calcPos(hkl)
            _, th = calcTheta(self.wavelength, cpos)
            fwhm = self.scan_polynom[0] + self.scan_polynom[1] * 2 * th + \
                self.scan_polynom[2] * np.power(2 * th, 2) + \
                self.scan_polynom[3] * np.power(2 * th, 3) + \
                self.scan_polynom[4] * np.power(2 * th, 4)
            return fwhm
        else:
            return EulerSXTal.getScanWidthFor(self, hkl)


class SinqNB(LiftingSXTal):
    """
    This class adds Romain's polynomial scan width calculation
    """

    parameters = {
        'use_polynom': Param('Flag for using the polynomial for scan '
                             'width calculation', type=bool, settable=True,
                             userparam=True),
        'scan_polynom': Param('The coefficients for the scan width '
                              'calculation polynom', type=listof(float),
                              userparam=True, settable=True)
    }

    def getScanWidthFor(self, hkl):
        if self.use_polynom:
            cpos = self._calcPos(hkl)
            _, th = calcTheta(self.wavelength, cpos)
            _, _, nu = z1ToNormalBeam(self.wavelength, cpos)
            fwhm = self.scan_polynom[0] + (
                self.scan_polynom[5] * nu + self.scan_polynom[6]) + \
                self.scan_polynom[1] * 2 * th + self.scan_polynom[
                       2] * np.power(2 * th, 2) + self.scan_polynom[
                       3] * np.power(2 * th, 3) + self.scan_polynom[
                       4] * np.power(2 * th, 4)
            return fwhm
        else:
            return LiftingSXTal.getScanWidthFor(self, hkl)
