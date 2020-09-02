#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2020 by the NICOS contributors (see AUTHORS)
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
from nicos.guisupport.livewidget import LiveWidget1D


class FullScreen1DWidget(LiveWidget1D):

    def __init__(self, parent):
        LiveWidget1D.__init__(self, parent)
        self.plot.viewport = [0.02, .98, 0.1, .98]
        self.plot.xlabel = 'channel'
        self.plot.ylabel = 'counts'
        self.axes.xdual = False
        self.axes.ticksize = 0.005


class LiveDataPanel(BaseLiveDataPanel):

    def initLiveWidget(self, widgetcls):
        if widgetcls == LiveWidget1D:
            widgetcls = FullScreen1DWidget
        BaseLiveDataPanel.initLiveWidget(self, widgetcls)
