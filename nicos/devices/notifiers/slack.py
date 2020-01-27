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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import slackclient

from nicos.core import ConfigurationError, Override, Param
from nicos.devices.notifiers import Notifier
from nicos.pycompat import escape_html
from nicos.utils.credentials.keystore import nicoskeystore


class Slacker(Notifier):
    """Slack notifications via a workspace specific app.

    To use this notifier, you can register your own Slack App (or use an
    existing one) via https://api.slack.com/apps and install it to your
    workspace. On installation you'll receive an OAuth token which needs
    to be stored in the nicos keyring (domain: nicos) using the
    ``keystoretoken`` as identifier.
    """

    parameters = {
        'keystoretoken': Param('Id used in the keystore for the OAuth token',
                               type=str, default='slack'),
    }

    parameter_overrides = {
        'receivers': Override(description='Slack receiver channels '
                              '(format: #channel)'),
    }

    def doInit(self, mode):
        if slackclient is None:
            raise ConfigurationError('slackclient package is missing')

        token = nicoskeystore.getCredential(self.keystoretoken)
        if not token:
            raise ConfigurationError('Slack API token missing in keyring')
        self._slack = slackclient.SlackClient(token)

    def send(self, subject, body, what=None, short=None, important=True):
        message = escape_html('*%s*\n\n```%s```' % (subject, body), False)

        for entry in self._getAllRecipients(important):
            self.log.debug('sending slack message to %s' % entry)
            try:
                reply = self._slack.api_call('chat.postMessage', channel=entry,
                                             text=message)
                if reply['ok']:
                    continue
                error = reply['error']
            except Exception as e:
                error = str(e)

            self.log.warning('Could not send slack message to %s: %s' %
                             (entry, error))
