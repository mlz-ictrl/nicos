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
#   Ebad Kamil <ebad.kamil@ess.eu>
#
# *****************************************************************************

from pathlib import Path

import numpy as np

from nicos.clients.flowui.panels import get_icon
from nicos.clients.flowui.panels.live import \
    LiveDataPanel as DefaultLiveDataPanel
from nicos.guisupport.qt import QFileDialog, pyqtSlot


class LiveDataPanel(DefaultLiveDataPanel):
    ui = f'{Path(__file__).parent}/ui_files/live.ui'

    def __init__(self, parent, client, options):
        DefaultLiveDataPanel.__init__(self, parent, client, options)
        self.last_save_location = None
        self.setControlsEnabled(False)

    def createPanelToolbar(self):
        toolbar = DefaultLiveDataPanel.createPanelToolbar(self)
        toolbar.addSeparator()
        toolbar.addAction(self.actionSaveData)
        return toolbar

    def set_icons(self):
        DefaultLiveDataPanel.set_icons(self)
        self.actionSaveData.setIcon(get_icon('archive-24px.svg'))

    @pyqtSlot()
    def on_actionSaveData_triggered(self):
        self.export_data_to_file()

    def export_data_to_file(self):
        filename = QFileDialog.getSaveFileName(
            self,
            'Save image',
            str(Path.home())
            if self.last_save_location is None
            else self.last_save_location,
            'Numpy binary files (*.npy)',
            initialFilter='*.npy',
        )[0]

        if not filename:
            return
        filename = Path(filename).with_suffix('.npy')
        self.last_save_location = str(filename.parent)

        data = self._extract_data()

        if data:
            np.save(filename, np.array(data[0]))
        else:
            self.showError(f'No data available for writing to {filename}')

    def _extract_data(self):
        if self.fileList.currentRow() == -1:
            self.fileList.setCurrentRow(0)
        # try to get data from the cache
        item = self.fileList.currentItem()

        current_blob = self.getDataFromItem(item)
        if not current_blob:
            return None, None

        data = current_blob.get('dataarrays', [])
        return data
