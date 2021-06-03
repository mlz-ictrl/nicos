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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

"""
Single crystal sample device
"""

import numpy as np

from nicos import session
from nicos.core import Attach, Param, floatrange, listof, oneof
from nicos.core.errors import InvalidValueError
from nicos.devices.sample import Sample
from nicos.devices.sxtal.xtal import symmetry

from nicos_sinq.sxtal.cell import Cell, calculateBMatrix
from nicos_sinq.sxtal.instrument import TASSXTal
from nicos_sinq.sxtal.reflist import ReflexList


class SXTalSample(Sample):
    parameters = {
        'a':         Param('a', type=float, category='sample',
                           settable=True),
        'b':         Param('b', type=float, category='sample',
                           settable=True),
        'c':         Param('c', type=float, category='sample',
                           settable=True),
        'alpha':     Param('alpha', type=floatrange(1., 179.),
                           category='sample',
                           settable=True),
        'beta':      Param('beta', type=floatrange(1., 179.),
                           category='sample',
                           settable=True),
        'gamma':     Param('gamma', type=floatrange(1., 179.),
                           category='sample',
                           settable=True),
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
        Sample.clear(self)
        self.ubmatrix = None
        for rfl in self._attached_reflists:
            rfl.clear()

    def new(self, parameters):
        self.clear()
        # pylint: disable=pointless-string-statement
        """Accepts several ways to spell new cell params."""
        lattice = parameters.pop('lattice', None)
        if lattice is not None:
            try:
                parameters['a'], parameters['b'], parameters['c'] = lattice
            except Exception:
                self.log.warning('invalid lattice spec ignored, should be '
                                 '[a, b, c]')
        angles = parameters.pop('angles', None)
        if angles is not None:
            try:
                parameters['alpha'], parameters['beta'], \
                    parameters['gamma'] = angles
            except Exception:
                self.log.warning('invalid angles spec ignored, should be '
                                 '[alpha, beta, gamma]')
        self.a = parameters.pop('a', None)
        if self.a is None:
            if 'cell' not in parameters:
                self.log.warning('using dummy lattice constant of 5 A')
            self.a = 5.0
        self.b = parameters.pop('b', self.a)
        self.c = parameters.pop('c', self.a)
        self.alpha = parameters.pop('alpha', 90.0)
        self.beta = parameters.pop('beta', 90.0)
        self.gamma = parameters.pop('gamma', 90.0)
        self.bravais = parameters.pop('bravais', 'P')
        self.laue = parameters.pop('laue', '1')
        Sample.new(self, parameters)

    def _applyParams(self, number, parameters):
        Sample._applyParams(self, number, parameters)

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

    def getCell(self):
        return Cell(self.a, self.b, self.c,
                    self.alpha, self.beta, self.gamma)

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
