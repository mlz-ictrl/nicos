#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

from nicos.core import Readable, Param, intrange
from nicos.devices.tango import PyTangoDevice


class MeanTemp(PyTangoDevice, Readable):
    """Returns mean temperature of some channels of a MawiTherm VectorInput."""

    parameters = {
        'first': Param('First channel to include', type=intrange(1, 8),
                       default=1, settable=True),
        'last':  Param('Last channel to include', type=intrange(1, 8),
                       default=8, settable=True),
    }

    def doRead(self, maxage=0):
        if self.first > self.last:
            return 0
        allchannels = self._dev.value[self.first - 1:self.last]
        return float(sum(allchannels) / len(allchannels))
