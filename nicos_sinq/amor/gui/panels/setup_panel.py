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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

from datetime import date
from os import path

from nicos_sinq.gui.panels.setup_panel import ExpPanel
from nicos.clients.gui.panels.setup_panel import splitUsers
from nicos.guisupport.qt import pyqtSlot

class AmorExpPanel(ExpPanel):

    def __init__(self, parent, client, options):
        ExpPanel.__init__(self, parent, client, options)

        # This field is not used on AMOR, hence we hide it to reduce confusion
        self.sampleName.setVisible(False)
        self.sampleNameLabel.setVisible(False)
        self.sampleNameDivider.setVisible(False)

    @pyqtSlot()
    def on_queryDBButton_clicked(self):
        ExpPanel.on_queryDBButton_clicked(self)
        scriptpath_name = self._scriptpath_name()
        if scriptpath_name:
            self.scriptPathLine.setText(scriptpath_name)

    def applyChanges(self):
        scriptpath = self.scriptPathLine.text()
        self.client.run(f'Exp.scriptpath = "{scriptpath}"')
        ExpPanel.applyChanges(self)
        self.client.run(f'Exp.createUserPaths("{scriptpath}")')

    def _scriptpath_name(self):
        users = splitUsers(self.users.text())
        try:
            user_name_components = users[0]['name'].split()
        except IndexError:
            return None
        if len(user_name_components) < 2:
            return None
        last_name = user_name_components[1]
        first_name = user_name_components[0]
        last_first_name = '_'.join([last_name, first_name]).lower()
        year_month = date.today().isoformat()[:-3]
        return path.join('/home', 'sinquser', last_first_name, year_month, 'scripts')

    def on_client_experiment(self, data):
        ExpPanel.on_client_experiment(self, data)
        if data[1] == 'service':
            self.scriptPathLine.setText(path.join('/home', 'sinquser', 'service', 'scripts'))
