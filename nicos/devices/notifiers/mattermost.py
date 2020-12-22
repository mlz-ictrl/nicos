#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

import json

import requests

from nicos.core import ConfigurationError, Param
from nicos.devices.notifiers import Notifier
from nicos.utils.credentials.keystore import nicoskeystore


class Mattermost(Notifier):
    """Mattermost notifier.

    Mattermost is a group chat system similar to Slack, but open source.

    To use this notifier, some Mattermost user must register an "Incoming
    Webhook" on the Mattermost instance.  The credid parameter should be set to
    a NICOS keystore credential ID of the "secret" part of the hook URL.

    Receivers can be given as channels, using the last part of the channel's
    URL, or people, in the form ``@joe``.

    For example, if you want to send messages via a webhook with the URL
    https://chat.example.org/hooks/xsdkue8djsk
    to the user "joe" and to the channel
    https://chat.example.org/team/channels/nicos-notifications
    you would set the following configuration::

       baseurl = 'https://chat.example.org'
       credid = '...' (a keystore ID with the value 'xsdkue8djsk')
       receivers = ['nicos-notifications', '@joe']

    The `username` parameter can be set freely, Mattermost will show "bot"
    next to it to avoid spoofing actual users.
    """

    parameters = {
        'baseurl':  Param('URL of the Mattermost instance',
                          type=str, mandatory=True),
        'username': Param('User name to show for notifications',
                          type=str, mandatory=True),
        'iconurl':  Param('URL of an image to show next to notifications',
                          type=str, default=''),
        'credid':   Param('Credential ID in the NICOS keystore '
                          'for the hook ID', type=str, default='mattermost'),
    }

    _headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    def doInit(self, mode):
        hookid = nicoskeystore.getCredential(self.credid)
        if not hookid:
            raise ConfigurationError('Mattermost hook ID missing in keystore')
        self._hookurl = self.baseurl + '/hooks/' + hookid

    def send(self, subject, body, what=None, short=None, important=True):
        message = '**%s**\n\n```\n%s\n```' % (subject, body)
        if important:
            message = '@all ' + message

        for entry in self._getAllRecipients(important):
            self.log.debug('sending Mattermost message to %s', entry)
            data = {'text': message, 'username': self.username,
                    'channel': entry}
            if self.iconurl:
                data['icon_url'] = self.iconurl
            try:
                response = requests.post(self._hookurl, headers=self._headers,
                                         data=json.dumps(data), timeout=2)
                if not response.ok:
                    raise ValueError(response.json()['message'])
            except Exception as err:
                self.log.warning('Could not send Mattermost '
                                 'message to %s: %s', entry, err, exc=1)
