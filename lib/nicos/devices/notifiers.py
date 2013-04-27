#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

import os
import threading
import subprocess
from email.header import Header
from email.message import Message
from email.charset import Charset, QP
from email.utils import formatdate, make_msgid

try:
    import xmpp
except ImportError:
    xmpp = None

from nicos.core import listof, mailaddress, usermethod, Device, Param

EMAIL_CHARSET = 'utf-8'
NS_XHTML = 'http://www.w3.org/1999/xhtml'


class Notifier(Device):
    """Base class for all notification systems.

    Do not use directly.
    """

    parameters = {
        'minruntime': Param('Minimum runtime of a command before a failure '
                            'is sent over the notifier', type=float, unit='s',
                            default=300, settable=True),
    }

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


class Jabberer(Notifier):
    """Notifier to send Jabber/XMPP notifications.

    Needs the Python xmpp module.
    """

    parameters = {
        'jid':       Param('Jabber JID of the notifier', type=str,
                           mandatory=True),
        'password':  Param('Password for the given JID', type=str,
                           mandatory=True),
        'receivers': Param('List of receiver JIDs', type=listof(str),
                           settable=True),
    }

    def doInit(self, mode):
        self._jid = xmpp.protocol.JID(self.jid)
        self._client = xmpp.Client(self._jid.getDomain(), debug=[])
        self._client.connect()
        self._client.auth(self._jid.getNode(), self.password)

    def send(self, subject, body, what=None, short=None, important=True):
        receivers = self.receivers
        self.log.debug('trying to send message to %s' % ', '.join(receivers))
        for receiver in receivers:
            try:
                msg = self._message(receiver, subject, body)
                self._client.send(msg)
            except Exception:
                self.log.exception('sending to %s failed' % receiver)
        self.log.info('%sjabber message sent to %s' %
                       what and what + ' ' or '', ', '.join(receivers))

    def _message(self, receiver, subject, body):
        """Create a message with the content as nicely formatted HTML in it."""
        plaintext = subject + '\n\n' + body
        msg = xmpp.protocol.Message(receiver, plaintext)
        html = msg.addChild('html', namespace=xmpp.protocol.NS_XHTML_IM)
        htmlbody = html.addChild('body', namespace=NS_XHTML)
        p = htmlbody.addChild('p')
        p.addChild('strong', payload=[subject])
        p.addChild('br')
        p.addData(body)
        return msg


class Mailer(Notifier):
    """Sends notifications via e-mail.

    If a Mailer is configured as a notifier, the receiver addresses (not copies)
    can be set by `.SetMailReceivers`.
    """

    parameters = {
        'sender':    Param('Mail sender address', type=mailaddress, mandatory=True),
        'receivers': Param('Mail receiver addresses', type=listof(mailaddress),
                           settable=True),
        'copies':    Param('Mail copy addresses', type=listof(mailaddress),
                           settable=True),
        'subject':   Param('Subject prefix', type=str, default='NICOS'),
    }

    def reset(self):
        self.log.info('mail receivers cleared')
        self.receivers = []

    def send(self, subject, body, what=None, short=None, important=True):
        def send():
            if not self.receivers:
                return
            receivers = self.receivers + self.copies
            ok = self._sendmail(self.sender,
                                self.receivers,
                                important and self.copies or [],
                                self.subject + ' -- ' + subject, body)
            if ok:
                self.log.info('%smail sent to %s' % (
                    what and what + ' ' or '', ', '.join(receivers)))
        mail_thread = threading.Thread(target=send, name='mail sender')
        mail_thread.setDaemon(True)
        mail_thread.start()

    def _sendmail(self, address, to, cc, subject, text):
        """Send e-mail with given recipients, subject and text."""
        if not address:
            self.log.debug('no sender address given, not sending anything')
            return False
        if isinstance(subject, unicode):
            subject = subject.encode(EMAIL_CHARSET)

        # Create a text/plain body using CRLF (see RFC2822)
        text = text.replace(u'\n', u'\r\n')
        if isinstance(text, unicode):
            text = text.encode(EMAIL_CHARSET)

        # Create a message using EMAIL_CHARSET and quoted printable
        # encoding, which should be supported better by mail clients.
        msg = Message()
        charset = Charset(EMAIL_CHARSET)
        charset.header_encoding = QP
        charset.body_encoding = QP
        msg.set_charset(charset)

        # work around a bug in python 2.4.3 and above:
        msg.set_payload('=')
        if msg.as_string().endswith('='):
            text = charset.body_encode(text)

        msg.set_payload(text)

        # Create message headers
        msg['From'] = address
        msg['To'] = ','.join(to)
        msg['CC'] = ','.join(cc)
        msg['Date'] = formatdate()
        msg['Message-ID'] = make_msgid()
        msg['Subject'] = Header(subject, charset)
        # Set Return-Path so that it isn't set (generally incorrectly) for us.
        msg['Return-Path'] = address

        self.log.debug('trying to send mail to %s' % ', '.join(to + cc))
        try:
            sendmailp = os.popen('/usr/sbin/sendmail ' + ' '.join(to + cc), 'w')
            # msg contains everything we need, so this is a simple write
            sendmailp.write(msg.as_string())
            sendmail_status = sendmailp.close()
            if sendmail_status:
                self.log.error('sendmail failed with status: %s' %
                                sendmail_status)
                return False
        except Exception:
            self.log.exception('sendmail failed with an exception')
            return False
        return True


class SMSer(Notifier):
    """SMS notifications via smslink client program.

    If a SMSer is configured as a notifier, the receiver addresses (not copies)
    can be set by `.SetSMSReceivers`.
    """

    parameters = {
        'receivers': Param('SMS receiver phone numbers', type=listof(str),
                           settable=True),
        'server':    Param('Name of SMS server', type=str, mandatory=True),
        'subject':   Param('Body prefix', type=str, default='NICOS'),
    }

    def send(self, subject, body, what=None, short=None, important=True):
        if not important:
            return
        receivers = self.receivers
        if not receivers:
            return
        body = self.subject + ': ' + (short or body)
        body = body[:160]
        self.log.debug('sending SMS to %s' % ', '.join(receivers))
        try:
            for receiver in receivers:
                proc = subprocess.Popen(['sendsms', '-d', receiver, '-m', body,
                                         self.server],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                out = proc.communicate()[0]
                if 'message queued' not in out:
                    raise RuntimeError(out.strip())
        except Exception:
            self.log.exception('sendsms failed with exception')
            return False
        self.log.info('%sSMS message sent to %s' % (
            what and what + ' ' or '', ', '.join(receivers)))
        return True
