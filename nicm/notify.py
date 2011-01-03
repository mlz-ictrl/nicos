#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Notification classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICOS notification classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import threading
import subprocess
from email.Header import Header
from email.Message import Message
from email.Charset import Charset, QP
from email.Utils import formatdate, make_msgid

try:
    import xmpp
except:
    xmpp = None

from nicm.utils import listof
from nicm.device import Device, Param

EMAIL_CHARSET = 'utf-8'
NS_XHTML = 'http://www.w3.org/1999/xhtml'


class Notifier(Device):
    """
    Interface for all notification systems.
    """

    def send(subject, body, what=None, short=None):
        raise NotImplementedError

    def sendConditionally(self, runtime, subject, body, what=None, short=None):
        # XXX implement runtime checking
        #if runtime > self.config.mail_minruntime:
        self.send(subject, body, what, short)


class Jabberer(Notifier):
    """
    Jabber notification handling.
    """

    parameters = {
        'jid':       Param('Jabber JID of the notifier', type=str,
                           mandatory=True),
        'password':  Param('Password for the given JID', type=str,
                           mandatory=True),
        'receivers': Param('List of receiver JIDs', type=listof(str),
                           settable=True),
    }

    def doInit(self):
        self._jid = xmpp.protocol.JID(self.jid)
        self._client = xmpp.Client(self._jid.getDomain(), debug=[])
        self._client.connect()
        self._client.auth(self._jid.getNode(), self.password)

    def send(self, subject, body, what=None, short=None):
        receivers = self.receivers
        self.printdebug('trying to send message to %s' % ', '.join(receivers))
        for receiver in receivers:
            try:
                msg = self._message(receiver, subject, body)
                self._client.send(msg)
            except Exception:
                self.printexception('sending to %s failed' % receiver)
        self.printinfo('%sjabber message sent to %s' %
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
    """
    E-Mail notification handling.
    """

    parameters = {
        'sender':    Param('Mail sender address', type=str, mandatory=True),
        'receivers': Param('Mail receiver addresses', type=listof(str),
                           settable=True),
        'copies':    Param('Mail copy addresses', type=listof(str)),
        # XXX take from daemon?
        'subject':   Param('Subject prefix', type=str, default='NICM'),
    }

    def send(self, subject, body, what=None, short=None):
        def send():
            receivers = self.receivers + self.copies
            if not receivers:
                return
            ok = self._sendmail(self.sender,
                                self.receivers,
                                self.copies,
                                self.subject + ' -- ' + subject, body)
            if ok:
                self.printinfo('%smail sent to %s' % (
                    what and what + ' ' or '', ', '.join(receivers)))
        mail_thread = threading.Thread(target=send)
        mail_thread.setDaemon(True)
        mail_thread.start()

    def _sendmail(self, address, to, cc, subject, text):
        """Send e-mail with given recipients, subject and text."""
        if not address:
            self.printdebug('no sender address given, not sending anything')
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

        self.printdebug('trying to send mail to %s' % ', '.join(to))
        try:
            sendmailp = os.popen('/usr/sbin/sendmail ' + ' '.join(to), 'w')
            # msg contains everything we need, so this is a simple write
            sendmailp.write(msg.as_string())
            sendmail_status = sendmailp.close()
            if sendmail_status:
                self.printerror('sendmail failed with status: %s' %
                                sendmail_status)
                return False
        except Exception:
            self.printexception('sendmail failed with an exception')
            return False
        return True


class SMSer(Notifier):
    """
    SMS notifications via smslink client program.
    """

    parameters = {
        'receivers': Param('SMS receiver phone numbers', type=listof(str),
                           settable=True),
        'server':    Param('Name of SMS server', type=str, mandatory=True),
        'subject':   Param('Body prefix', type=str, default='NICM'),
    }

    def send(self, subject, body, what=None, short=None):
        receivers = self.receivers
        if not receivers:
            return
        body = self.subject + ': ' + (short or body)
        body = body[:160]
        self.printdebug('sending SMS to %s' % ', '.join(receivers))
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
            self.printexception('sendsms failed with exception')
            return False
        self.printinfo('%sSMS message sent to %s' % (
            what and what + ' ' or '', ', '.join(receivers)))
        return True
