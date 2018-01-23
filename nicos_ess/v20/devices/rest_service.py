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
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

from nicos.core import Param, host, status, Override, CommunicationError
from nicos.devices.abstract import MappedMoveable
import requests

status_map = {
    'running': (status.OK, 'Service is up and running'),
    'stopped': (status.WARN, 'Service is not running'),
    'error': (status.ERROR, 'Error in remote service'),
}


class RestServiceClientDevice(MappedMoveable):
    parameters = {
        'host': Param('Host where REST service is running.',
                      type=host, settable=False, mandatory=True),
        'service': Param('Name of service.',
                         type=str, settable=False, mandatory=True)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
        'mapping': Override(mandatory=False, settable=False)
    }

    def _rest_request(self, endpoint):
        response = requests.get('http://{}/{}/{}'.format(self.host, endpoint,
                                                         self.service))
        jsondata = response.json()

        if 'data' in jsondata:
            return jsondata['data']

        raise CommunicationError('Error: {}'.format(jsondata['error']))

    def doReadDescription(self):
        return self._rest_request('description')

    def doStatus(self, maxage=0):
        service_status = self._rest_request('status')
        return status_map[service_status]

    def _readRaw(self, maxage=0):
        return self._rest_request('status') == 'running'

    def _startRaw(self, target):
        self._rest_request('start' if target else 'stop')

    def doReadMapping(self):
        return dict(On=True, Off=False)
