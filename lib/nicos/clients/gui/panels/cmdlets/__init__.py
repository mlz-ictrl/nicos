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

"""NICOS GUI command input widgets."""

from PyQt4.QtCore import Qt, SIGNAL, pyqtSignature as qtsig
from PyQt4.QtGui import QWidget, QColor

from nicos.clients.gui.utils import loadUi, setBackgroundColor

invalid = QColor('#ffcccc')


class Cmdlet(QWidget):

    name = ''
    category = ''

    def __init__(self, parent, client):
        self.client = client
        QWidget.__init__(self, parent)

    @qtsig('')
    def on_delBtn_clicked(self):
        self.emit(SIGNAL('cmdletRemoved'), self)
        self.parent().layout().removeWidget(self)
        self.hide()

    def markValid(self, ctl, condition):
        if condition:
            setBackgroundColor(ctl, Qt.white)
        else:
            setBackgroundColor(ctl, invalid)
        return condition

    def isValid(self):
        """Check if all entered data is valid.

        This method can change widget styles to indicate invalid data with
        the markValid() method if wanted.
        """
        return True

    def generate(self, mode):
        """Generate code for the commandlet.

        *mode* is 'python' or 'simple'.

        Should generate a string of lines, complete with newlines.
        """
        return ''


class Move(Cmdlet):

    name = 'Move'
    category = 'Device'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'move.ui', 'panels/cmdlets')
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))

    def isValid(self):
        return self.markValid(self.target, not self.target.text().isEmpty())

    def generate(self, mode):
        args = (self.device.currentText(), self.target.text())
        if mode == 'simple':
            return 'maw %s %s\n' % args
        return 'maw(%s, %s)\n' % args


class Count(Cmdlet):

    name = 'Count'
    category = 'Device'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'count.ui', 'panels/cmdlets')

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'count %s\n' % self.seconds.value()
        return 'count(%s)\n' % self.seconds.value()


class Scan(Cmdlet):

    name = 'Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'scan.ui', 'panels/cmdlets')
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))

    def isValid(self):
        # NOTE: cannot use "return markValid() and markValid() and ..." because
        # that short-circuits evaluation and therefore skips marking all but the
        # first invalid control
        valid = [
            self.markValid(self.start, not self.start.text().isEmpty()),
            self.markValid(self.step, not self.step.text().isEmpty()),
            self.markValid(self.numpoints, self.numpoints.value() > 0),
            self.markValid(self.seconds, self.seconds.value() > 0),
        ]
        return all(valid)

    def generate(self, mode):
        args = (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numpoints.value(),
            self.seconds.value(),
        )
        if mode == 'simple':
            return 'scan %s %s %s %s %s\n' % args
        return 'scan(%s, %s, %s, %s, %s)\n' % args


class CScan(Cmdlet):

    name = 'Centered Scan'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'cscan.ui', 'panels/cmdlets')
        self.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))

    def isValid(self):
        valid = [
            self.markValid(self.start, not self.start.text().isEmpty()),
            self.markValid(self.step, not self.step.text().isEmpty()),
            self.markValid(self.numpoints, self.numpoints.value() > 0),
            self.markValid(self.seconds, self.seconds.value() > 0),
        ]
        return all(valid)

    def generate(self, mode):
        args = (
            self.device.currentText(),
            self.start.text(),
            self.step.text(),
            self.numpoints.value(),
            self.seconds.value(),
        )
        if mode == 'simple':
            return 'cscan %s %s %s %s %s\n' % args
        return 'cscan(%s, %s, %s, %s, %s)\n' % args


class Sleep(Cmdlet):

    name = 'Sleep'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'sleep.ui', 'panels/cmdlets')

    def isValid(self):
        return self.markValid(self.seconds, self.seconds.value() > 0)

    def generate(self, mode):
        if mode == 'simple':
            return 'sleep %s\n' % self.seconds.text()
        return 'sleep(%s)\n' % self.seconds.text()


class Configure(Cmdlet):

    name = 'Configure'
    category = 'Device'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client)
        loadUi(self, 'configure.ui', 'panels/cmdlets')
        self.device.addItems(self.client.getDeviceList())
        self.on_device_change(self.device.currentText())
        self.connect(self.device, SIGNAL('currentIndexChanged(const QString&)'),
                     self.on_device_change)

    def on_device_change(self, text):
        params = self.client.getDeviceParamInfo(str(text))
        self.parameter.clear()
        self.parameter.addItems(sorted(p for p in params
                                       if params[p]['settable']))

    def isValid(self):
        return self.markValid(self.target, not self.target.text().isEmpty())

    def generate(self, mode):
        args = (self.device.currentText(), self.parameter.currentText(),
                self.target.text())
        if mode == 'simple':
            return 'set %s %s %s\n' % args
        return '%s.%s = %s\n' % args


all_cmdlets = [Move, Count, Scan, CScan, Sleep, Configure]
all_categories = ['Device', 'Scan', 'Other']
