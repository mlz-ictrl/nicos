# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""VTOFTOF sample device."""

from nicos.core import Override, Param, intrange
from nicos_mlz.toftof.devices.sample import Sample as BaseSample


class Sample(BaseSample):

    parameters = {
        'sampletype': Param('Sample type: '
                            '0 - Vanadium '
                            '1 - Empty cell '
                            '2 - Water ',
                            type=intrange(0, 2), userparam=True,
                            settable=True),
    }

    parameter_overrides = {
        'samples': Override(mandatory=True, settable=False, internal=False),
    }

    def _applyParams(self, number, parameters):
        BaseSample._applyParams(self, number, parameters)
        for key, value in parameters.items():
            if key in ['sampletype', 'nature', 'type']:
                setattr(self, key, value)
