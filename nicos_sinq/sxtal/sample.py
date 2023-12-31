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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

"""
Single crystal sample device
"""

import numpy as np

from nicos import session
from nicos.core import Attach, Param, listof, oneof
from nicos.core.errors import InvalidValueError
from nicos.devices.sxtal.xtal import symmetry

from nicos_sinq.devices.sample import CrystalSample
from nicos_sinq.sxtal.cell import calculateBMatrix
from nicos_sinq.sxtal.instrument import TASSXTal
from nicos_sinq.sxtal.reflist import ReflexList


class SXTalSample(CrystalSample):
    parameters = {
        'ubmatrix':  Param('UB matrix', type=listof(float),
                           category='sample', settable=True,
                           userparam=True),
        'bravais':   Param('Bravais lattice',
                           type=oneof(*symmetry.Bravais.conditions),
                           settable=True, default='P', category='sample'),
        'laue':      Param('Laue group', type=oneof(*symmetry.symbols),
                           settable=True, default='1', category='sample'),
        'reflist': Param('The name of the default reflection '
                         'list to operate upon',
                         type=str,
                         userparam=True),
    }

    attached_devices = {
        'reflists': Attach('List of available reflection lists',
                           devclass=ReflexList,
                           multiple=True,
                           optional=False),
    }

    def clear(self):
        """Clear experiment-specific information."""
        CrystalSample.clear(self)
        self.ubmatrix = None
        for rfl in self._attached_reflists:
            rfl.clear()

    def _prepare_new(self, parameters):
        CrystalSample._prepare_new(self, parameters)
        self.bravais = parameters.pop('bravais', 'P')
        self.laue = parameters.pop('laue', '1')
        self.ubmatrix = list(self.getUB().flatten())

    def doWriteUbmatrix(self, ub):
        if not ub:
            return
        if not isinstance(ub, list):
            raise ValueError('Expecting list of 9 values')
        if len(ub) != 9:
            raise ValueError('Expected 9 values')

    def doWriteReflist(self, name):
        if name not in self._adevs:
            raise InvalidValueError('% is no known reflection list' % name)
        if not isinstance(self._adevs[name], ReflexList):
            raise InvalidValueError('%s is not a reflection list' % name)

    def getUB(self):
        if self.ubmatrix:
            ub = np.array(self.ubmatrix, dtype='float64')
            ub = ub.reshape((3, 3))
            return ub
        # Return B instead when no UB available
        cell = self.getCell()
        ub = calculateBMatrix(cell)
        if isinstance(session.experiment, TASSXTal):
            return ub
        else:
            return ub/(2. * np.pi)

    def getRefList(self, name=None):
        if not name:
            name = self.reflist
        for reflist in self._attached_reflists:
            if reflist.name == name:
                return reflist
