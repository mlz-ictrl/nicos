#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import requests

from nicos.core import Readable, Param, tupleof, status, Override, oneof
from nicos.core.mixins import HasCommunication
from nicos.core.errors import CommunicationError


class HttpConnector(HasCommunication, Readable):
    """ Device to connect to the HTTP Server using HTTP Basic Authentication.
    *baseurl* provided in the parameters is prepended while connecting to the
    server using GET or POST. Parameter *base64auth* provides a way to
    authenticate the connection.
    """
    parameters = {
        'baseurl': Param('Base request URL to be used',
                         type=str, mandatory=True),
        'base64auth': Param('HTTP authentication encoded in base64',
                            type=str, mandatory=True),
        'byteorder': Param('Endianness of the raw data on server(big/little)',
                           type=oneof('big', 'little'),
                           default='little'),
        'curstatus': Param('Current status of the connection (readonly)',
                           type=tupleof(int, str), settable=True,
                           userparam=False)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, userparam=False, settable=False)
    }

    status_code_msg = {
        400: 'Bad request',
        403: 'Authentication did not work..',
        404: 'Somehow, address was not found!',
        500: 'Internal server error',
    }

    def doInit(self, mode):
        # Check if the base url is available
        self._com_retry(None, requests.get, self.baseurl,
                        headers=self._get_auth())

    def _get_auth(self):
        return {"Authorization": "Basic %s" % self.base64auth}

    def _com_return(self, result, info):
        # Check if the communication was successful
        response = result.status_code
        if response in self.status_code_msg:
            raise CommunicationError(self.status_code_msg.get(response))
        elif response != 200:
            raise CommunicationError('Error while connecting to server!')
        self._setROParam('curstatus', (status.OK, ''))
        return result

    def _com_raise(self, err, info):
        self._setROParam('curstatus', (status.ERROR, 'Communication Error!'))
        HasCommunication._com_raise(self, err, info)

    def _com_warn(self, retries, name, err, info):
        self._com_raise(err, info)

    def doRead(self, maxage=0):
        return ''

    def doStatus(self, maxage=0):
        return self.curstatus

    def get(self, name='', params=()):
        """Connect to *baseurl/name* using the GET protocol
        :param name: String to be appended to the *baseurl*
        :param params: GET parameters to be passed
        :return: (requests.Response) response
        """
        return self._com_retry(None, requests.get, self.baseurl + '/' + name,
                               headers=self._get_auth(), params=params)

    def post(self, name='', data=()):
        """Connect to *baseurl/name* using the POST protocol
        :param name: String to be appended to the *baseurl*
        :param data: POST parameters to be passed
        :return: (requests.Response) response
        """
        return self._com_retry(None, requests.post, self.baseurl + '/' + name,
                               headers=self._get_auth(), data=data)
