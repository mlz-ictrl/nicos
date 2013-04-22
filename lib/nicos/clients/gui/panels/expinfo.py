#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI panel with most important experiment info."""

from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QLabel

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi


class SqueezedLabel(QLabel):
    """A label that elides text to fit its width."""

    def __init__(self, *args):
        self._fulltext = ''
        QLabel.__init__(self, *args)
        self._squeeze()

    def resizeEvent(self, event):
        self._squeeze()
        QLabel.resizeEvent(self, event)

    def setText(self, text):
        self._fulltext = text
        self._squeeze(text)

    def _squeeze(self, text=None):
        if text is None:
            text = self.text()
        fm = self.fontMetrics()
        labelwidth = self.size().width()
        squeezed = False
        new_lines = []
        for line in text.split('\n'):
            if fm.width(line) > labelwidth:
                squeezed = True
                new_lines.append(fm.elidedText(line, Qt.ElideRight, labelwidth))
            else:
                new_lines.append(line)
        if squeezed:
            QLabel.setText(self, u'\n'.join(map(unicode, new_lines)))
            self.setToolTip(self._fulltext)
        else:
            QLabel.setText(self, self._fulltext)
            self.setToolTip('')

    def mouseDoubleClickEvent(self, event):
        self.emit(SIGNAL('doubleClicked'))


class ExpInfoPanel(Panel):
    panelName = 'Experiment Info'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'expinfo.ui', 'panels')

        self.expdevname = '---'
        self.sampledevname = '---'
        if client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('cache'), self.on_client_cache)

    def on_client_connected(self):
        values = self.client.eval('session.experiment.name, '
                                  'session.experiment.sample.name, '
                                  'session.experiment.proposal, '
                                  'session.experiment.title, '
                                  'session.experiment.users, '
                                  'session.experiment.localcontact, '
                                  'session.experiment.remark, '
                                  'session.experiment.sample.samplename', None)
        if values is None:
            return
        self.expdevname = values[0].lower() + '/'
        self.sampledevname = values[1].lower() + '/'
        self.expproposal.setText(values[2])
        self.exptitle.setText(values[3])
        self.expusers.setText(values[4])
        self.explocalcontact.setText(values[5])
        self.expremark.setText(values[6])
        self.samplename.setText(values[7])

    def on_client_cache(self, (time, key, op, value)):
        if key.startswith((self.expdevname, self.sampledevname)):
            self.on_client_connected()
