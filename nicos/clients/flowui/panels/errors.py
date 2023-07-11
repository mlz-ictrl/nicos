# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI error and warning window."""
import os
from logging import WARNING

from nicos.clients.flowui import uipath
from nicos.clients.gui.panels.errors import ErrorPanel as DefaultErrorPanel
from nicos.guisupport.qt import QTextCursor


class ErrorPanel(DefaultErrorPanel):
    """Provides an output view similar to the ConsolePanel.

    In comparison to the ConsolePanel it only displays messages with the
    WARNING and ERROR loglevel.
    """
    ui = os.path.join(uipath, 'panels', 'ui_files', 'errpanel.ui')

    def __init__(self, parent, client, options):
        DefaultErrorPanel.__init__(self, parent, client, options)
        self.outView.insert_position = QTextCursor.MoveOperation.Start

    def on_client_connected(self):
        messages = self.client.ask('getmessages', '10000', default=[])
        self.outView.clear()
        self.outView.addMessages([msg for msg in reversed(messages) if msg[2]
                                  >= WARNING])
        self.outView.scrollToBottom()

    def on_client_message(self, message):
        if message[2] >= WARNING:  # show if level is warning or higher
            self.outView.addMessage(message)
