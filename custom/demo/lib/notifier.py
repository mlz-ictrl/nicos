#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS demo notification class using the freedesktop notification protocol."""

from PyQt4.QtDBus import QDBusInterface
from PyQt4.QtCore import QVariant, QStringList

from nicos.devices.notifiers import Notifier


class DBusNotifier(Notifier):

    def send(self, subject, body, what=None, short=None, important=True):
        dbus_interface = QDBusInterface('org.freedesktop.Notifications',
                                        '/org/freedesktop/Notifications')
        dbus_interface.call('Notify',
                            'NICOS',                  # app_name
                            QVariant(QVariant.UInt),  # replaces_id
                            'dialog-error',           # app_icon
                            subject,                  # summary
                            body,                     # body
                            QStringList(),            # actions
                            {},                       # hints
                            10000,                    # timeout (in ms)
        )
