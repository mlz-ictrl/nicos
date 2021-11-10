#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   AUC Hardal <umit.hardal@ess.eu>
# *****************************************************************************
import os

import requests

from nicos.core import Device, Param, usermethod


class ScichatBot(Device):
    parameters = {
        'url': Param('SciChat server address', type=str, settable=False,
                     mandatory=True, userparam=False),
        'room_id': Param('SciChat room identification', type=str,
                         settable=False, mandatory=True, userparam=False)
    }

    def doInit(self, mode):
        if not self.url.startswith("https:"):
            raise ConnectionError("server URL must be https")
        self._join_room()

    def _join_room(self):
        url = f'{self.url}/join/{self.room_id}'
        try:
            self._post(url)
        except Exception as err:
            raise RuntimeError(f'could not join room: {err}') from None

    @usermethod
    def send(self, message):
        url = f'{self.url}/rooms/{self.room_id}/send/m.room.message'
        data = {"msgtype": "m.text", "body": f'{message}'}
        try:
            self._post(url, data)
        except Exception as err:
            raise RuntimeError(f'could not send message: {err}') from None

    def _post(self, url, data=None):
        response = requests.post(url, headers={
            "Authorization": f"Bearer {os.environ.get('SCICHAT_TOKEN')}"},
            json=data)
        if response.status_code != 200:
            raise RuntimeError(f'{response.reason} ({response.status_code})')
