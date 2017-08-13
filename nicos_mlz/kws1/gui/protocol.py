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

"""Generate a measurement protocol from saved runs."""

from os import path

from nicos.guisupport.qt import pyqtSlot, QPrintDialog, QPrinter, QFileDialog

from nicos.utils import findResource
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.pycompat import to_utf8


class ProtocolPanel(Panel):
    """Generate a measurement protocol from saved runs."""

    panelName = 'KWS protocol'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, findResource('nicos_mlz/kws1/gui/protocol.ui'))

        self.firstEdit.setShadowText('default: all')
        self.lastEdit.setShadowText('default: all')
        self.fontBox.setValue(self.outText.font().pointSize())

    @pyqtSlot()
    def on_genBtn_clicked(self):
        datadir = self.client.eval('session.experiment.proposalpath', '')
        if not datadir:
            self.showError('Cannot determine data directory! Are you '
                           'connected?')
            return
        if not path.isdir(path.join(datadir, 'data')):
            self.showError('Cannot read data! This tool works only when '
                           'the data is accessible at %s.' % datadir)
            return

        first = self.firstEdit.text() or None
        if first:
            try:
                first = int(first)
            except ValueError:
                self.showError('First run is not a number!')
                return
        last = self.lastEdit.text() or None
        if last:
            try:
                last = int(last)
            except ValueError:
                self.showError('Last run is not a number!')
                return

        with_ts = self.stampBox.isChecked()

        text = self.client.eval('session.experiment._generate_protocol('
                                '%s, %s, %s)' % (first, last, with_ts))
        self.outText.setPlainText(text)

    @pyqtSlot()
    def on_saveBtn_clicked(self):
        initialdir = self.client.eval('session.experiment.proposalpath', '')
        fn = QFileDialog.getSaveFileName(self, 'Save protocol', initialdir,
                                         'Text files (*.txt)')
        if not fn:
            return
        try:
            text = self.outText.toPlainText()
            with open(fn, 'wb') as fp:
                fp.write(to_utf8(text))
        except Exception as err:
            self.showError('Could not save: %s' % err)

    @pyqtSlot()
    def on_printBtn_clicked(self):
        # Let the user select the desired printer via the system printer list
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if not dialog.exec_():
            return
        doc = self.outText.document().clone()
        font = self.outText.font()
        font.setPointSize(self.fontBox.value())
        doc.setDefaultFont(font)
        printer.setPageMargins(10, 15, 10, 20, QPrinter.Millimeter)
        doc.print_(printer)
