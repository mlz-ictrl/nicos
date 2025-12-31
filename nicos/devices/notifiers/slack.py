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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

import html

from slack import WebClient as slackwebclient
from slack.errors import SlackApiError

from nicos.core import SIMULATION, Override, Param, secret
from nicos.devices.notifiers import Notifier


class Slacker(Notifier):
    """Slack notifications via a workspace specific app.

    To use this notifier, you can register your own Slack App (or use an
    existing one) via https://api.slack.com/apps and install it to your
    workspace. On installation you'll receive an OAuth token which needs
    to be stored in the NICOS keyring (domain: nicos). The identifier for
    the keystore entry then needs to be configured as the device parameter
    ``authtoken`` as  ``secret('...')``.
    """

    parameters = {
        'authtoken': Param('NICOS keystore secret name for the OAuth token',
                           type=secret, default='slack'),
    }

    parameter_overrides = {
        'receivers': Override(description='Slack receiver channels '
                              '(format: #channel)'),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        secret_token = self.authtoken.lookup('Slack API token not in keystore')
        self._slack = slackwebclient(secret_token)

    def send(self, subject, body, what=None, short=None, important=True):
        message = html.escape('*%s*\n\n```%s```' % (subject, body), False)

        for entry in self._getAllRecipients(important):
            self.log.debug('sending slack message to %s', entry)
            try:
                response = self._slack.chat_postMessage(channel=entry,
                                                        text=message)
                if response['ok']:
                    continue
            except SlackApiError as e:
                error = e.response['error']

            self.log.warning('Could not send slack message to %s: %s',
                             entry, error)
