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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.clients.gui.panels.live import LiveDataPanel as BaseLiveDataPanel


class LiveDataPanel(BaseLiveDataPanel):
    """Special live view with grayscale and disabled keep ratio."""

    def _initLiveWidget(self, array):
        BaseLiveDataPanel._initLiveWidget(self, array)
        # Set the grayscale as default
        for action in self.actionsColormap.actions():
            if action.data().upper() == 'GRAYSCALE':
                action.trigger()
                break
        # Set keep ratio as not active as default
        if self.actionKeepRatio.isChecked():
            self.actionKeepRatio.trigger()
