#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI single cmdlet command input."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels.cmdbuilder import \
    CommandPanel as DefaultCommandPanel
from nicos.guisupport.qt import pyqtSlot

from nicos_ess.gui import uipath
from nicos_ess.gui.panels import get_icon


class CommandPanel(DefaultCommandPanel):
    """Extends the CommandPanel with a button that toggles the
    SelectCommand widget.
    """

    panelName = 'Command'
    ui = '%s/panels/cmdbuilder.ui' % uipath
    frame_visible = False

    def __init__(self, parent, client, options):
        DefaultCommandPanel.__init__(self, parent, client, options)
        self.set_icons()

    def set_icons(self):
        self.cmdBtn.setIcon(get_icon('add-24px.svg'))
        self.simBtn.setIcon(get_icon('play_arrow_outline-24px.svg'))
        self.runBtn.setIcon(get_icon('play_arrow-24px.svg'))
        self.frame.hide()

    def toggle_frame(self):
        self.frame_visible = not self.frame_visible
        self.frame.setVisible(self.frame_visible)
        self.cmdBtn.setText('Hide Cmd' if self.frame_visible else 'New Cmd')
        self.cmdBtn.setIcon(get_icon('remove-24px.svg' if self.frame_visible
                                     else 'add-24px.svg'))

    @pyqtSlot()
    def on_cmdBtn_clicked(self):
        self.toggle_frame()

    @pyqtSlot()
    def on_runBtn_clicked(self):
        DefaultCommandPanel.on_runBtn_clicked(self)
        self.commandInput.clear()

    def on_commandInput_execRequested(self, script, action):
        DefaultCommandPanel.on_commandInput_execRequested(self, script, action)
        self.commandInput.clear()
