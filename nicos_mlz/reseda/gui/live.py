# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

import numpy

from nicos.clients.gui.panels.live import LiveDataPanel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QWidget

uipath = path.dirname(__file__)


class CascadeControls(QWidget):

    controlsui = f'{uipath}/cascadecontrols.ui'

    foilsnumber = 0

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(self, self.controlsui)
        for w in (self.foilLabel, self.foilBox, self.timeChannelLabel,
                  self.timeChannelBox):
            w.setHidden(True)
        self.singleSlidesBox.setDisabled(True)
        self.setFoilsOrder(list(range(self.foilsnumber)))

    def initControls(self, data):
        imagedata = len(data.shape) < 3
        self.singleSlidesBox.setDisabled(imagedata)
        if imagedata:
            self.singleSlidesBox.setChecked(False)
        else:
            self.foilBox.setMaximum(self.foilsnumber)
            self.timeChannelBox.setMaximum(data.shape[0] // self.foilsnumber)

    def handleData(self, data):
        if len(data.shape) > 2:
            if self.singleSlidesBox.isChecked():
                foil = self._foilsorder.index(self.foilBox.value() - 1)
                time_channel = self.timeChannelBox.value()
                timechannels = data.shape[0] // self.foilsnumber
                if time_channel:
                    idx = foil * timechannels + time_channel - 1
                    return data[idx]
                startfoil = foil * timechannels
                return numpy.sum(data[startfoil:startfoil + timechannels],
                                 axis=0)
            return numpy.sum(data, axis=0)
        return data

    def setFoilsOrder(self, foilsorder):
        self._foilsorder = foilsorder
        self.foilsnumber = len(foilsorder)


class CascadeLiveDataPanel(LiveDataPanel):

    def __init__(self, parent, client, options):
        LiveDataPanel.__init__(self, parent, client, options)

    def _initControlsGUI(self):
        self.controls = CascadeControls()
        self.splitter.addWidget(self.controls)
        self.controls.singleSlidesBox.toggled.connect(self.showData)
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
            self._initLiveWidget(arrays[0])
            self._setData(arrays, labels, titles)
