#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos.core import Moveable, Readable
from nicos.core.errors import ConfigurationError
from nicos.core.params import Attach

from nicos_mlz.refsans.devices.mixins import PolynomFit


class AnalogEncoder(PolynomFit, Readable):

    attached_devices = {
        'device': Attach('Sensing device (poti etc)', Readable),
    }

    def doRead(self, maxage=0):
        """Return a read analogue signal corrected by a polynom.

        A correcting polynom of at least first order is used.
        Result is then offset + mul * <previously calculated value>
        """
        return self._fit(self._attached_device.read(maxage))


class AnalogMove(AnalogEncoder, Moveable):
    """does only work for polynomial order of 1
    a reverse polynomial can only be done for a order of 1
    """

    def doStart(self, target):
        self.log.debug('uncorrected value: %f', target)
        result = (target - self.poly[0]) / self.poly[1]
        self.log.debug('final result: %f', result)
        return self._attached_device.move(result)

    def doWritePoly(self, poly):
        if len(poly) != 2:
            raise ConfigurationError('Only a linear correction is allowed')
        self._fitter = np.polynomial.Polynomial(poly)
