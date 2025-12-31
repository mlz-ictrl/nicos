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
#   Petr Čermák <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""Show next bus departure from Kuchynka in the PID network."""

import json
import urllib

from nicos.core import NicosError, Override, Param, Readable, status

URL = ('https://ext.crws.cz/api/ABCz/departureTables?from=%s')


class Bus(Readable):

    parameters = {
        'station':     Param('Name of the bus station',
                             type=str, settable=True,
                             default='Kuchyňka'),
        'destination': Param('Name of destination',
                             type=str, settable=True,
                             default=None),
    }

    parameter_overrides = {
        'unit':         Override(mandatory=False, default='min'),
        'fmtstr':       Override(default='%s'),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=70),
    }

    def doRead(self, maxage=0):
        try:
            response = urllib.urlopen(URL % self.station)
            data = json.loads(response.read())
            if self.destination is None:
                return ', '.join([d['dateTime'].split()[1]
                                  for d in data['records']][:4])
            else:
                return ', '.join([d['dateTime'].split()[1]
                                  for d in data['records']
                                  if d['destination'] == self.destination][:4])
        except Exception as err:
            raise NicosError(self, 'PID site not responding or changed format:'
                             ' %s' % err) from err

    def doStatus(self, maxage=0):
        return status.OK, ''
