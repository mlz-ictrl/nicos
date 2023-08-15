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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

import numpy as np

from nicos.clients.gui.panels.live import LiveDataPanel


class TThetaLiveDataPanel(LiveDataPanel):

    def setData(self, arrays, labels=None, titles=None, uid=None, display=True):

        # This will cache the original data, but does not display it
        if uid:
            LiveDataPanel.setData(self, arrays, labels, titles, uid=uid,
                                  display=False)

        ttheta = arrays[0][0]
        counts = arrays[0][1]

        labels = {'x': np.array(ttheta)}
        titles = {'x': '2θ [deg]', 'y': 'counts'}
        # This will display the modified data, but does not cache it..
        LiveDataPanel.setData(self, np.array([counts]), labels, titles,
                              uid=None, display=display)

    # def _initLiveWidget(self, array):
    #    self.initLiveWidget(LiveWidget1D)
