#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""'Instrument reconfiguration' tool for LoKI"""

from nicos.clients.gui.utils import DlgUtils, loadUi
from nicos.guisupport.qt import QButtonGroup, QLabel, QMainWindow, QRadioButton
from nicos.utils import findResource

TEMPLATE = '''\
# -*- coding: utf-8 -*-

description = %(description)r
group = 'basic'

modules = %(modules)s

includes = %(includes)s
'''


class InstrumentConfigTool(DlgUtils, QMainWindow):

    def __init__(self, parent, client, **settings):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Instrument config')
        loadUi(self, findResource('nicos_ess/loki/gui/ui_files/instrconfig.ui'))
        self.setWindowTitle('Reconfigure Instrument')
        self.client = client
        self.client.connected.connect(self.on_client_connected)
        self.client.disconnected.connect(self.on_client_disconnected)
        self._parts = settings['parts']
        self._widgets = []
        for (i, part) in enumerate(self._parts):
            label = QLabel(part + ':', self)
            bgrp = QButtonGroup(self)
            rbtn = QRadioButton('real', self)
            vbtn = QRadioButton('virtual', self)
            bgrp.addButton(rbtn)
            bgrp.addButton(vbtn)
            self.grid.addWidget(label, i, 0)
            self.grid.addWidget(rbtn, i, 1)
            self.grid.addWidget(vbtn, i, 2)
            self._widgets.append((label, bgrp, rbtn, vbtn))
        self.resize(self.sizeHint())
        if self.client.isconnected:
            self._update()
        else:
            self.frame.setDisabled(True)

    def on_client_connected(self):
        self.frame.setDisabled(False)
        self._update()

    def on_client_disconnected(self):
        self.frame.setDisabled(True)

    def on_buttonBox_accepted(self):
        if self.client.isconnected:
            self._apply()
            self.close()

    def on_buttonBox_rejected(self):
        self.close()

    def _update(self):
        try:
            configcode = self.client.eval(
                '__import__("nicos_ess").loki._get_instr_config()')
            config = {'__builtins__': None}
            exec(configcode, config)
        except Exception:
            self.showError('Could not determine current config.')
            self.frame.setDisabled(True)
            return
        includes = set(config['includes'])
        for (part, widgets) in zip(self._parts, self._widgets):
            if 'virtual_' + part in includes:
                widgets[3].setChecked(True)
                includes.discard('virtual_' + part)
            else:
                widgets[2].setChecked(True)
                includes.discard(part)
        self.additionalBox.setPlainText('\n'.join(includes))
        self._modules = config.get('modules', [])
        self._description = config.get('description', 'instrument setup')

    def _apply(self):
        info = {'description': self._description, 'modules': self._modules,
                'includes': []}
        for (part, widgets) in zip(self._parts, self._widgets):
            if widgets[3].isChecked():
                info['includes'].append('virtual_' + part)
            else:
                info['includes'].append(part)
        for add in self.additionalBox.toPlainText().splitlines():
            if add:
                info['includes'].append(add)
        code = TEMPLATE % info
        try:
            self.client.eval(
                '__import__("nicos_ess").loki._apply_instr_config(%r)' % code)
        except Exception:
            self.showError('Could not apply new config.')
            return
        self.client.run('NewSetup()')
        self.showInfo('Instrument was successfully reconfigured.')
