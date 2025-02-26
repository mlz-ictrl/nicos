# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos.clients.gui.panels import Panel
from nicos.guisupport.qt import QHBoxLayout, QLabel, QScrollArea, \
    QSizePolicy, Qt


class CommandOutput(Panel):
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.setLayout(QHBoxLayout())
        scroll = QScrollArea()
        self.setMaximumHeight(55)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Minimum)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMaximumHeight(40)

        self.outputMessage = QLabel()
        self.outputMessage.setMaximumHeight(30)
        self.outputMessage.setSizePolicy(QSizePolicy.Policy.Expanding,
                                         QSizePolicy.Policy.Minimum)
        scroll.setWidget(self.outputMessage)
        self.layout().addWidget(scroll)
        client.message.connect(self.on_client_message)

    def on_client_message(self, message):
        self.outputMessage.setText(message[3])
