# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI tomography command input widgets."""

from nicos.clients.gui.cmdlets import Cmdlet, PresetHelper, register
from nicos.guisupport.qt import pyqtSlot


class Tomo(PresetHelper, Cmdlet):

    name = 'Tomography'
    category = 'Scan'
    cmdname = 'tomo'
    uiName = 'cmdlets/tomo.ui'

    def __init__(self, parent, client, options):
        Cmdlet.__init__(self, parent, client, options, self.uiName)
        self._addPresets(self.presetunit)
        self.device.addItems(self._getDeviceList())
        self.on_device_change(self.device.currentText())
        self.device.currentTextChanged.connect(self.changed)
        self.imgPerAngle.valueChanged.connect(self.changed)
        self.numpoints.valueChanged.connect(self.changed)
        self.preset.valueChanged.connect(self.changed)
        self.preset.setValue(1.0)
        self.presetunit.currentTextChanged.connect(self.changed)
        self.detectors.currentTextChanged.connect(self.changed)
        self.contBox.toggled.connect(self.changed)
        self.detectors.addItems(
            self.client.eval('session.experiment.detlist', []))
        self.contBox.clicked[bool].connect(self.on_contBox_clicked)
        self.refFirst.clicked[bool].connect(self.on_refFirst_clicked)
        self.start.valueChanged[float].connect(self.on_start_changed)

    @pyqtSlot(float)
    def on_start_changed(self):
        self.changed()

    @pyqtSlot(bool)
    def on_contBox_clicked(self, checked):
        if checked:
            self.refFirst.setChecked(False)
        self.changed()

    @pyqtSlot(bool)
    def on_refFirst_clicked(self, checked):
        if checked:
            self.contBox.setChecked(False)
        self.changed()

    def on_device_change(self, text):
        self.changed()

    def isValid(self):
        return all([
            self.markValid(self.numpoints, self.numpoints.value() > 0),
            self.markValid(self.preset, self.preset.value() > 0),
            self.markValid(self.device, self.device.currentText().strip()),
        ])

    def getValues(self):
        return {'dev': self.device.currentText(),
                'nangles': self.numpoints.value(),
                'imgsperangle': self.imgPerAngle.value(),
                'preset': self.preset.value(),
                'presetunit': self.presetunit.currentText(),
                'reffirst': self.refFirst.isChecked(),
                'detlist': self.detectors.currentText(),
                'start': self.start.value() if self.contBox.isChecked() else 0.0,
                }

    def generate(self):
        values = self.getValues()
        preset = self._getPreset(values)
        devrepr = self._getDeviceRepr(values['dev'])
        ret = f'{self.cmdname}({values["nangles"]}, '
        if values['dev']:
            ret += f'moveables={devrepr}, '
        else:
            ret += 'None, '
        ret += f'imgsperangle={values["imgsperangle"]}, ' \
            f'ref_first={values["reffirst"]}, startpoint={values["start"]}, '
        if values['detlist']:
            ret += f'{values["detlist"]}, '
        ret += f'{preset})'
        return ret


register(Tomo)
