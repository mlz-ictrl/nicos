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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS demo notification classes:

* using the freedesktop notification protocol.
* using Jabber.
"""

try:
    import xmpp  # pylint: disable=F0401
except ImportError:
    xmpp = None

from nicos import session
from nicos.core import listof, Param
from nicos.devices.notifiers import Notifier

NS_XHTML = 'http://www.w3.org/1999/xhtml'


class DBusNotifier(Notifier):

    def send(self, subject, body, what=None, short=None, important=True):
        from nicos.guisupport.qt import QVariant, QtDBus

        dbus_interface = QtDBus.QDBusInterface(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
        )
        dbus_interface.call('Notify',
                            'NICOS',                  # app_name
                            QVariant(QVariant.UInt),  # replaces_id
                            'dialog-error',           # app_icon
                            subject,                  # summary
                            body,                     # body
                            [],                       # actions
                            {},                       # hints
                            10000,                    # timeout (in ms)
                            )


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
        self._client.auth(self._jid.getNode(), self.password,
                          resource=session.instrument.instrument)

    def send(self, subject, body, what=None, short=None, important=True):
        receivers = self.receivers
        self.log.debug('trying to send message to %s', ', '.join(receivers))
        for receiver in receivers:
            try:
                msg = self._message(receiver, subject, body)
                self._client.send(msg)
            except Exception:
                self.log.exception('sending to %s failed', receiver)
        self.log.info('%sjabber message sent to %s',
                      what and what + ' ' or '', ', '.join(receivers))

    def _message(self, receiver, subject, body):
        """Create a message with the content as nicely formatted HTML in it."""
        plaintext = subject + '\n\n' + body
        msg = xmpp.protocol.Message(receiver, plaintext)
        msg.setSubject(subject)
        html = msg.addChild('html', namespace=xmpp.protocol.NS_XHTML_IM)
        htmlbody = html.addChild('body', namespace=NS_XHTML)
        p = htmlbody.addChild('p')
        p.addChild('strong', payload=[subject])
        p.addChild('br')
        p.addData(body)
        return msg
