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

"""Dialog for showing (potentially multiple) error messages."""

from PyQt4.QtGui import QDialog, QStyle

from nicos.clients.gui.utils import loadUi


class ErrorDialog(QDialog):

    def __init__(self, parent, windowTitle='Error'):
        QDialog.__init__(self, parent)
        loadUi(self, 'error.ui', 'dialogs')

        self.iconLabel.setPixmap(
            self.style().standardIcon(QStyle.SP_MessageBoxWarning).
            pixmap(32, 32))
        self.setWindowTitle(windowTitle)

    def addMessage(self, message):
        existing = self.errorText.text()
        if existing:
            self.errorText.setText(existing + '\n' + message)
        else:
            self.errorText.setText(message)
