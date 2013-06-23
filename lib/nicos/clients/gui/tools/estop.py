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

"""Always-on-top emergency stop button."""

from PyQt4.QtGui import QDialog, QPushButton, QHBoxLayout
from PyQt4.QtCore import SIGNAL, Qt


class EmergencyStopTool(QDialog):
    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        self.client = client
        self.setWindowTitle(' ')  # window title is unnecessary
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.btn = QPushButton('STOP', self)
        self.btn.setStyleSheet('''
        QPushButton {
            color: yellow;
            font-size: 24px;
            font-weight: bold;
            background-color: #ff0000;
            border-style: solid;
            border-width: 5px;
            border-radius: 45px;
            border-color: #cc0000;
            max-width: 80px;
            max-height: 80px;
            min-width: 80px;
            min-height: 80px;
        }''')

        layout = QHBoxLayout()
        layout.addWidget(self.btn)
        layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(layout)
        self.connect(self.btn, SIGNAL('clicked()'), self.dostop)

    def dostop(self, *ignored):
        self.client.tell('emergency')
