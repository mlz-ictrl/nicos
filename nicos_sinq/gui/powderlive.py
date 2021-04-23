#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
"""
  A live view which shows a powder diagram with the correct two_theta and a
  title.
"""
import numpy

from nicos.clients.gui.panels.live import IntegralLiveWidget, LiveDataPanel, \
    LiveWidget1D


class LivePowderWidget(LiveWidget1D):
    def __init__(self, parent, **kwargs):
        LiveWidget1D.__init__(self, parent, **kwargs)

    def _setData(self, array, nx, ny, nz, newrange):
        start = float(self.client.getCacheKey('s2t/value')[1])
        self.curve.x = numpy.linspace(start,start+nx*self.tthstep,nx)
        self.curve.y = numpy.ma.masked_equal(self._array.ravel(), 0).astype(
            numpy.float)
        self.curve.filly = .1 if self._logscale else 0
        self.axes.setWindow(start,start+nx*self.tthstep,0,ny)
        title = self.client.getCacheKey('exp/title')[1]
        self.plot.title = title
        self.plot._title = title

    def setWidgetData(self,client,tthstep):
        self.client = client
        self.tthstep = tthstep


class LivePowderPanel(LiveDataPanel):

    panelName = 'Live Powder View'
    """
    This panel draws a powder diagram with a two theta axis generated from the
    position of the detector, the tthstep option and the length of the data
    array passed in the livedata event.

    Options:
    * ``tthstep`` (default 0.1) -- The detector stepping two theta
    """
    def __init__(self, parent, client, options):
        LiveDataPanel.__init__(self,parent,client,options)
        self.tthstep = float(options.get('tthstep','0.1'))

    def _initLiveWidget(self, array):
        """Initialize livewidget based on array's shape"""
        if len(array.shape) == 1:
            widgetcls = LivePowderWidget
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)

    def initLiveWidget(self, widgetcls):
        LiveDataPanel.initLiveWidget(self,widgetcls)
        if isinstance(self.widget,LivePowderWidget):
            self.widget.setWidgetData(self.client,self.tthstep)
