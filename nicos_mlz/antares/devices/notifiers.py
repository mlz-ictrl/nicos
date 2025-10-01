# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Simon Sebold <simon.sebold@frm2.tum.de>
#
# *****************************************************************************

import requests

from nicos.core import Param
from nicos.devices.notifiers import Notifier


class TelegramNotifier(Notifier):
    """Notifier sending messages to the Telegram messenger service."""

    parameters = {
        'chatid': Param('Chat ID the bot should send the messages to.',
                        type=str, mandatory=True),
        'bottoken': Param('Bot API access token.',
                          type=str, mandatory=True),
    }

    def doInit(self, mode):
        self.log.info('notifier init')
        self._subject = self.subject

    def send(self, subject, body, what=None, short=None, important=True):

        if subject != body:
            text = f'{subject}\n{body}'
        else:
            text = subject

        url_req = f'https://api.telegram.org/bot{self.bottoken}/sendMessage?' \
                  f'chat_id={self.chatid}&text={text}'
        try:
            _ = requests.get(url_req, timeout=3)
        except Exception as e:
            self.log.warn(f'TelegramNotifier:send got error ({str(e)}).')
