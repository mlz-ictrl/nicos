#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Forecast final values of a TACO detector."""

__version__ = "$Revision$"

from nicos.core import status, Readable, Override
from nicos.devices.generic import MultiChannelDetector


class Forecast(Readable):
    attached_devices = {
        'det': (MultiChannelDetector, 'The detector to forecast values.'),
    }

    parameter_overrides = {
        'unit':  Override(default='', mandatory=False),
    }

    def doRead(self, maxage=0):
        # read all values of all counters and store them by device
        counter_values = dict((c, c.read(maxage)[0])
                              for c in self._adevs['det']._counters)
        # go through the master channels and determine the one
        # closest to the preselection
        fraction_complete = 0
        for m in self._adevs['det']._masters:
            p = m.preselection
            fraction_complete = max(fraction_complete, counter_values[m] / p)
        # scale all counter values by that fraction
        return [v / fraction_complete for v in counter_values.itervalues()]

    def doStatus(self, maxage=0):
        return status.OK, ''

    def valueInfo(self):
        return self._adevs['det'].valueInfo()
