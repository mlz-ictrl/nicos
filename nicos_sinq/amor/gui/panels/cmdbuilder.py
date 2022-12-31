#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from nicos.clients.flowui.panels import get_icon
from nicos.clients.flowui.panels.cmdbuilder import \
    CommandPanel as DefaultCommandPanel
from nicos.guisupport.qt import pyqtSlot

from nicos_sinq.amor.gui import uipath


class CommandPanel(DefaultCommandPanel):
    ui = f'{uipath}/panels/ui_files/cmdbuilder.ui'

    def set_icons(self):
        DefaultCommandPanel.set_icons(self)
        self.pauseBtn.setIcon(get_icon('stop-24px.svg'))
        self.emergencyStopBtn.setIcon(
            get_icon('emergency_stop_cross_red-24px.svg')
            )
        self.pause = False

    @pyqtSlot()
    def on_pauseBtn_clicked(self):
        self.client.tell_action('stop')

    @pyqtSlot()
    def on_emergencyStopBtn_clicked(self):
        self.client.tell_action('emergency')
