#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI cmdlets for POLI."""

from nicos.clients.gui.cmdlets import Cmdlet, register, isFloat, isInt
from nicos.utils import findResource


class CenterPeak(Cmdlet):

    name = 'Center peak'
    category = 'Scan'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource('custom/poli/lib/gui/centerpeak.ui'))
        self.multiList.entryAdded.connect(self.on_entryAdded)
        self.multiList.uifile = findResource('custom/poli/lib/gui/centerpeak_one.ui')
        self.steps.valueChanged.connect(self.changed)
        self.stepsize.textChanged.connect(self.changed)
        self.func.currentIndexChanged.connect(self.changed)
        self.seconds.textChanged.connect(self.changed)
        self.rounds.valueChanged.connect(self.changed)
        self.contBox.toggled.connect(self.changed)

    def on_entryAdded(self, entry):
        entry.device.addItems(self.client.getDeviceList('nicos.core.device.Moveable'))
        entry.device.currentIndexChanged['QString'].connect(self.changed)
        entry.step.textChanged.connect(self.changed)
        entry.steps.textChanged.connect(self.changed)

    def _setDevice(self, values):
        """Helper for setValues for setting a device combo box."""
        if 'dev' in values:
            idx = self.multiList.entry(0).device.findText(values['dev'])
            if idx > -1:
                self.multiList.entry(0).device.setCurrentIndex(idx)

    def getValues(self):
        return {
            'dev': self.multiList.entry(0).device.currentText(),
            'counttime': float(self.seconds.text()),
        }

    def setValues(self, values):
        self._setDevice(values)

    def isValid(self):
        valid = [
            self.markValid(self.stepsize, isFloat(self.stepsize)),
            self.markValid(self.seconds, isFloat(self.seconds)),
        ] + [
            self.markValid(e.steps, e.steps.text() == '' or isInt(e.steps)) and
            self.markValid(e.step, e.step.text() == '' or isFloat(e.step))
            for e in self.multiList.entries()
        ]
        return all(valid)

    def generate(self, mode):
        cmd = 'centerpeak'
        entries = self.multiList.entries()
        args = [e.device.currentText() for e in entries]
        kwargs = []
        for e in entries:
            if e.step.text():
                kwargs.append(('step_' + e.device.currentText(),
                               float(e.step.text())))
            if e.steps.text():
                kwargs.append(('steps_' + e.device.currentText(),
                               int(e.steps.text())))
        kwargs.append(('steps', self.steps.value()))
        kwargs.append(('step', float(self.stepsize.text())))
        kwargs.append(('rounds', self.rounds.value()))
        if self.func.currentText() != 'center_of_mass':
            kwargs.append(('fit', self.func.currentText()))
        kwargs.append(('t', float(self.seconds.text())))
        if self.contBox.isChecked():
            kwargs.append(('cont', True))
        if mode == 'simple':
            return cmd + ' ' + ' '.join(args) + ' ' + \
                ' '.join('%s %r' % i for i in kwargs)
        return cmd + '(' + ', '.join(args) + ', ' + \
            ', '.join('%s=%r' % i for i in kwargs) + ')'


register(CenterPeak)
