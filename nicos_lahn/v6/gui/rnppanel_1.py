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


class RNPPanel(Panel):
    panelName = 'RNP Instrument'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_lahn/v6/gui/rnppanel_1.ui'))
        self.current_status = None
        self.btnRun.setIcon(QIcon(':/continue'))
        self.btnRun.clicked.connect(self.on_start_clicked)
        self.changed_sliders()

    def changed_sliders(self):
        changed_sliders = {
            'beam_m': (self.beam_m, self.beam_m_value),
            'lin_m': (self.lin_m, self.lin_m_value),
            'omega_m': (self.omega_m, self.omega_m_value),
            'height_slit1': (self.height_slit1, self.height_slit1_value),
            'width_slit1': (self.width_slit1, self.width_slit1_value),
            'height_slit2': (self.height_slit2, self.height_slit2_value),
            'width_slit2': (self.width_slit2, self.width_slit2_value),
            'chi': (self.chi, self.chi_value),
            'high_s': (self.high_s, self.high_s_value),
            'omega_s': (self.omega_s, self.omega_s_value),
            'y': (self.y, self.y_value),
            'z': (self.z, self.z_value),
            'beam_d': (self.beam_d, self.beam_d_value),
            'height_slit3': (self.height_slit3, self.height_slit3_value),
            'width_slit3': (self.width_slit3, self.width_slit3_value),
            'delta_d': (self.delta_d, self.delta_d_value),
        }
        for (slider, label) in changed_sliders.values():
            slider.setRange(100 * slider.minimum(), 100 * slider.maximum())
            slider.valueChanged.connect(
                lambda value, lbl=label: lbl.setText(str(value / 100.0))
            )
            label.setText(str(slider.value() / 100.0))

    def updateStatus(self, status, exception=False):
        self.current_status = status

    @pyqtSlot()
    def on_start_clicked(self):
        code = [
            'move(beam_m, %r)' % self.beam_m_value.text(),
            'maw(lin_m, %r, omega_m, %r)' %
            (self.lin_m_value.text(), self.omega_m_value.text()),
            'maw(slit_1, [%r, %r, %r, %r])' %
            (0, 0, self.width_slit1_value.text(),
             self.height_slit1_value.text()),
            'maw(slit_2, [%r, %r, %r, %r])' %
            (0, 0, self.width_slit2_value.text(),
             self.height_slit2_value.text()),
            'maw(chi, %r, high_s, %r, omega_s, %r, y, %r, z, %r)' %
            (self.chi_value.text(), self.high_s_value.text(),
             self.omega_s_value.text(), self.y_value.text(),
             self.z_value.text()),
            'move(beam_d, %r)' % self.beam_d_value.text(),
            'maw(slit_3, [%r, %r, %r, %r])' %
            (0, 0, self.width_slit3_value.text(),
             self.height_slit3_value.text()),
            'move(delta_d, %r)' % self.delta_d_value.text(),
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
