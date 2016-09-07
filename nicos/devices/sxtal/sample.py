#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   pedersen
#
# *****************************************************************************

"""
Single crystal sample device
"""

from numpy import array

from nicos.devices.sample import Sample
from nicos.core.params import Param, floatrange
from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell, SXTalCellType


class SXTalSample(Sample):
    parameters = {
                   'cell': Param('Unit cell with matrix', type=SXTalCellType,
                                 settable=True, mandatory=False,
                                 default=SXTalCell.fromabc(5)),
                  'a': Param('a', type=float, settable=False,
                             volatile=True),
                  'b': Param('b', type=float, settable=False,
                             volatile=True),
                  'c': Param('c', type=float, settable=False,
                             volatile=True),
                  'alpha': Param('alpha', type=floatrange(1., 179.), settable=False,
                                 volatile=True),
                  'beta': Param('beta', type=floatrange(1., 179.), settable=False,
                                volatile=True),
                  'gamma': Param('gamma', type=floatrange(1., 179.), settable=False,
                                 volatile=True),
                  'rmat': Param('rmat', type=array, settable=False,
                                volatile=True, default=None),
                  }

    def doReadA(self, maxage=0):
        return self.cell.cellparams().a

    def doReadB(self, maxage=0):
        return self.cell.cellparams().b

    def doReadC(self, maxage=0):
        return self.cell.cellparams().c

    def doReadAlpha(self, maxage=0):
        return self.cell.cellparams().alpha

    def doReadBeta(self, maxage=0):
        return self.cell.cellparams().beta

    def doReadGamma(self, maxage=0):
        return self.cell.cellparams().gamma

    def doReadRmat(self, maxage=0):
        return self.cell.rmat

    def doWriteCell(self, a, b=None, c=None, alpha=90.0, beta=90.0, gamma=90.0, bravais='P'):
        if isinstance(a, SXTalCell):
            self._params['cell'] = a
        elif isinstance(a, array):
            self._params['cell'] = SXTalCell(a, bravais)
        else:
            self._params['cell'] = SXTalCell.fromabc(a, b, c, alpha, beta, gamma, bravais)
        self._setROParam('a', self.doReadA(0))
        self._setROParam('b', self.doReadB(0))
        self._setROParam('c', self.doReadC(0))
        self._setROParam('alpha', self.doReadAlpha(0))
        self._setROParam('beta', self.doReadBeta(0))
        self._setROParam('gamma', self.doReadGamma(0))
