#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""NICOS livewidget for SINQ: we want to be able to show plots of scanfiles.
A slider allows to select which scanpoint to display"""

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from nicos.clients.flowui.panels.live import \
    LiveDataPanel as FlowuiLiveDataPanel
from nicos.guisupport.qt import QSlider, QVBoxLayout, QWidget


class ScanSlider(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        self.slider = QSlider(Qt.Horizontal, self)
        self.title = QLabel('Scanpoint selection', self)
        self.title.setMaximumHeight(25)
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.slider)
        self.layout().addSpacing(15)


class LiveDataPanel(FlowuiLiveDataPanel):
    def __init__(self, parent, client, options):
        FlowuiLiveDataPanel.__init__(self, parent, client, options)
        self.scan_slider = ScanSlider(parent)
        self.scan_slider.setMaximumHeight(90)
        self.layout().insertWidget(self.layout().count() - 1, self.scan_slider)
        self.scan_slider.hide()
        self._arrays = []
        self.scan_slider.slider.valueChanged.connect(self._update_scan_slice)

    def _show(self, data=None):
        """Same as the default, but if data has dimension 3 assumes that the
        first dimension is the scanpoint set.
        In that case shows a slider that allow to scroll and display all the
        scanpoints images.
        """

        idx = self.fileList.currentRow()
        if idx == -1:
            self.fileList.setCurrentRow(0)
            return

        # no data has been provided, try to get it from the cache
        if data is None:
            data = self.getDataFromItem(self.fileList.currentItem())
            # still no data
            if data is None:
                return

        arrays = data.get('dataarrays', [])
        labels = data.get('labels', {})
        titles = data.get('titles', {})

        if len(np.asarray(arrays).shape) == 4:
            _arrays = np.asarray(arrays)
            self.scan_slider.show()
            self.scan_slider.slider.setMaximum(_arrays.shape[1] - 1)
            self.scan_slider.title.setText(
                f'Scanpoint selection: <# {self.scan_slider.slider.value()+1}>')

            _arrays = _arrays[:, self.scan_slider.slider.value(), ...]
        else:
            _arrays = np.asarray(arrays)
            self.scan_slider.hide()

        # if multiple datasets have to be displayed in one widget, they have
        # the same dimensions, so we only need the dimensions of one set
        self._initLiveWidget(_arrays)
        self.applyPlotSettings()
        for widget in self._get_all_widgets():
            widget.setData(_arrays, labels)
            widget.setTitles(titles)

        if self.unzoom and self.widget:
            self.on_actionUnzoom_triggered()

    def _update_scan_slice(self):
        # the signal triggering _show() directly might cause an exception.
        # Looks like this prevents it
        self._show()
