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

"""NICOS GUI panel for generic panels made with Qt designer."""

from logging import WARNING

from PyQt4.QtCore import SIGNAL

from nicos.utils import findResource
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.guisupport.widget import NicosWidget


class GenericPanel(Panel):
    """Provides a generic implementation of Panel to display any ``.ui`` file.

    The ``.ui`` file may also use NICOS GUI widgets (see :ref:`gui-widgets`).

    Options:

    * ``uifile`` -- the path to the UI file to display
    """

    panelName = 'Generic'  # XXX this is not unique

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        self._error_window = None
        self.connect(client, SIGNAL('connected'), self.on_client_connected)

    def setOptions(self, options):
        Panel.setOptions(self, options)
        loadUi(self, findResource(options['uifile']))
        if options.get('showmsg'):
            self.connect(self.client, SIGNAL('message'), self.on_client_message)

    def on_client_connected(self):
        for ch in self.findChildren(NicosWidget):
            ch.setClient(self.client)

    def on_client_message(self, message):
        # show warnings and errors emitted by the current command in a window
        if len(message) < 7 or message[6] != self.client.last_reqno or \
           message[2] < WARNING:
            return
        msg = '%s: %s' % (message[0], message[3].strip())
        if self._error_window is None:
            def reset_errorwindow():
                self._error_window = None
            self._error_window = ErrorDialog(self)
            self._error_window.accepted.connect(reset_errorwindow)
            self._error_window.addMessage(msg)
            self._error_window.show()
        else:
            self._error_window.addMessage(msg)
            self._error_window.activateWindow()
