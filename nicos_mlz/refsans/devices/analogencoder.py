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
#   Matthias Pomm <Matthias.Pomm@hzg.de>
#
# ****************************************************************************
"""
Support code for any encoder with analog signal, like poti laser distance etc
"""

import numpy as np

from nicos.core import HasPrecision, Moveable, Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach
from nicos.devices.abstract import TransformedMoveable, TransformedReadable

from nicos_mlz.refsans.devices.mixins import PolynomFit


class AnalogEncoder(PolynomFit, TransformedReadable):

    attached_devices = {
        'device': Attach('Sensing device (poti etc)', Readable),
    }

    def _readRaw(self, maxage=0):
        return self._attached_device.read(maxage)

    def _mapReadValue(self, value):
        """Return a read analogue signal corrected by a polynom.

        A correcting polynom of at least first order is used.
        Result is then offset + mul * <previously calculated value>
        """
        return self._fit(value)


class AnalogMove(HasPrecision, PolynomFit, TransformedMoveable):
    """Does only work for polynomial order of 1
    a reverse polynomial can only be done for a order of 1
    """

    attached_devices = {
        'device': Attach('Acting device (motor etc)', Moveable),
    }

    def _mapReadValue(self, value):
        return self._fit(value)

    def _mapTargetValue(self, target):
        self.log.debug('uncorrected value: %f', target)
        result = (target - self.poly[0]) / self.poly[1]
        self.log.debug('final result: %f', result)
        return result

    def _readRaw(self, maxage=0):
        return self._attached_device.read(maxage)

    def _startRaw(self, target):
        return self._attached_device.move(target)

    def doUpdatePoly(self, poly):
        if len(poly) != 2:
            self._fitter = None
            raise ConfigurationError('Only a linear correction is allowed')
        self._fitter = np.polynomial.Polynomial(poly)
