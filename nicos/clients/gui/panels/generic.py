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

"""NICOS GUI panel for generic panels made with Qt designer."""

from logging import WARNING

from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core.errors import ConfigurationError
from nicos.guisupport.widget import NicosWidget
from nicos.utils import findResource


class GenericPanel(Panel):
    """Provides a generic implementation of Panel to display any ``.ui`` file.

    The ``.ui`` file may also use NICOS GUI widgets (see :ref:`gui-widgets`).

    Options:

    * ``uifile`` -- the path to the UI file to display
    * ``showmsg`` -- if set to `True` a dialog window pops up in case of an
      error or warning inside the daemon and displays the corresponding
      message. If the dialog is already open, a new line with the error or
      warning message will be added to the open dialog.
    """

    panelName = 'Generic'  # XXX this is not unique

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self._error_window = None
        if 'uifile' not in options:
            raise ConfigurationError('GenericPanels require at least an'
                                     ' `uifile` option.')
        loadUi(self, findResource(options['uifile']))
        if options.get('showmsg'):
            self.client.message.connect(self.on_client_message)
        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)

    def on_client_connected(self):
        for ch in self.findChildren(NicosWidget):
            ch.setClient(self.client)

    def on_client_message(self, message):
        # show warnings and errors emitted by the current command in a window
        if len(message) < 6 or message[5] != self.client.last_reqid or \
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
