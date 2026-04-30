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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import ScriptExecQuestion, loadUi
from nicos.guisupport.qt import QIcon, QMessageBox, pyqtSlot
from nicos.utils import findResource


class V6Panel(Panel):
    panelName = 'V6 Instrument'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_lahn/v6/gui/panel.ui'))
        self.current_status = None
        self.btnRun.setIcon(QIcon(':/continue'))
        self.btnRun.clicked.connect(self.on_start_clicked)

    def updateStatus(self, status, exception=False):
        self.current_status = status

    @pyqtSlot()
    def on_start_clicked(self):
        code = []
        code.append(
            'maw(slit_2, [%r, %r, %r, %r])' %
            (self.slit2_x_value.text(),
             self.slit2_y_value.text(),
             self.slit2_w_value.text(),
             self.slit2_h_value.text()))
        code.append(
            'maw(slit_3, [%r, %r, %r, %r])' %
            (self.slit3_x_value.text(),
             self.slit3_y_value.text(),
             self.slit3_w_value.text(),
             self.slit3_h_value.text()))
        code.append('move(chi, %r)' % self.chi_value.text())
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
        if action == 'queue':
            self.client.run(script)
        else:
            self.client.tell('exec', script)
