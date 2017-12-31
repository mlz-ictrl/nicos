#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""
Single crystal sample device
"""

from nicos.core import Param, floatrange, dictof, listof, oneof
from nicos.devices.sample import Sample
from nicos.devices.sxtal.xtal.sxtalcell import SXTalCell, SXTalCellType
from nicos.devices.sxtal.xtal import symmetry


class SXTalSample(Sample):
    parameters = {
        'cell':      Param('Unit cell with matrix', type=SXTalCellType,
                           settable=True, mandatory=False,
                           default=SXTalCell.fromabc(5)),
        'a':         Param('a', type=float, category='sample'),
        'b':         Param('b', type=float, category='sample'),
        'c':         Param('c', type=float, category='sample'),
        'alpha':     Param('alpha', type=floatrange(1., 179.),
                           category='sample'),
        'beta':      Param('beta', type=floatrange(1., 179.),
                           category='sample'),
        'gamma':     Param('gamma', type=floatrange(1., 179.),
                           category='sample'),
        'rmat':      Param('rmat', type=listof(listof(float)),
                           default=None, userparam=False),
        'ubmatrix':  Param('UB matrix (rmat^T)', type=listof(listof(float)),
                           category='sample'),
        'bravais':   Param('Bravais lattice',
                           type=oneof(*symmetry.Bravais.conditions),
                           settable=True, default='P', category='sample'),
        'laue':      Param('Laue group', type=oneof(*symmetry.symbols),
                           settable=True, default='1', category='sample'),

        'peaklists': Param('Lists of peaks for scanning', userparam=False,
                           type=dictof(str, list), settable=True),
        'poslists':  Param('Lists of positions for indexing', userparam=False,
                           type=dictof(str, list), settable=True),
    }

    def clear(self):
        """Clear experiment-specific information."""
        Sample.clear(self)
        self.cell = SXTalCell.fromabc(5)
        self.peaklists = {}
        self.poslists = {}

    def new(self, parameters):
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
        a = parameters.pop('a', None)
        if a is None:
            if 'cell' not in parameters:
                self.log.warning('using dummy lattice constant of 5 A')
            a = 5.0
        b = parameters.pop('b', a)
        c = parameters.pop('c', a)
        alpha = parameters.pop('alpha', 90.0)
        beta = parameters.pop('beta', 90.0)
        gamma = parameters.pop('gamma', 90.0)
        # TODO: map spacegroup/bravais/laue with triple-axis
        bravais = parameters.pop('bravais', 'P')
        laue = parameters.pop('laue', '1')
        if 'cell' not in parameters:
            parameters['cell'] = [a, b, c, alpha, beta, gamma, bravais, laue]
        Sample.new(self, parameters)

    def _applyParams(self, number, parameters):
        Sample._applyParams(self, number, parameters)
        if 'cell' in parameters:
            self.cell = parameters['cell']

    def doReadBravais(self):
        return self.cell.bravais.bravais

    def doWriteBravais(self, value):
        self.cell.bravais = symmetry.Bravais(value)

    def doReadLaue(self):
        return self.cell.laue.laue

    def doWriteLaue(self, value):
        self.cell.laue = symmetry.Laue(value)

    def doWriteCell(self, cell):
        params = cell.cellparams()
        self._setROParam('a', params.a)
        self._setROParam('b', params.b)
        self._setROParam('c', params.c)
        self._setROParam('alpha', params.alpha)
        self._setROParam('beta', params.beta)
        self._setROParam('gamma', params.gamma)
        self._setROParam('rmat', cell.rmat.tolist())
        self._setROParam('ubmatrix', cell.rmat.T.tolist())
        self._setROParam('bravais', cell.bravais.bravais)
        self._setROParam('laue', cell.laue.laue)

        self.log.info('New sample cell set. Parameters:')
        self.log.info('a = %8.3f  b = %8.3f  c = %8.3f',
                      params.a, params.b, params.c)
        self.log.info('alpha = %8.3f  beta = %8.3f  gamma = %8.3f',
                      params.alpha, params.beta, params.gamma)
        self.log.info('Bravais: %s  Laue: %s',
                      cell.bravais.bravais, cell.laue.laue)
        self.log.info('UB matrix:')
        for row in cell.rmat.T:
            self.log.info('%8.4f %8.4f %8.4f', *row)
