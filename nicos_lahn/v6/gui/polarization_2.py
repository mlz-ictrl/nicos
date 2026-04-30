# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Facundo Silberstein <facundosilberstein@cnea.gob.ar>
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
# *****************************************************************************

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import ScriptExecQuestion, loadUi
from nicos.guisupport.qt import QIcon, QMessageBox, pyqtSlot
from nicos.utils import findResource


class Polarization(Panel):
    panelName = 'Polarization subsystem settings'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_lahn/v6/gui/polarization_2.ui'))
        self.current_status = None
        self.btnRun.setIcon(QIcon(':/continue'))
        self.btnRun.clicked.connect(self.on_start_clicked)
        self.changed_sliders()
        self.ok_btn_1.clicked.connect(self.on_mezeiflipper1)
        self.off_btn_1.clicked.connect(self.off_mezeiflipper1)
        self.ok_btn_2.clicked.connect(self.on_mezeiflipper2)
        self.off_btn_2.clicked.connect(self.off_mezeiflipper2)
        self.flip1.valueChanged.connect(self.set_display_flip1)
        self.comp1.valueChanged.connect(self.set_display_comp1)
        self.flip2.valueChanged.connect(self.set_display_flip2)
        self.comp2.valueChanged.connect(self.set_display_comp2)

    def changed_sliders(self):
        changed_sliders = {
            'trans_po': (self.trans_po, self.trans_po_value),
            'rot_po': (self.rot_po, self.rot_po_value),
            'rot_anoff': (self.rot_anoff, self.rot_anoff_value),
        }
        for (slider, label) in changed_sliders.values():
            slider.setRange(100 * slider.minimum(), 100 * slider.maximum())
            slider.valueChanged.connect(
                lambda value, lbl=label: lbl.setText(str(value / 100.0))
            )
            label.setText(str(slider.value() / 100.0))

    def updateStatus(self, status, exception=False):
        self.current_status = status

    def on_mezeiflipper1(self):
        flip = 0.95
        comp = 3.12
        try:
            self.flip1.valueChanged.disconnect(self.set_display_flip1)
            self.comp1.valueChanged.disconnect(self.set_display_comp1)
        except BaseException:
            pass
        self.flip1.setValue(int(flip * 10))
        self.comp1.setValue(int(comp * 10))
        self.flip1.valueChanged.connect(self.set_display_flip1)
        self.comp1.valueChanged.connect(self.set_display_comp1)

        self.flip1_value.display(flip)
        self.comp1_value.display(comp)

    def on_mezeiflipper2(self):
        flip = 0.95
        comp = 3.12
        try:
            self.flip2.valueChanged.disconnect(self.set_display_flip2)
            self.comp2.valueChanged.disconnect(self.set_display_comp2)
        except BaseException:
            pass
        self.flip2.setValue(int(flip * 10))
        self.comp2.setValue(int(comp * 10))
        self.flip2.valueChanged.connect(self.set_display_flip2)
        self.comp2.valueChanged.connect(self.set_display_comp2)

        self.flip2_value.display(flip)
        self.comp2_value.display(comp)

    @pyqtSlot(int)
    def set_display_flip1(self, value):
        self.flip1_value.display(value / 10.0)

    @pyqtSlot(int)
    def set_display_comp1(self, value):
        self.comp1_value.display(value / 10.0)

    def off_mezeiflipper1(self):
        self.flip1.setValue(0)
        self.comp1.setValue(0)

    @pyqtSlot(int)
    def set_display_flip2(self, value):
        self.flip2_value.display(value / 10.0)

    @pyqtSlot(int)
    def set_display_comp2(self, value):
        self.comp2_value.display(value / 10.0)

    def off_mezeiflipper2(self):
        self.flip2.setValue(0)
        self.comp2.setValue(0)

    @pyqtSlot()
    def on_start_clicked(self):
        code = [
            'maw(flip1, %r, comp1, %r)' % (self.flip1_value.value(),
                                           self.comp1_value.value()),
            'maw(flip2, %r, comp2, %r)' % (self.flip2_value.value(),
                                           self.comp2_value.value()),
            'maw(trans_po, %r, rot_po, %r)' %
            (self.trans_po_value.text(), self.rot_po_value.text()),
            'move(rot_anoff, %r)' % self.rot_anoff_value.text(),
            'read()'
        ]
        self.execScript('\n'.join(code))

    def execScript(self, script):
        action = 'queue'
        if self.current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                action = 'execute'
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
