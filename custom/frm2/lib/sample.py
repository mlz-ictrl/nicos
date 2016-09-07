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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS Sample device."""

from nicos.core import Param, none_or
from nicos.devices.sample import Sample as NicosSample


class Sample(NicosSample):
    """A special device to represent a sample.

    This has the MLZ-specific sample ID from the sample tracker.
    """

    parameters = {
        'sampleid':     Param('Sample ID from the sample tracker',
                              type=none_or(int), settable=True,
                              category='sample'),
    }

    def clear(self):
        """Clear experiment-specific information."""
        NicosSample.clear(self)
        self.sampleid = None

    def _applyParams(self, number, parameters):
        """Apply sample parameters."""
        NicosSample._applyParams(self, number, parameters)
        self.sampleid = parameters.get('id')
