#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Graphical maintenance command runner."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time
import subprocess
from os import path

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QPushButton
from PyQt4.uic import loadUi

from nicos.gui import custom
from nicos.gui.tools.uitools import runDlgStandalone


class CmdTool(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        custom.load_customization()
        loadUi(path.join(path.dirname(__file__), 'cmdtool.ui'), self)

        self.connect(self.closeBtn, SIGNAL('clicked()'), self.close)

        ncmds = len(custom.MAINT_COMMANDS)
        collen = min(ncmds, 8)

        for i, (text, cmd) in enumerate(custom.MAINT_COMMANDS):
            btn = QPushButton(text, self)
            self.buttonLayout.addWidget(btn, i % collen, i // collen)
            self.connect(btn, SIGNAL('clicked()'),
                         lambda cmd=cmd: self.execute(cmd))

    def execute(self, cmd):
        self.outputBox.setPlainText('[%s] Executing %s...\n' %
                                    (time.strftime('%H:%M:%S'), cmd))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0]
        self.outputBox.appendPlainText(out)


if __name__ == '__main__':
    runDlgStandalone(CmdTool)
