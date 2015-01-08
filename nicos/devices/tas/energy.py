#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

from math import pi, sqrt

THZ2MEV = 4.1356675
ANG2MEV = 81.804165


UNITS = {'A':   'lambda',
         'A-1': 'k',
         'meV': 'meV',
         'THz': 'THz'}

class Energy(object):
    """Energy class."""

    def __init__(self, value, unit=None):
        if isinstance(value, Energy):
            value, unit = value.value, value.unit
        if unit not in UNITS:
            raise ValueError('unknown energy unit: %r' % unit)
        self.value = value
        self.unit = unit

    def __repr__(self):
        return '%.5g %s' % (self.value, self.unit)

    def as_meV(self):
        if self.unit == 'meV':
            return self.value
        elif self.unit == 'THz':
            return self.value * THZ2MEV
        elif self.unit == 'A-1':
            return ANG2MEV / (2*pi)**2 * self.value**2
        elif self.unit == 'A':
            return ANG2MEV / self.value**2
        raise ValueError('impossible energy unit: %r' % self.unit)

    def as_THz(self):
        return self.as_meV() / THZ2MEV

    def as_k(self):
        return 2*pi * sqrt(self.as_meV() / ANG2MEV)

    def as_lambda(self):
        return sqrt(ANG2MEV / self.as_meV())

    def __float__(self):
        return float(self.value)

    def asUnit(self, unit):
        """Return a new Energy that represents this energy with another unit."""
        return getattr(self, 'as_%s' % UNITS[unit])()

    def storable(self):
        """Dictionary representation."""
        return {'unit': self.unit, 'e': self.value}

    def __getstate__(self):
        return self.storable()

    def __setstate__(self, state):
        self.__dict__.update(state)
