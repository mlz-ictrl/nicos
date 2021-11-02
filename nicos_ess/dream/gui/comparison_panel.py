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

from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import numpy as np

from nicos.clients.flowui.panels import get_icon
from nicos.clients.gui.panels.live import FILENAME, FILETAG, FILEUID, \
    LiveDataPanel
from nicos.core.constants import LIVE
from nicos.guisupport.qt import QAction, QCursor, QFileDialog, QInputDialog, \
    QLineEdit, QMenu, Qt, QToolBar, QVBoxLayout, pyqtSlot
from nicos.utils import BoundedOrderedDict

from nicos_ess.dream.gui.comparison_plot_widgets import ComparisonPlot1D, \
    ComparisonPlot2D
from nicos_ess.dream.gui.normalisers import NormaliserFactory, NormaliserType

SNAP = 'snap'


class ComparisonPanel(LiveDataPanel):
    """ComparisonPanel class"""

    _available_normalisers = OrderedDict({
        '': NormaliserType.NONORMALISER,
        'INTEGRAL': NormaliserType.INTEGRAL,
    })
    ui = f'{Path(__file__).parent}/ui_files/comparison_panel.ui'

    def __init__(self, parent, client, options):
        self.widgetLayout = QVBoxLayout()
        LiveDataPanel.__init__(self, parent, client, options)
        self.setupUi()
        self.init_connections()
        client.livedata.connect(self.on_live_data_update)

        self._init_right_click_context_menu()
        self._reset_reference_data()

        self.last_save_location = None

        self.reference_data_1d = None
        self.reference_data_2d = None
        self._normaliser = NormaliserFactory.create(
            NormaliserType.NONORMALISER
        )
        self._show_difference = True
        self._snap_cache = BoundedOrderedDict(maxlen=10)

    def init_connections(self):
        self.norm_cb.currentTextChanged.connect(
            self._on_norm_change)
        self.showDifferenceButton.toggled.connect(
            self._on_show_difference)

    def getToolbars(self):
        return []

    def setupUi(self):
        for v in self._available_normalisers:
            self.norm_cb.addItem(v)

        self._plot_1d = ComparisonPlot1D(
            '', 'x', 'y', 2, parent=self.plot_1d
        )
        self._plot_2d = ComparisonPlot2D('', parent=self.plot_2d)

        self.toolbar = QToolBar()
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionSaveData)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionLogScale)
        self.toolbar.addAction(self.actionUnzoom)

        self.actionUnzoom.setIcon(get_icon('zoom_out-24px.svg'))
        self.actionOpen.setIcon(get_icon('folder_open-24px.svg'))
        self.actionSaveData.setIcon(get_icon('archive-24px.svg'))
        self.layout().setMenuBar(self.toolbar)

        # Hide tabs during initialization. Will become visible when data arrives
        for index in range(self.tabWidget.count()):
            self.tabWidget.setTabVisible(index, False)

        self.setControlsEnabled(True)

    def on_fileList_currentItemChanged(self):
        self.on_live_data_update()

    def _show(self, data=None):
        pass

    def on_live_data_update(self):
        data = self._get_data()
        if data:
            self.set_live_data(data)

    def _get_data(self):
        name, data, labels = self._extract_data()
        if data:
            return name, labels, data[0]
        return

    def _extract_data(self):
        if self.fileList.currentRow() == -1:
            self.fileList.setCurrentRow(0)
        # try to get data from the cache
        item = self.fileList.currentItem()
        name = item.data(FILENAME)
        if item.data(FILETAG) == LIVE:
            name = f'LIVE {int(name) + 1}'

        current_blob = self.getDataFromItem(item)
        if not current_blob:
            return None, None, None

        data = current_blob.get('dataarrays', [])
        labels = current_blob.get('labels', {})
        return name, data, labels

    def getDataFromItem(self, item):
        if item is None:
            return

        uid = item.data(FILEUID)
        if uid and hasattr(self, '_snap_cache') and uid in self._snap_cache:
            return self._snap_cache[uid]
        else:
            return LiveDataPanel.getDataFromItem(self, item)

    def remove_obsolete_cached_files(self):
        for index in reversed(range(self.fileList.count())):
            item = self.fileList.item(index)
            uid = item.data(FILEUID)
            # is the uid still cached
            if uid and uid not in self._datacache and uid not in self._snap_cache:
                # does the file still exist on the filesystem
                if Path(item.data(FILENAME)).is_file():
                    item.setData(FILEUID, None)
                else:
                    self.fileList.takeItem(index)

    def _init_right_click_context_menu(self):
        self.fileList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self):
        menu = QMenu()

        edit_action = QAction('Rename', self)
        edit_action.triggered.connect(self._rename_snapshot)
        edit_action.setIcon(get_icon('edit-24px.svg'))
        menu.addAction(edit_action)

        delete_action = QAction('Remove', self)
        delete_action.triggered.connect(self._remove_snapshot)
        delete_action.setIcon(get_icon('cut_24px.svg'))
        menu.addAction(delete_action)

        menu.exec_(QCursor.pos())

    def _on_norm_change(self, value):
        self._normaliser = NormaliserFactory.create(
            self._available_normalisers[value]
        )
        self.on_live_data_update()

    def _on_show_difference(self, state):
        self._show_difference = state
        self.on_live_data_update()

    def _update_1d_plot(self, data_blob=None):
        if not data_blob and not self.reference_data_1d:
            return

        def _extract_data(blob):
            labels, data = blob
            return labels["x"] if labels else np.arange(data.shape[0]), data

        x1, y1, x2, y2 = [None] * 4
        if data_blob:
            x1, y1 = _extract_data(data_blob)
            y1 = self._normaliser.normalise(y1, x1)

        if self.reference_data_1d:
            x2, y2 = _extract_data(self.reference_data_1d)
            y2 = self._normaliser.normalise(y2, x2)

        self._plot_1d.setData(x1, y1, x2, y2, difference=np.array_equal(x1, x2))

    def _update_2d_plot(self, data_blob=None):
        if not data_blob and not self.reference_data_2d:
            return

        if not data_blob and self.reference_data_2d:
            self._plot_2d.setData(
                self.reference_data_2d[1], labels=self.reference_data_2d[0]
            )

        if data_blob:
            labels, data = data_blob
            if (
                self.reference_data_2d
                and data.shape == self.reference_data_2d[1].shape
            ):
                data = (
                    data - self.reference_data_2d[1]
                    if self._show_difference
                    else data + self.reference_data_2d[1]
                )

            self._plot_2d.setData(data, labels=labels)

    def set_live_data(self, blob):
        _, labels, data = blob
        self._set_tab_visibility(data.ndim)
        if data.ndim == 1:
            self._update_1d_plot((labels, data))
        elif data.ndim == 2:
            self._update_2d_plot((labels, data))

    def _set_tab_visibility(self, dim):
        visibile_tab_index = self.tabWidget.indexOf(self.tab_1d) \
            if dim == 1 else self.tabWidget.indexOf(self.tab_2d)

        for index in range(self.tabWidget.count()):
            self.tabWidget.setTabVisible(index, index == visibile_tab_index)

    def _set_reference_data(self):
        blob = self._get_data()
        if not blob:
            return

        name, labels, data = blob
        msg = f'Reference: {name} \nSet at: '

        if data.ndim == 1:
            self.reference_data_1d = (labels, data)
            self._update_1d_plot()
            self.status_1d.setText(f'{msg} {datetime.now()}')
        elif data.ndim == 2:
            self.reference_data_2d = (labels, data)
            self._update_2d_plot()
            self.status_2d.setText(f'{msg} {datetime.now()}')

    def _reset_reference_data(self):
        self.reference_data_1d = None
        self.reference_data_2d = None
        self._plot_1d.reset_reference()
        msg = 'No reference available'
        self.status_1d.setText(msg)
        self.status_2d.setText(msg)

    def _remove_snapshot(self):
        item = self.fileList.currentItem()
        if self._is_item_snapshot(item):
            uid = item.data(FILEUID)
            if uid and uid in self._snap_cache:
                self.fileList.takeItem(self.fileList.row(item))
                del self._snap_cache[uid]

    def _rename_snapshot(self):
        item = self.fileList.currentItem()
        if self._is_item_snapshot(item):
            new_name, ok = QInputDialog.getText(
                self, 'Rename', '', QLineEdit.Normal, item.text()
            )
            if ok and new_name:
                item.setText(new_name)
                item.setData(FILENAME, new_name)

    def _is_item_snapshot(self, item):
        return item is not None and item.data(FILETAG) == SNAP

    def export_data_to_file(self):
        """Saves data of the currently selected item on the fileList widget.
        Note: Does not save reference data and difference.
        """
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

        _, data, _ = self._extract_data()

        if data:
            np.save(filename, np.array(data[0]))
        else:
            self.showError(f'No data available for writing to {filename}')

    @pyqtSlot()
    def on_actionLogScale_triggered(self):
        self._plot_2d.plot.logscale(self.actionLogScale.isChecked())
        self._plot_1d.plot.logscale(self.actionLogScale.isChecked())

    @pyqtSlot()
    def on_actionUnzoom_triggered(self):
        self._plot_2d.plot.unzoom()

    @pyqtSlot()
    def on_updateReferenceButton_clicked(self):
        self._set_reference_data()

    @pyqtSlot()
    def on_resetReferenceButton_clicked(self):
        self._reset_reference_data()

    @pyqtSlot()
    def on_snapShotButton_clicked(self):
        _, data, labels = self._extract_data()
        if not data:
            return
        uid = uuid4()
        self._snap_cache[uid] = {'dataarrays': data, 'labels': labels}
        self.add_to_flist(f'snapshot_{datetime.now()}', '', SNAP, uid)

    @pyqtSlot()
    def on_actionSaveData_triggered(self):
        self.export_data_to_file()
