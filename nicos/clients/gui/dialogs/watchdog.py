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

"""NICOS GUI watchdog event notification window."""

import time

from nicos.guisupport.qt import QDialog, QFrame, QVBoxLayout, QWidget, \
    QDialogButtonBox

from nicos.clients.gui.utils import loadUi


class WatchdogDialog(QDialog):
    def __init__(self, main):
        QDialog.__init__(self, main)
        loadUi(self, 'watchdog.ui', 'dialogs')

        self.frame = QFrame(self)
        self.scrollArea.setWidget(self.frame)
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().setContentsMargins(0, 0, 10, 0)
        self.frame.layout().addStretch()

        def btn(button):
            if self.buttonBox.buttonRole(button) == QDialogButtonBox.ResetRole:
                for w in self.frame.children():
                    if isinstance(w, QWidget):
                        w.hide()
            else:
                self.close()
        self.buttonBox.clicked.connect(btn)

    def addEvent(self, data):
        w = QWidget(self.frame)
        loadUi(w, 'watchdog_item.ui', 'dialogs')
        self.frame.layout().insertWidget(self.frame.layout().count()-1, w)
        if data[0] == 'warning':
            w.datelabel.setText('Watchdog alert - %s' %
                                time.strftime('%Y-%m-%d %H:%M',
                                              time.localtime(data[1])))
            w.messagelabel.setText(data[2])
        elif data[0] == 'action':
            w.datelabel.setText('Watchdog action - %s' %
                                time.strftime('%Y-%m-%d %H:%M',
                                              time.localtime(data[1])))
            w.messagelabel.setText('Executing action:\n' + data[2])
