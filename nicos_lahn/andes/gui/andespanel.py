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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, ScriptExecQuestion
from nicos.utils import findResource
from nicos.guisupport.qt import QIcon, pyqtSlot, QMessageBox


class ANDESPanel(Panel):
    panelName = 'ANDES Instrument'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_lahn/andes/gui/andespanel.ui'))

        self.current_status = None

        self.btnRun.setIcon(QIcon(':/continue'))
        self.btnRun.clicked.connect(self.on_start_clicked)

        client.connected.connect(self.on_client_connected)
        client.device.connect(self.on_client_device)

    def updateStatus(self, status, exception=False):
        self.current_status = status

    def on_client_connected(self):
        self.cbCollimator.clear()
        self.cbCollimator.addItems(self.client.eval('hole.valuetype.vals'))

    def on_client_device(self, data):
        (action, devlist) = data
        if 'hole' in devlist:
            if action == 'create':
                self.cbCollimator.addItems(self.client.eval('hole.valuetype.vals'))
            elif action == 'destroy':
                self.cbCollimator.clear()

    @pyqtSlot()
    def on_start_clicked(self):
        code = []
        code.append('move(sw.width, %r)' % self.sw_value.text())
        code.append('move(hole, %r)' % self.cbCollimator.currentText())
        code.append('maw(mtt, %r)' % self.mtt_value.text())
        code.append('maw(x, %r, y, %r, z, %r, phi, %r)' % (self.x_value.text(), self.y_value.text(),
                                                           self.z_value.text(), self.phi_value.text()))
        code.append('read()')
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
        self.client.tell(script, action)
