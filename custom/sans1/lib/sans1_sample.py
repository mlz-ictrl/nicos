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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Sans1 Sample device."""

from nicos import session
from nicos.core import Override
from nicos.devices.sample import Sample as NicosSample


class Sans1Sample(NicosSample):
    """A special device to represent a sample.

    Represent a set of samples with a currently activated one.
    """

    parameter_overrides = {
        # We want this to occur in the data files.
        'samplenumber': Override(category='sample'),
    }

    def new(self, parameters):
        if self.samplenumber is None:
            NicosSample.new(self, parameters)
        else:
            self.set(self.samplenumber, parameters)
            self._applyParams(self.samplenumber, parameters)

    def _applyParams(self, number, parameters):
        if number > 0:
            # move sample changer to new position!
            sc = session.getDevice('SampleChanger')
            sc.maw(number)
        NicosSample._applyParams(self, number, parameters)
