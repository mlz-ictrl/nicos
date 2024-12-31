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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS Sample device."""

from nicos.core import Param, none_or
from nicos.core.mixins import DeviceMixinBase
from nicos.devices.sample import Sample as NicosSample
from nicos.devices.tas import TASSample as NicosTASSample


class MLZSampleMixin(DeviceMixinBase):
    """Special mixin with MLZ-specific sample ID from the sample tracker. """

    parameters = {
        'sampleid': Param('Sample ID from the sample tracker',
                          type=none_or(int), settable=True,
                          category='sample'),
    }

    def clear(self):
        """Clear sample tracker information."""
        self.sampleid = None

    def _applyParams(self, number, parameters):
        """Apply sample tracker id."""
        self.sampleid = parameters.get('id')


class Sample(MLZSampleMixin, NicosSample):
    """A special device to represent a sample.

    This has the MLZ-specific sample ID from the sample tracker.
    """

    def clear(self):
        """Clear experiment-specific information."""
        NicosSample.clear(self)
        MLZSampleMixin.clear(self)

    def _applyParams(self, number, parameters):
        """Apply sample parameters."""
        NicosSample._applyParams(self, number, parameters)
        MLZSampleMixin._applyParams(self, number, parameters)


class TASSample(MLZSampleMixin, NicosTASSample):
    """A special device to represent a TAS sample.

    This has the MLZ-specific sample ID from the sample tracker.
    """

    def clear(self):
        """Clear experiment-specific information."""
        NicosTASSample.clear(self)
        MLZSampleMixin.clear(self)

    def _applyParams(self, number, parameters):
        """Apply sample parameters."""
        NicosTASSample._applyParams(self, number, parameters)
        MLZSampleMixin._applyParams(self, number, parameters)
