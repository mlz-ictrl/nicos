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

"""NICOS GUI traceback display window."""

from nicos.guisupport.qt import pyqtSlot, QDialog, QPushButton, QFont, \
    QTreeWidgetItem, QDialogButtonBox, QApplication, QClipboard

from nicos.clients.gui.utils import loadUi
from nicos.pycompat import iteritems


class TracebackDialog(QDialog):

    def __init__(self, parent, view, tb):
        QDialog.__init__(self, parent)
        loadUi(self, 'traceback.ui', 'dialogs')
        self.tb = tb
        self.view = view
        self.client = parent.client

        assert tb.startswith('Traceback')
        # split into frames and message
        frames = []
        message = ''
        curframe = []
        for line in tb.splitlines():
            if line.startswith('        '):
                try:
                    name, v = line.split('=', 1)
                except ValueError:
                    pass  # most probably the "^" line of a SyntaxError
                else:
                    if curframe:
                        curframe[2][name.strip()] = v.strip()
            elif line.startswith('    '):
                if curframe:
                    curframe[1] = line.strip()
            elif line.startswith('  '):
                curframe = [line.strip(), '', {}]
                frames.append(curframe)
            elif not line.startswith('Traceback'):
                message += line

        button = QPushButton('To clipboard', self)
        self.buttonBox.addButton(button, QDialogButtonBox.ActionRole)

        def copy():
            QApplication.clipboard().setText(tb+'\n', QClipboard.Selection)
            QApplication.clipboard().setText(tb+'\n', QClipboard.Clipboard)
        button.clicked.connect(copy)

        self.message.setText(message[:200])
        self.tree.setFont(view.font())
        boldfont = QFont(view.font())
        boldfont.setBold(True)
        for filename, line, bindings in frames:
            item = QTreeWidgetItem(self.tree, [filename])
            item.setFirstColumnSpanned(True)
            item = QTreeWidgetItem(self.tree, [line])
            item.setFirstColumnSpanned(True)
            item.setFont(0, boldfont)
            for var, value in iteritems(bindings):
                QTreeWidgetItem(item, ['', var, value])

    @pyqtSlot()
    def on_ticketButton_clicked(self):
        from nicos.clients.gui.tools.bugreport import BugreportTool
        formatted_log = ''.join(self.view.formatMessage(msg)[0]
                                for msg in self.view.getLatest())
        dlg = BugreportTool(self, self.client, traceback=self.tb,
                            log_excerpt=formatted_log)
        dlg.exec_()
        self.reject()
