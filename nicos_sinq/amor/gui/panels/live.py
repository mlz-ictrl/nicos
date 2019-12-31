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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels.livegr import LiveDataPanel as BaseLiveDataPanel
from nicos.guisupport.livewidget import IntegralLiveWidget as BaseIntegralLiveWidget, \
    LiveWidget1D as BaseLiveWidget1D, Plot


class ProvidesTitleSetter(object):
    """Provides function to set the the title of the plot
    """

    def setPlotTitle(self, title):
        if hasattr(self, 'plot') and isinstance(self.plot, Plot):
            self.plot.title = title


class SingleDetectorLiveWidget(ProvidesTitleSetter, BaseLiveWidget1D):
    def __init__(self, parent):
        BaseLiveWidget1D.__init__(self, parent)
        self.plot.viewport = [0.1, .95, 0.1, .85]


class IntegralLiveWidget(ProvidesTitleSetter, BaseIntegralLiveWidget):
    def __init__(self, parent):
        BaseIntegralLiveWidget.__init__(self, parent)
        self.plot.viewport = [.1, .75, .1, .70]
        self.plotxint.viewport = [.8, .95, .1, .70]


class LiveDataPanel(BaseLiveDataPanel):
    """In addition to the base class, also sets the title of the plots
    """

    def __init__(self, parent, client, options):
        BaseLiveDataPanel.__init__(self, parent, client, options)
        self._plot_titles = []

    def _initLiveWidget(self, array):
        if len(array.shape) == 1:
            widgetcls = SingleDetectorLiveWidget
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)

    def on_client_liveparams(self, params):
        BaseLiveDataPanel.on_client_liveparams(self, params)
        _, _, _, fname, _, _, _, _, _ = params
        self._plot_titles = fname
        if len(self._plot_titles) == len(self.liveitems):
            for item, title in zip(self.liveitems, self._plot_titles):
                item.setText(title)

    def setData(self, array, uid=None, display=True):
        BaseLiveDataPanel.setData(self, array, uid, display)
        if display:
            self.widget.setPlotTitle(self._plot_titles[self._livechannel])
