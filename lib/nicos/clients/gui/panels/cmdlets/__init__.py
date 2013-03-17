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

"""NICOS GUI command input widgets."""

__version__ = "$Revision$"

from PyQt4.QtCore import SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QWidget

from nicos.clients.gui.utils import loadUi


class Cmdlet(QWidget):

    name = ''
    category = 'device'

    def __init__(self, parent, client):
        self.client = client
        QWidget.__init__(self, parent)

    def getdevlist(self):
        # XXX
        return sorted(self.client.eval(
            'list(dn for (dn, d) in session.devices.iteritems() if '
            '"nicos.core.device.Moveable" in d.classes and '
            'dn in session.explicit_devices)', []))

    @qtsig('')
    def on_delBtn_clicked(self):
        self.emit(SIGNAL('cmdletRemoved'), self)
        self.parent().layout().removeWidget(self)
        self.hide()

    def generate(self):
        return ''


class Move(Cmdlet):

    name = 'Move'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'move.ui', 'panels/cmdlets')
        self.device.addItems(self.getdevlist())

    def generate(self):
        return 'maw(%s, %s)\n' % (self.device.currentText(),
                                  self.target.text())


class Count(Cmdlet):

    name = 'Count'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'count.ui', 'panels/cmdlets')

    def generate(self):
        return 'count(%s)\n' % self.seconds.value()


class Scan(Cmdlet):

    name = 'Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'scan.ui', 'panels/cmdlets')
        self.device.addItems(self.getdevlist())

    def generate(self):
        return 'scan(%s, %s, %s, %s, %s)\n' % (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numsteps.value(),
            self.seconds.value(),
        )


class CScan(Cmdlet):

    name = 'Centered Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'cscan.ui', 'panels/cmdlets')
        self.device.addItems(self.getdevlist())

    def generate(self):
        return 'cscan(%s, %s, %s, %s, %s)\n' % (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numsteps.value(),
            self.seconds.value(),
        )


all_cmdlets = [Move, Count, Scan, CScan]
