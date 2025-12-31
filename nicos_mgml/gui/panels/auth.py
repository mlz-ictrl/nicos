# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
from nicos.guisupport.qt import QSizePolicy, Qt


class ConnectionDialog(ParentConDiag):
    """Simple panel showing image."""

    def __init__(self, parent, connpresets, lastpreset, lastdata, tunnel=''):
        ParentConDiag.__init__(self, parent, connpresets, lastpreset, lastdata,
                               tunnel=tunnel)
        self.setWindowFlags(
            Qt.Window
            | Qt.CustomizeWindowHint
            | Qt.FramelessWindowHint
            | Qt.Tool)
        # the positions of the spacers are taken from the UI file
        # verticalSpacerTop
        self.layout().itemAtPosition(0, 1).changeSize(
            1, 1, vPolicy=QSizePolicy.Policy.MinimumExpanding)
        # verticalSpacerBottom
        self.layout().itemAtPosition(6, 1).changeSize(
            1, 1, vPolicy=QSizePolicy.Policy.MinimumExpanding)
        # horizontalSpacerLeft
        self.layout().itemAtPosition(1, 0).changeSize(
            1, 1, hPolicy=QSizePolicy.Policy.MinimumExpanding)
        # horizontalSpacerRight
        self.layout().itemAtPosition(1, 3).changeSize(
            1, 1, hPolicy=QSizePolicy.Policy.MinimumExpanding)
        self.showFullScreen()
