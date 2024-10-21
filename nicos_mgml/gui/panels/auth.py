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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""NICOS MGML GUI auth module."""

from nicos.clients.gui.dialogs.auth import ConnectionDialog as ParentConDiag
from nicos.guisupport.qt import Qt
from nicos.utils import findResource

from nicos_mgml.gui import uipath


class ConnectionDialog(ParentConDiag):
    """Simple panel showing image."""

    ui = findResource(f'{uipath}/panels/auth.ui')

    def __init__(self, parent, connpresets, lastpreset, lastdata, tunnel=''):
        ParentConDiag.__init__(self, parent, connpresets, lastpreset, lastdata,
                               tunnel=tunnel)
        self.setWindowFlags(
            Qt.Window
            | Qt.CustomizeWindowHint
            | Qt.FramelessWindowHint
            | Qt.Tool)
        self.showFullScreen()
