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
#
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""LoKI Script Builder Panel."""

import os.path as osp
from collections import OrderedDict
from functools import partial

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAction, QApplication, QCursor, QFileDialog, \
    QHeaderView, QKeySequence, QMenu, QShortcut, Qt, QTableView, pyqtSlot
from nicos.utils import findResource

from nicos_ess.gui.panels import get_icon
from nicos_ess.loki.gui.loki_panel import LokiPanelBase
from nicos_ess.loki.gui.loki_script_generator import ScriptFactory, TransOrder
from nicos_ess.loki.gui.loki_scriptbuilder_model import LokiScriptModel
from nicos_ess.utilities.csv_utils import export_table_to_csv, \
    import_table_from_csv
from nicos_ess.utilities.table_utils import convert_table_to_clipboard_text, \
    extract_table_from_clipboard_text

TABLE_QSS = 'alternate-background-color: aliceblue;'


class LokiScriptBuilderPanel(LokiPanelBase):
    _available_trans_options = OrderedDict({
        'All TRANS First': TransOrder.TRANSFIRST,
        'All SANS First': TransOrder.SANSFIRST,
        'TRANS then SANS': TransOrder.TRANSTHENSANS,
        'SANS then TRANS': TransOrder.SANSTHENTRANS,
        'Simultaneous': TransOrder.SIMULTANEOUS
    })

    def __init__(self, parent, client, options):
        LokiPanelBase.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui')
               )

        self.window = parent
        self.duration_options = ['Mevents', 'seconds', 'frames']

        self.permanent_columns = {
            'position': 'Position',
            'sample': 'Sample',
            'thickness': 'Thickness\n(mm)',
            'trans_duration': 'TRANS Duration',
            'sans_duration': 'SANS Duration'
        }

        self.optional_columns = {
            'temperature': ('Temperature', self.chkShowTempColumn),
            'pre-command': ('Pre-command', self.chkShowPreCommand),
            'post-command': ('Post-command', self.chkShowPostCommand)
        }
        # Set up trans order combo-box
        self.comboTransOrder.addItems(self._available_trans_options.keys())

        self.columns_in_order = list(self.permanent_columns.keys())
        self.columns_in_order.extend(self.optional_columns.keys())
        self.last_save_location = None
        self._init_table_panel()
        self._init_right_click_context_menu()

    def _init_table_panel(self):
        headers = [
            self.permanent_columns[name]
            if name in self.permanent_columns
            else self.optional_columns[name][0]
            for name in self.columns_in_order
        ]

        self.model = LokiScriptModel(headers)
        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QTableView.ContiguousSelection)

        for name, details in self.optional_columns.items():
            _, checkbox = details
            checkbox.stateChanged.connect(
                partial(self._on_optional_column_toggled, name))
            self._hide_column(name)

        self._link_duration_combobox_to_column('sans_duration',
                                               self.comboSansDurationType)
        self._link_duration_combobox_to_column('trans_duration',
                                               self.comboTransDurationType)

        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableView.resizeColumnsToContents()
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setStyleSheet(TABLE_QSS)

        self._create_keyboard_shortcuts()

    def _init_right_click_context_menu(self):
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self._show_context_menu)

    def _show_context_menu(self):
        menu = QMenu()

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self._handle_copy_cells)
        copy_action.setIcon(get_icon("file_copy-24px.svg"))
        menu.addAction(copy_action)

        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self._handle_cut_cells)
        cut_action.setIcon(get_icon("cut_24px.svg"))
        menu.addAction(cut_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self._handle_table_paste)
        paste_action.setIcon(get_icon("paste_24px.svg"))
        menu.addAction(paste_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self._delete_rows)
        delete_action.setIcon(get_icon("remove-24px.svg"))
        menu.addAction(delete_action)

        menu.exec_(QCursor.pos())

    def _create_keyboard_shortcuts(self):
        for key, to_call in [
            (QKeySequence.Paste, self._handle_table_paste),
            (QKeySequence.Cut, self._handle_cut_cells),
            (QKeySequence.Copy, self._handle_copy_cells),
            ("Ctrl+Backspace", self._delete_rows),
        ]:
            self._create_shortcut_key(key, to_call)

    def _create_shortcut_key(self, shortcut_keys, to_call):
        shortcut = QShortcut(shortcut_keys, self.tableView)
        shortcut.activated.connect(to_call)
        shortcut.setContext(Qt.WidgetShortcut)

    @pyqtSlot()
    def on_cutButton_clicked(self):
        self._handle_cut_cells()

    @pyqtSlot()
    def on_copyButton_clicked(self):
        self._handle_copy_cells()

    @pyqtSlot()
    def on_pasteButton_clicked(self):
        self._handle_table_paste()

    @pyqtSlot()
    def on_addAboveButton_clicked(self):
        self._insert_row_above()

    @pyqtSlot()
    def on_addBelowButton_clicked(self):
        self._insert_row_below()

    @pyqtSlot()
    def on_deleteRowsButton_clicked(self):
        self._delete_rows()

    @pyqtSlot()
    def on_loadTableButton_clicked(self):
        try:
            filename = QFileDialog.getOpenFileName(
                self,
                'Open table',
                osp.expanduser('~') if self.last_save_location is None \
                    else self.last_save_location,
                'Table Files (*.txt *.csv)')[0]

            if not filename:
                return

            headers_from_file, data = import_table_from_csv(filename)

            if not set(headers_from_file).issubset(set(self.columns_in_order)):
                raise AttributeError('incorrect headers in file')
            # Clear existing table before populating from file
            self.on_clearTableButton_clicked()
            self._fill_table(headers_from_file, data)

            for optional in set(headers_from_file).intersection(
                set(self.optional_columns.keys())):
                self.optional_columns[optional][1].setChecked(True)
        except Exception as error:
            self.showError(f'Could not load {filename}:  {error}')

    def _fill_table(self, headers, data):
        # corresponding indices of elements in headers_from_file list to headers
        indices = [index for index, element in
                   enumerate(self.columns_in_order) if element in headers]

        table_data = []
        for row in data:
            # create appropriate length list to fill the table row
            row = self._fill_elements(row, indices, len(self.columns_in_order))
            table_data.append(row)

        self.model.table_data = table_data

    def _fill_elements(self, row, indices, length):
        """Returns a list with row elements placed in the given indices.
        """
        if len(row) == length:
            return row
        result = [''] * length
        # Slicing similar to numpy arrays result[indices] = row
        for index, value in zip(indices, row):
            result[index] = value
        return result

    @pyqtSlot()
    def on_saveTableButton_clicked(self):
        if self.is_data_in_hidden_columns():
            self.showError('Cannot save because data in optional column(s).'
                           'Select the optional column or clear the column.')
            return

        filename = QFileDialog.getSaveFileName(
            self,
            'Save table',
            osp.expanduser('~') if self.last_save_location is None
            else self.last_save_location,
            'Table files (*.txt *.csv)',
            initialFilter='*.txt;;*.csv')[0]

        if not filename:
            return
        if not filename.endswith(('.txt', '.csv')):
            filename = filename + '.csv'

        self.last_save_location = osp.dirname(filename)
        try:
            headers = self._extract_headers_from_table()
            data = self._extract_data_from_table()
            export_table_to_csv(data, filename, headers)
        except Exception as ex:
            self.showError(f'Cannot write table contents to {filename}:\n{ex}')

    def is_data_in_hidden_columns(self):
        optional_indices = [index for index, element in
                            enumerate(self.columns_in_order)
                            if element in self.optional_columns.keys()]
        # Transform table_data to allow easy access to columns like data[0]
        data = list(zip(*self.model.table_data))
        return any(
            (any(data[column])
             for column in optional_indices
             if self.tableView.isColumnHidden(column)))

    def _extract_headers_from_table(self):
        headers = [column
                   for idx, column in enumerate(self.columns_in_order)
                   if not self.tableView.isColumnHidden(idx)]
        return headers

    def _extract_data_from_table(self):
        table_data = self.model.table_data
        # Remove hidden columns from data
        data = []
        for row, row_data in enumerate(table_data):
            relevant_column = []
            for column, column_data in enumerate(row_data):
                if not self.tableView.isColumnHidden(column):
                    relevant_column.append(column_data)
            data.append(relevant_column)
        # Remove the trailing empty rows
        for row, row_data in reversed(list(enumerate(data))):
            if any(row_data):
                break
            else:
                data.pop(row)
        return data

    def _delete_rows(self):
        rows_to_remove = set()
        for index in self.tableView.selectedIndexes():
            rows_to_remove.add(index.row())
        rows_to_remove = list(rows_to_remove)
        self.tableView.model().removeRows(rows_to_remove)

    def _insert_row_above(self):
        lowest, _ = self._get_selected_rows_limits()
        if lowest is not None:
            self.tableView.model().insertRow(lowest)
        elif self.model.num_rows == 0:
            self.tableView.model().insertRow(0)

    def _insert_row_below(self):
        _, highest = self._get_selected_rows_limits()
        if highest is not None:
            self.tableView.model().insertRow(highest + 1)
        elif self.model.num_rows == 0:
            self.tableView.model().insertRow(0)

    def _get_selected_rows_limits(self):
        lowest = None
        highest = None
        for index in self.tableView.selectedIndexes():
            if lowest is None:
                lowest = index.row()
                highest = index.row()
                continue
            lowest = min(lowest, index.row())
            highest = max(highest, index.row())
        return lowest, highest

    def _handle_cut_cells(self):
        self._handle_copy_cells()
        self._handle_delete_cells()

    def _handle_delete_cells(self):
        for index in self.tableView.selectedIndexes():
            self.model.update_data_at_index(index.row(), index.column(), '')

    def _handle_copy_cells(self):
        selected_data = self._extract_selected_data()
        clipboard_text = convert_table_to_clipboard_text(selected_data)
        QApplication.instance().clipboard().setText(clipboard_text)

    def _extract_selected_data(self):
        selected_indices = []
        for index in self.tableView.selectedIndexes():
            if self.tableView.isColumnHidden(index.column()):
                # Don't select hidden columns
                continue
            selected_indices.append((index.row(), index.column()))

        selected_data = self.model.select_data(selected_indices)
        return selected_data

    def _get_hidden_column_indices(self):
        return [idx for idx, _ in enumerate(self.columns_in_order)
                if self.tableView.isColumnHidden(idx)]

    def _get_hidden_column_names(self):
        return [name for idx, name in enumerate(self.columns_in_order)
                if self.tableView.isColumnHidden(idx)]

    def _handle_table_paste(self):
        indices = []
        for index in self.tableView.selectedIndexes():
            indices.append((index.row(), index.column()))

        if not indices:
            return
        top_left = indices[0]

        data_type = QApplication.instance().clipboard().mimeData()

        if not data_type.hasText():
            # Don't paste images etc.
            return

        clipboard_text = QApplication.instance().clipboard().text()
        copied_table = extract_table_from_clipboard_text(clipboard_text)

        if len(copied_table) == 1 and len(copied_table[0]) == 1:
            # Only one value, so put it in all selected cells
            self._do_bulk_update(copied_table[0][0])
            return

        self.model.update_data_from_clipboard(copied_table, top_left,
                                              self._get_hidden_column_indices())

    def _link_duration_combobox_to_column(self, column_name, combobox):
        combobox.addItems(self.duration_options)
        combobox.currentTextChanged.connect(
            partial(self._on_duration_type_changed, column_name))
        self._on_duration_type_changed(column_name,
                                       combobox.currentText())

    @pyqtSlot()
    def on_bulkUpdateButton_clicked(self):
        self._do_bulk_update(self.txtValue.text())

    def _do_bulk_update(self, value):
        for index in self.tableView.selectedIndexes():
            self.model.update_data_at_index(index.row(), index.column(), value)

    @pyqtSlot()
    def on_clearTableButton_clicked(self):
        self.model.clear()

    def _extract_labeled_data(self):
        hidden_column_names = self._get_hidden_column_names()
        labeled_data = []
        for row_data in self.model.table_data:
            labeled_row_data = dict(zip(self.columns_in_order, row_data))
            for key in hidden_column_names:
                del labeled_row_data[key]
            # Row will contribute to script only if all permanent columns
            # values are present
            if all(map(labeled_row_data.get, self.permanent_columns.keys())):
                labeled_data.append(labeled_row_data)
        return labeled_data

    @pyqtSlot()
    def on_generateScriptButton_clicked(self):
        if self.is_data_in_hidden_columns():
            self.showError('There is data in optional column(s) which will '
                           'not appear in the script')

        labeled_data = self._extract_labeled_data()

        if self._available_trans_options[self.comboTransOrder.currentText()]\
                == TransOrder.SIMULTANEOUS:
            if not all((data['sans_duration'] == data['trans_duration']
                        for data in labeled_data)):
                self.showError(
                        'Different SANS and TRANS duration specified in '
                        'SIMULTANEOUS mode. SANS duration will be used in '
                        'the script.'
                )

        _trans_order = self._available_trans_options[
            self.comboTransOrder.currentText()]
        template = ScriptFactory.from_trans_order(_trans_order).\
            generate_script(labeled_data,
                            self.comboTransDurationType.currentText(),
                            self.comboSansDurationType.currentText(),
                            self.sbTransTimes.value(),
                            self.sbSansTimes.value())

        self.mainwindow.codeGenerated.emit(template)

    def _on_optional_column_toggled(self, column_name, state):
        if state == Qt.Checked:
            self._show_column(column_name)
        else:
            self._hide_column(column_name)

    def _hide_column(self, column_name):
        column_number = self.columns_in_order.index(column_name)
        self.tableView.setColumnHidden(column_number, True)

    def _show_column(self, column_name):
        column_number = self.columns_in_order.index(column_name)
        self.tableView.setColumnHidden(column_number, False)

    def _on_duration_type_changed(self, column_name, value):
        column_number = self.columns_in_order.index(column_name)
        self._set_column_title(column_number,
                               f'{self.permanent_columns[column_name]}'
                               f'\n({value})')

    def _set_column_title(self, index, title):
        self.model.setHeaderData(index, Qt.Horizontal, title)
