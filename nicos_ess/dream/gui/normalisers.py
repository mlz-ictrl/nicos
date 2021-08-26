#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Ebad Kamil <ebad.kamil@ess.eu>
#
# *****************************************************************************

from enum import Enum

import numpy as np


class NormaliserType(Enum):
    NONORMALISER = 0
    INTEGRAL = 1  # area under curve


class NoNormaliser:
    def normalise(self, y, x):
        return y


class IntegralNormaliser:
    def normalise(self, y, x):
        if not np.any(y):
            # if all entries are zero return the original array
            return y
        integ = np.trapz(y, x)
        if integ == 0:
            # Don't normalize if area under curve is zero.
            return y
        return y / integ


class NormaliserFactory:
    _available_normalisers = {
        NormaliserType.NONORMALISER: NoNormaliser,
        NormaliserType.INTEGRAL: IntegralNormaliser,
    }

    @classmethod
    def create(cls, norm):
        if norm in cls._available_normalisers:
            return cls._available_normalisers[norm]()
        raise NotImplementedError(f'Unknown normaliser type: {norm}')
