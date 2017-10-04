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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS notification classes."""

import subprocess
from time import time as currenttime

from nicos.core import Device, Param, listof, mailaddress, oneof, tupleof, \
    usermethod, floatrange, ConfigurationError
from nicos.pycompat import text_type, escape_html
from nicos.utils import createThread, createSubprocess
from nicos.utils.emails import sendMail
from nicos.utils.credentials.keystore import nicoskeystore

try:
    import slackclient
except ImportError:
    slackclient = None


class Notifier(Device):
    """Base class for all notification systems.

    Do not use directly.
    """

    parameters = {
        'minruntime': Param('Minimum runtime of a command before a failure '
                            'is sent over the notifier', type=float, unit='s',
                            default=300, settable=True),
        'ratelimit':  Param('Minimum time between sending two notifications',
                            default=60, type=floatrange(30), unit='s',
                            settable=True),
    }

    _lastsent = 0

    def _checkRateLimit(self):
        """Implement rate limiting."""
        ct = currenttime()
        if ct - self._lastsent < self.ratelimit:
            self.log.info('rate limiting: not sending notification')
            return False
        self._lastsent = ct
        return True

    @usermethod
    def send(self, subject, body, what=None, short=None, important=True):
        """Send a notification."""
        raise NotImplementedError('send() must be implemented in subclasses')

    @usermethod
    def sendConditionally(self, runtime, subject, body, what=None, short=None,
                          important=True):
        """Send a notification if the given runtime is large enough."""
        if runtime > self.minruntime:
            self.send(subject, body, what, short, important)

    def reset(self):
        """Reset experiment-specific configuration.  Does nothing by default."""


class Mailer(Notifier):
    """Sends notifications via e-mail.

    If a Mailer is configured as a notifier (the Mailer device is in the list
    of `notifiers` in the `sysconfig` entry), the receiver addresses (not
    copies) can be set by `.SetMailReceivers`.
    """

    parameters = {
        'mailserver': Param('Mail server', type=str, default='localhost',
                            settable=True),
        'sender':     Param('Mail sender address', type=mailaddress,
                            mandatory=True),
        'receivers':  Param('Mail receiver addresses', type=listof(mailaddress),
                            settable=True),
        'copies':     Param('Addresses that get a copy of messages, a list of '
                            'tuples: (mailaddress, messagelevel: "all" or '
                            '"important")',
                            type=listof(tupleof(mailaddress,
                                                oneof('all', 'important'))),
                            settable=True),
        'subject':    Param('Subject prefix', type=str, default='NICOS'),
    }

    def reset(self):
        self.log.info('mail receivers cleared')
        self.receivers = []

    def send(self, subject, body, what=None, short=None, important=True):
        def send():
            receivers = list(self.receivers)
            receivers.extend(addr for (addr, level) in self.copies
                             if level == 'all' or important)
            if not receivers:
                return
            ret = sendMail(self.mailserver, receivers, self.sender,
                           self.subject + ' -- ' + subject, body)
            if not ret:  # on error, ret is a list of errors
                self.log.info('%smail sent to %s',
                              what and what + ' ' or '', ', '.join(receivers))
            else:
                self.log.warning('sending mail failed: %s', ', '.join(ret))
        if not self._checkRateLimit():
            return
        createThread('mail sender', send)


# Implements the GSM03.38 encoding for SMS messages, including escape-encoded
# chars, generated from ftp://ftp.unicode.org/Public/MAPPINGS/ETSI/GSM0338.TXT

GSM0338_MAP = {
    u'\x0c': '\x1b\n', u' ': ' ', u'\xa3': '\x01', u'$': '\x02', u'\xa7': '_',
    u'\u03a9': '\x15', u'(': '(', u',': ',', u'0': '0', u'4': '4', u'8': '8',
    u'<': '<', u'\xbf': '`', u'D': 'D', u'H': 'H', u'L': 'L',
    u'P': 'P', u'T': 'T', u'X': 'X', u'\\': '\x1b/', u'\xdf': '\x1e', u'd': 'd',
    u'\xe7': '\t', u'h': 'h', u'l': 'l', u'p': 'p', u't': 't', u'x': 'x',
    u'|': '\x1b@', u'\u039e': '\x1a', u'\xa0': '\x1b', u'#': '#', u'\xa4': '$',
    u"'": "'", u'\u03a6': '\x12', u'+': '+', u'\u20ac': '\x1be', u'/': '/',
    u'3': '3', u'7': '7', u';': ';', u'?': '?', u'C': 'C', u'\xc4': '[',
    u'G': 'G', u'K': 'K', u'O': 'O', u'S': 'S', u'W': 'W', u'\xd8': '\x0b',
    u'[': '\x1b<', u'\xdc': '^', u'_': '\x11', u'\xe0': '\x7f', u'c': 'c',
    u'\xe4': '{', u'g': 'g', u'\xe8': '\x04', u'k': 'k', u'\xec': '\x07',
    u'o': 'o', u's': 's', u'w': 'w', u'\xf8': '\x0c', u'{': '\x1b(',
    u'\xfc': '~', u'\n': '\n', u'\u0393': '\x13', u'\u039b': '\x14',
    u'\xa1': '@', u'\u03a3': '\x18', u'"': '"', u'\xa5': '\x03', u'&': '&',
    u'*': '*', u'.': '.', u'2': '2', u'6': '6', u':': ':', u'>': '>',
    u'B': 'B', u'\xc5': '\x0e', u'F': 'F', u'\xc9': '\x1f', u'J': 'J',
    u'N': 'N', u'\xd1': ']', u'R': 'R', u'V': 'V', u'Z': 'Z', u'^': '\x1b\x14',
    u'b': 'b', u'\xe5': '\x0f', u'f': 'f', u'\xe9': '\x05', u'j': 'j',
    u'n': 'n', u'\xf1': '}', u'r': 'r', u'v': 'v', u'\xf9': '\x06', u'z': 'z',
    u'~': '\x1b=', u'\r': '\r', u'\u0394': '\x10', u'\u0398': '\x19', u'!': '!',
    u'\u03a0': '\x16', u'%': '%', u')': ')', u'\u03a8': '\x17', u'-': '-',
    u'1': '1', u'5': '5', u'9': '9', u'=': '=', u'A': 'A', u'E': 'E',
    u'\xc6': '\x1c', u'I': 'I', u'M': 'M', u'Q': 'Q', u'U': 'U', u'\xd6': '\\',
    u'Y': 'Y', u']': '\x1b>', u'a': 'a', u'e': 'e', u'\xe6': '\x1d', u'i': 'i',
    u'm': 'm', u'q': 'q', u'\xf2': '\x08', u'u': 'u', u'\xf6': '|', u'y': 'y',
    u'}': '\x1b)'
}


class SMSer(Notifier):
    """SMS notifications via smslink client program (sendsms)."""

    parameters = {
        'receivers': Param('SMS receiver phone numbers', type=listof(str),
                           settable=True),
        'server':    Param('Name of SMS server', type=str, mandatory=True),
        'subject':   Param('Body prefix', type=str, default='NICOS'),
    }

    def _transcode(self, string):
        """Re-encode UTF-8 string into SMS encoding (GSM 03.38)."""
        if not isinstance(string, text_type):
            string = string.decode('utf-8')
        return ''.join(GSM0338_MAP.get(c, '') for c in string)

    def send(self, subject, body, what=None, short=None, important=True):
        if not important:
            return
        receivers = self.receivers
        if not receivers:
            return
        if not self._checkRateLimit():
            return
        body = self.subject + ': ' + (short or body)
        body = self._transcode(body)[:160]
        self.log.debug('sending SMS to %s', ', '.join(receivers))
        try:
            for receiver in receivers:
                proc = createSubprocess(['sendsms', '-Q', '-d', receiver,
                                         '-m', body, self.server],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                out = proc.communicate()[0]
                if 'message queued' not in out and \
                   'message successfully sent' not in out:
                    raise RuntimeError('unexpected output %r' % out.strip())
        except Exception:
            self.log.exception('sendsms failed')
            return False
        self.log.info('%sSMS message sent to %s',
                      what and what + ' ' or '', ', '.join(receivers))
        return True


class Slacker(Notifier):
    """Slack notifications via a workspace specific app.

    To use this notifier, you can register your own Slack App (or use an
    existing one) via https://api.slack.com/apps and install it to your
    workspace. On installation you'll receive an OAuth token which needs
    to be stored in the nicos keyring (domain: nicos) using the
    ``keystoretoken`` as identifier.
    """

    parameters = {
        'receivers': Param('Slack receiver channels (format: #channel)',
                           type=listof(str), settable=True),
        'keystoretoken': Param('Id used in the keystore for the OAuth token',
                               type=str, default='slack'),
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

        for entry in self.receivers:
            self.log.debug('Send slack message to %s' % entry)
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
