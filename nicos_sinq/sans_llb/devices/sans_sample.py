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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

from nicos.core import Param

from nicos.core.params import floatrange
from nicos.devices.sample import Sample


class SANSSample(Sample):
    """Sample adding additional parameters for SANS (e.g. thickness).
    """

    parameters = {
        'thickness':  Param('Sample thickness (info only)',
                            type=floatrange(0), settable=True, unit='mm',
                            category='sample', default=0.),
    }

    def clear(self):
        Sample.clear(self)
        self.thickness = 0.

    def _applyParams(self, number, parameters):
        Sample._applyParams(self, number, parameters)
        self.thickness = parameters.get('thickness', 0.0)

    def doWriteThickness(self, value):
        params = dict(self.samples[self.samplenumber])
        if params.get('thickness', 0.0)!=value:
            params['thickness'] = value
            self.set(self.samplenumber, params)
