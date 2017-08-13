#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
"""SPODI live data panel."""

import numpy

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QFont, QGridLayout, QSizePolicy, QStatusBar

from nicos.clients.gui.panels import Panel

try:
    from nicos_mlz.spodi.gui.panels.live.livegrplot import LiveDataPlot
except ImportError:
    from nicos_mlz.spodi.gui.panels.live.liveqwtplot import LiveDataPlot

# the empty string means: no live data is coming, only the filename is important
DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4', ''))


class LiveDataPanel(Panel):

    panelName = 'Live data'
    bar = None
    menu = None

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.user_color = Qt.white
        self.user_font = QFont('monospace')

        self.dataPlot = LiveDataPlot(self, self)
        self.gridLayout.addWidget(self.dataPlot, 0, 0, 1, 1)

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.gridLayout.addWidget(self.statusBar, 1, 0, 1, 1)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('setup'), self.on_client_connected)

    def on_client_livedata(self, data):
        if data:
            d = numpy.frombuffer(data, dtype=self._dtype)
            if sum(d):
                d = numpy.reshape(d, (self._nx, self._ny), order='F')
                det = self.client.eval('adet._startpos, adet.resosteps, '
                                       'adet.range', None)
                step = det[2] / det[1]
                # The orientation of the tths is in negative direction but
                # it will be used in positive direction to avoid type the '-'
                # for each position in the frontend
                start = det[0] - (det[2] - step)
                end = start + self._nx * step
                self.dataPlot.setCurveData((numpy.arange(start, end, step),
                                            numpy.sum(d, axis=1)))

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata', 'liveparams'])

    def on_client_liveparams(self, params):
        # TODO: remove compatibility code
        if len(params) == 7:  # Protocol version < 16
            _tag, _fname, dtype, nx, ny, _nz, runtime = params
        elif len(params) == 9:  # Protocol version >= 16
            _tag, _uid, _det, _fname, dtype, nx, ny, _nz, runtime = params

        self.statusBar.showMessage('Runtime: %.1f s' % runtime)
        normalized_type = numpy.dtype(dtype).str if dtype else ''
        if not _fname and normalized_type not in DATATYPES:
            self.log.warning('Unsupported live data format: %s', params)
            return
        self._dtype = normalized_type
        self._nx, self._ny = nx, ny

    def setOptions(self, options):
        Panel.setOptions(self, options)
        if self.client.isconnected:
            self.on_client_connected()
