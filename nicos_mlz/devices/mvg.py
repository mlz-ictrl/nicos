# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
"""Show next U-Bahn departures from Garching-Forschungszentrum (or any stop)
in the MVG network."""

import time
from datetime import datetime

from nicos.core import Override, Param, oneof
from nicos.devices.entangle import VectorInput as TangoVectorInput


class MVG(TangoVectorInput):
    """Interface to the MVG tango server"""
    parameters = {
        'limit':
        Param(
            'Maximum number of departure times', type=int, settable=True,
            default=5
        ),
        'displaymode':
        Param(
            'Display mode', type=oneof('delta', 'time'), settable=True,
            default='delta'
        ),
        'deltaoffset':
        Param(
            'Only display departures at least this time in the future',
            type=float, settable=True, default=0)
    }
    parameter_overrides = {
        'unit': Override(mandatory=False, volatile=True, default='min'),
        'fmtstr': Override(default='%s'),
        'pollinterval': Override(default=60),
        'maxage': Override(default=70),
    }

    def doRead(self, maxage=0):
        raw = TangoVectorInput.doRead(self, maxage)
        now = time.time()
        if self.displaymode == 'time':
            res = [
                datetime.fromtimestamp(d).time().strftime('%H:%M') for d in raw
                if d > now+ self.deltaoffset
            ][0:self.limit]
        else:
            deltas = [d - now for d in raw if d > now + self.deltaoffset]
            res = [str(round(d / 60)) for d in deltas][0:self.limit]
        return ','.join(res)

    def doReadUnit(self):
        return 'min' if self.displaymode == 'delta' else ''
