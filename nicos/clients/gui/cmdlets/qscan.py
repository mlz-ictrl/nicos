# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI Qscan command input widgets."""

from nicos.clients.gui.cmdlets import Cmdlet, PresetHelper, isFloat, register
from nicos.guisupport.qt import pyqtSlot
from nicos.guisupport.utils import DoubleValidator


class QScan(PresetHelper, Cmdlet):

    name = 'Q scan'
    category = 'Scan'
    cmdname = 'qscan'
    uiName = 'cmdlets/qscan.ui'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, self.uiName)
        self._addPresets(self.presetunit)
        self.preset.setValue(1.0)
        self.preset.valueChanged.connect(self.changed)
        self.presetunit.currentTextChanged.connect(self.changed)
        self.numpoints.valueChanged.connect(self.on_range_changed)
        self.centerBox.toggled[bool].connect(self.on_centerBox_toggled)
        for w in [self.starth, self.startk, self.startl, self.startE,
                  self.steph, self.stepk, self.stepl, self.stepE]:
            w.setValidator(DoubleValidator(self))
            w.textChanged.connect(self.on_range_changed)
            w.setText('0')

    @pyqtSlot()
    def on_range_changed(self):
        try:
            start = self._Q()
            step = self._dQ()
        except ValueError:
            endpos = ''
        else:
            numpoints = self._steps() - 1
            if not self.centerBox.isChecked():
                endpos = '(%s)' % ' '.join(
                    ['%.3f' % (start[i] + numpoints * step[i])
                     for i in range(4)])
            else:
                endpos = '(%s) - (%s)' % (
                    ' '.join(['%.3f' % (start[i] - numpoints * step[i])
                              for i in range(4)]),
                    ' '.join(['%.3f' % (start[i] + numpoints * step[i])
                              for i in range(4)]))
        self.endPos.setText(endpos)
        self.changed()

    def _Q(self):
        return (float(self.starth.text()), float(self.startk.text()),
                float(self.startl.text()), float(self.startE.text()))

    def _dQ(self):
        return (float(self.steph.text()), float(self.stepk.text()),
                float(self.stepl.text()), float(self.stepE.text()))

    def _steps(self):
        return self.numpoints.value()

    def getValues(self):
        return {
            'scanpoints': self.numpoints.value(),
            'preset': self.preset.value(),
            'presetunit': self.presetunit.currentText(),
        }

    @pyqtSlot(bool)
    def on_centerBox_toggled(self, check):
        if check:
            self.start_center.setText('Center:')
            self.ends_at.setText('Edges:')
        else:
            self.start_center.setText('Start:')
            self.ends_at.setText('Ends at:')
        self.on_range_changed()

    def isValid(self):
        return all([
            self.markValid(self.numpoints, self.numpoints.value() > 0),
            self.markValid(self.preset, self.preset.value() > 0),
            self.markValid(self.starth, isFloat(self.starth)),
            self.markValid(self.startk, isFloat(self.startk)),
            self.markValid(self.startl, isFloat(self.startl)),
            self.markValid(self.startE, isFloat(self.startE)),
            self.markValid(self.steph, isFloat(self.steph)),
            self.markValid(self.stepk, isFloat(self.stepk)),
            self.markValid(self.stepl, isFloat(self.stepl)),
            self.markValid(self.stepE, isFloat(self.stepE)),
        ])

    def generate(self):
        self.cmdname = 'qcscan' if self.centerBox.isChecked() else 'qscan'
        values = self.getValues()
        preset = self._getPreset(values)
        return f'{self.cmdname}({self._Q()}, {self._dQ()}, {self._steps()}, ' \
               f'{preset})'


register(QScan)
