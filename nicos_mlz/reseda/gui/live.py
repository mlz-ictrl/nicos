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

from os import path

import numpy as np

from nicos.clients.gui.panels.live import LiveDataPanel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QWidget

uipath = path.dirname(__file__)


class CascadeControls(QWidget):

    controlsui = f'{uipath}/cascadecontrols.ui'

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(self, self.controlsui)
        # for w in (self.foilLabel, self.foilBox, self.timeChannelLabel,
        #           self.timeChannelBox):
        #     w.setHidden(True)
        self.setHidden(True)
        self.setFoilsOrder([])

    def initControls(self, data):
        imagedata = len(data.shape) < 3
        self.setHidden(imagedata)
        if not imagedata:
            foilsnumber = data.shape[0]
            self.foilBox.setMaximum(foilsnumber)
            self.timeChannelBox.setMaximum(data.shape[1])
            self.setFoilsOrder(list(range(foilsnumber)))

    def handleData(self, data):
        if len(data.shape) == 2:
            return data
        foil = self.foilBox.value()
        time_channel = self.timeChannelBox.value()
        if not (foil or time_channel):
            return np.sum(data, axis=(0, 1))
        if time_channel:
            if foil:
                return data[self._foilsorder.index(foil - 1)][time_channel - 1]
            return np.sum(data, axis=0)[time_channel - 1]
        return np.sum(data, axis=1)[self._foilsorder.index(foil - 1)]

    def setFoilsOrder(self, foilsorder):
        self._foilsorder = foilsorder


class CascadeLiveDataPanel(LiveDataPanel):

    def __init__(self, parent, client, options):
        LiveDataPanel.__init__(self, parent, client, options)

    def _initControlsGUI(self):
        self.controls = CascadeControls()
        self.splitter.addWidget(self.controls)
        self.controls.foilBox.valueChanged.connect(self.showData)
        self.controls.timeChannelBox.valueChanged.connect(self.showData)

    def showData(self):
        idx = self.fileList.currentRow()
        if idx == -1:
            self.fileList.setCurrentRow(0)
            return

        data = self.getDataFromItem(self.fileList.currentItem())
        if data is None:  # no data
            return

        arrays = data.get('dataarrays', [])
        labels = data.get('labels', {})
        titles = data.get('titles', {})

        # copy to avoid modifications of original data
        self.controls.setFoilsOrder(
            self.client.eval('psd_channel.foilsorder', []))

        # if multiple datasets have to be displayed in one widget, they have
        # the same dimensions, so we only need the dimensions of one set
        self.controls.initControls(arrays[0])
        self._initLiveWidget(self.controls.handleData(arrays[0]))
        self.applyPlotSettings()

        self._setData(arrays, labels, titles)

        if self.unzoom and self.widget:
            self.on_actionUnzoom_triggered()

    def _setData(self, arrays, labels, titles):
        arrs = [self.controls.handleData(array) for array in arrays]
        for widget in self._get_all_widgets():
            widget.setData(arrs, labels)
            widget.setTitles(titles)

    def _show(self, params=None, data=None):
        self.showData()

    def setData(self, arrays, labels=None, titles=None, uid=None, display=True):
        """Dispatch data array to corresponding live widgets.

        Cache array based on uid parameter. No caching if uid is ``None``.
        """
        if uid:
            if uid not in self._datacache:
                self.log.debug('add to cache: %s', uid)
                self._datacache[uid] = {}
            self._datacache[uid]['dataarrays'] = arrays
        if display:
            if uid:
                if titles is None:
                    titles = self._datacache[uid].get('titles')
                if labels is None:
                    labels = self._datacache[uid].get('labels')
            self.controls.initControls(arrays[0])
            arr = self.controls.handleData(arrays[0])
            self._initLiveWidget(arr)
            self._setData([arr], labels, titles)
