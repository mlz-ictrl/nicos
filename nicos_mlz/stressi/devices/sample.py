# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Stressi sample device."""

from math import pi

from nicos.core.mixins import DeviceMixinBase
from nicos.core.params import Param, floatrange, nonzero, oneof, vec3
from nicos.devices.tas.spacegroups import sg_by_hm

from nicos_mlz.devices.sample import Sample as BaseSample


class PowderSampleMixin(DeviceMixinBase):

    parameters = {
        'lattice': Param('Lattice constants',
                         type=vec3, settable=True,
                         default=[2 * pi, 2 * pi, 2 * pi], unit='A',
                         category='sample'),
        'angles': Param('Lattice angles',
                        type=vec3, settable=True, unit='deg',
                        default=[90, 90, 90], category='sample'),
        'spacegroup': Param('Space group of the sample', settable=True,
                            type=oneof(*range(1, 231), *sg_by_hm),
                            category='sample'),
        'mass': Param('Sample mass',
                      type=nonzero(floatrange(0)), settable=True,
                      unit='g', default=1, category='sample'),
        'density': Param('Density of the sample material',
                         type=nonzero(floatrange(0)), settable=True,
                         unit='g/cm^3', default=1, category='sample'),
    }

    parameters['spacegroup'].ext_desc = """
The spacegroup is either the number between 1 and 230 or the Hermann–Mauguin
(H-M) notation.

.. seealso::

   https://en.wikipedia.org/wiki/List_of_space_groups

   https://en.wikipedia.org/wiki/Hermann%E2%80%93Mauguin_notation
"""


class Sample(PowderSampleMixin, BaseSample):

    def _applyParams(self, number, parameters):
        BaseSample._applyParams(self, number, parameters)
        for key, value in parameters.items():
            if key in ['lattice', 'angles', 'spacegroup', 'mass', 'density']:
                setattr(self, key, value)
