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

from nicos.core import Param, floatrange
from nicos.devices.sample import Sample

from nicos_sinq.sxtal.cell import Cell


class PowderSample(Sample):
    """Powder sample with the mur parameter used at SINQ."""
    parameters = {
        'mur': Param('Sample muR', type=floatrange(.0, 1.), settable=True,
                     category='sample'),
    }


class CrystalSample(Sample):
    """Crystal sample, allows to define the set of parameters according to the
    NeXus NXCrystal definition"""

    parameters = {
        'a':         Param('a', type=float, category='sample', settable=True),
        'b':         Param('b', type=float, category='sample', settable=True),
        'c':         Param('c', type=float, category='sample', settable=True),
        'alpha':     Param('alpha', type=floatrange(1., 179.), settable=True,
                           category='sample'),
        'beta':      Param('beta', type=floatrange(1., 179.), settable=True,
                           category='sample'),
        'gamma':     Param('gamma', type=floatrange(1., 179.), settable=True,
                           category='sample'),
    }

    def new(self, parameters):
        self.clear()
        self._prepare_new(parameters)
        Sample.new(self, parameters)

    def _prepare_new(self, parameters):
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
        aa = parameters.pop('a', None)
        if aa is None:
            if 'cell' not in parameters:
                self.log.warning('using dummy lattice constant of 6.28 A')
            aa = 6.28
        self.a = aa
        self.b = parameters.pop('b', self.a)
        self.c = parameters.pop('c', self.a)
        self.alpha = parameters.pop('alpha', 90.0)
        self.beta = parameters.pop('beta', 90.0)
        self.gamma = parameters.pop('gamma', 90.0)

    def getCell(self):
        return Cell(self.a, self.b, self.c,
                    self.alpha, self.beta, self.gamma)
