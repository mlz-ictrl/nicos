#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Graphical maintenance command runner."""

import time
import subprocess

from PyQt4.QtGui import QDialog, QPushButton
from PyQt4.QtCore import SIGNAL

from nicos.clients.gui.utils import loadUi


class CommandsTool(QDialog):
    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'commands.ui', 'tools')

        self.connect(self.closeBtn, SIGNAL('clicked()'), self.close)

        commands = settings.get('commands', [])
        ncmds = len(commands)
        collen = min(ncmds, 8)

        for i, (text, cmd) in enumerate(commands):
            btn = QPushButton(text, self)
            self.buttonLayout.addWidget(btn, i % collen, i // collen)
            self.connect(btn, SIGNAL('clicked()'),
                         lambda btncmd=cmd: self.execute(btncmd))

    def execute(self, cmd):
        self.outputBox.setPlainText('[%s] Executing %s...\n' %
                                    (time.strftime('%H:%M:%S'), cmd))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0].decode()
        self.outputBox.appendPlainText(out)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()
