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
#
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""LoKI Script Builder Panel."""
import os.path as osp
from collections import OrderedDict, namedtuple
from functools import partial

from nicos.clients.flowui.panels import get_icon
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAction, QCursor, QFileDialog, QHeaderView, \
    QKeySequence, QMenu, QShortcut, Qt, QTableView, QToolBar, pyqtSlot
from nicos.utils import findResource

from nicos_ess.gui.panels.panel import PanelBase
from nicos_ess.loki.gui.script_generator import ScriptFactory, TransOrder
from nicos_ess.loki.gui.scriptbuilder_model import LokiScriptModel
from nicos_ess.loki.gui.table_helper import Clipboard, TableHelper
from nicos_ess.utilities.csv_utils import export_table_to_csv, \
    import_table_from_csv

TABLE_QSS = 'alternate-background-color: aliceblue;'


Column = namedtuple('Column', ['header', 'optional', 'header_style'])


class LokiScriptBuilderPanel(PanelBase):
    _available_trans_options = OrderedDict({
        'All TRANS First': TransOrder.TRANSFIRST,
        'All SANS First': TransOrder.SANSFIRST,
        'TRANS then SANS': TransOrder.TRANSTHENSANS,
        'SANS then TRANS': TransOrder.SANSTHENTRANS,
        'Simultaneous': TransOrder.SIMULTANEOUS
    })

    def __init__(self, parent, client, options):
        PanelBase.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/scriptbuilder.ui')
               )

        self.window = parent
        self.duration_options = ['Mevents', 'seconds', 'frames']

        self.columns = OrderedDict({
            'position': Column('Position', False, QHeaderView.ResizeToContents),
            'sample': Column('Sample', False, QHeaderView.Stretch),
            'thickness': Column('Thickness\n(mm)', False,
                                QHeaderView.ResizeToContents),
            'trans_duration': Column('TRANS Duration', False,
                                     QHeaderView.ResizeToContents),
            'sans_duration': Column('SANS Duration', False,
                                    QHeaderView.ResizeToContents),
            'temperature': Column('Temperature', True,
                                  QHeaderView.ResizeToContents),
            'pre-command': Column('Pre-command', True,
                                  QHeaderView.ResizeToContents),
            'post-command': Column('Post-command', True,
                                   QHeaderView.ResizeToContents),
        })
        self.columns_headers = list(self.columns.keys())

        self.optional_columns_to_checkbox = {
            'temperature': self.chkShowTempColumn,
            'pre-command': self.chkShowPreCommand,
            'post-command': self.chkShowPostCommand
        }

        # Set up trans order combo-box
        self.comboTransOrder.addItems(self._available_trans_options.keys())

        self.last_save_location = None
        self._init_table_panel()
        self._create_actions()
        self._create_toolbar()
        self._init_right_click_context_menu()

    def _create_actions(self):
        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self._open_file)
        self.open_action.setIcon(get_icon('folder_open-24px.svg'))

        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self._save_table)
        self.save_action.setIcon(get_icon('save-24px.svg'))

        self.copy_action = QAction('Copy', self)
        self.copy_action.triggered.connect(
            self.table_helper.copy_selected_to_clipboard)
        self.copy_action.setIcon(get_icon('file_copy-24px.svg'))

        self.cut_action = QAction('Cut', self)
        self.cut_action.triggered.connect(
            self.table_helper.cut_selected_to_clipboard)
        self.cut_action.setIcon(get_icon('cut_24px.svg'))

        self.paste_action = QAction('Paste', self)
        self.paste_action.triggered.connect(
            self.table_helper.paste_from_clipboard)
        self.paste_action.setIcon(get_icon('paste_24px.svg'))

        self.add_row_above_action = QAction('Add Row Above', self)
        self.add_row_above_action.triggered.connect(self._insert_row_above)
        self.add_row_above_action.setIcon(get_icon('add_row_above-24px.svg'))

        self.add_row_below_action = QAction('Add Row Below', self)
        self.add_row_below_action.triggered.connect(self._insert_row_below)
        self.add_row_below_action.setIcon(get_icon('add_row_below-24px.svg'))

        self.delete_row_action = QAction('Delete Row(s)', self)
        self.delete_row_action.triggered.connect(self._delete_rows)
        self.delete_row_action.setIcon(get_icon('delete_row-24px.svg'))

        self.clear_action = QAction('Clear Table', self)
        self.clear_action.triggered.connect(self.model.clear)
        self.clear_action.setIcon(get_icon('delete-24px.svg'))

    def _create_toolbar(self):
        bar = QToolBar('Builder')
        bar.addAction(self.open_action)
        bar.addAction(self.save_action)
        bar.addSeparator()
        bar.addAction(self.copy_action)
        bar.addAction(self.cut_action)
        bar.addAction(self.paste_action)
        bar.addSeparator()
        bar.addAction(self.add_row_above_action)
        bar.addAction(self.add_row_below_action)
        bar.addAction(self.delete_row_action)
        bar.addAction(self.clear_action)
        self.verticalLayout.insertWidget(0, bar)

    def _init_table_panel(self):
        headers = [column.header for column in self.columns.values()]

        mappings = {v.header: k for k, v in self.columns.items()}
        for option in self.duration_options:
            mappings[f'TRANS Duration\n({option})'] = 'trans_duration'
            mappings[f'SANS Duration\n({option})'] = 'sans_duration'

        self.model = LokiScriptModel(headers, mappings)
        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QTableView.ContiguousSelection)
        self.table_helper = TableHelper(self.tableView, self.model, Clipboard())

        for name, checkbox in self.optional_columns_to_checkbox.items():
            checkbox.stateChanged.connect(
                partial(self._on_optional_column_toggled, name))
            self._hide_column(name)

        self._link_duration_combobox_to_column('sans_duration',
                                               self.comboSansDurationType)
        self._link_duration_combobox_to_column('trans_duration',
                                               self.comboTransDurationType)

        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        for i, column in enumerate(self.columns.values()):
            self.tableView.horizontalHeader().setSectionResizeMode(
                i, column.header_style)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setStyleSheet(TABLE_QSS)
        self._create_keyboard_shortcuts()

    def _init_right_click_context_menu(self):
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self._show_context_menu)

    def _show_context_menu(self):
        menu = QMenu()
        menu.addAction(self.copy_action)
        menu.addAction(self.cut_action)
        menu.addAction(self.paste_action)
        menu.addSeparator()
        menu.addAction(self.delete_row_action)
        menu.exec_(QCursor.pos())

    def _create_keyboard_shortcuts(self):
        for key, to_call in [
            (QKeySequence.Paste, self.table_helper.paste_from_clipboard),
            (QKeySequence.Cut, self.table_helper.cut_selected_to_clipboard),
            (QKeySequence.Copy, self.table_helper.copy_selected_to_clipboard),
            ('Ctrl+Backspace', self._delete_rows),
        ]:
            self._create_shortcut_key(key, to_call)

    def _create_shortcut_key(self, shortcut_keys, to_call):
        shortcut = QShortcut(shortcut_keys, self.tableView)
        shortcut.activated.connect(to_call)
        shortcut.setContext(Qt.WidgetShortcut)

    def _open_file(self):
        try:
            filename = QFileDialog.getOpenFileName(
                self,
                'Open table',
                osp.expanduser('~') if self.last_save_location is None
                else self.last_save_location,
                'Table Files (*.txt *.csv)')[0]

            if not filename:
                return

            headers_from_file, data = import_table_from_csv(filename)

            if not set(headers_from_file).issubset(set(self.columns_headers)):
                raise AttributeError('incorrect headers in file')
            # Clear existing table before populating from file
            self.model.clear()
            self._fill_table(headers_from_file, data)

            for name in headers_from_file:
                if name in self.columns and self.columns[name].optional:
                    self.optional_columns_to_checkbox[name].setChecked(True)
        except Exception as error:
            self.showError(f'Could not load selected file:  {error}')

    def _fill_table(self, headers, data):
        raw_data = []
        for row in data:
            raw_data.append(dict(zip(headers, row)))
        self.model.raw_data = raw_data

    def _save_table(self):
        if self.is_data_in_hidden_columns():
            self.showError('Cannot save because there is data in a non-visible '
                           'optional column(s).')
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
                            enumerate(self.columns.values())
                            if element.optional]
        # Transform table_data to allow easy access to columns like data[0]
        data = list(zip(*self.model.table_data))
        return any(
            (any(data[column])
             for column in optional_indices
             if self.tableView.isColumnHidden(column)))

    def _extract_headers_from_table(self):
        headers = [column for idx, column in enumerate(self.columns_headers)
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
        to_remove = {index.row()
                     for index in self.tableView.selectedIndexes()
                     if index.isValid() and
                     index.row() < self.model.num_entries}
        self.tableView.model().remove_rows(to_remove)

    def _insert_row_above(self):
        if self.model.num_entries == 0:
            self.tableView.model().insert_row(0)
            self.tableView.selectRow(0)
            return
        lowest, _ = self._get_selected_rows_limits()
        if lowest is not None:
            self.tableView.model().insert_row(lowest)
            self.tableView.selectRow(lowest + 1)

    def _insert_row_below(self):
        if self.model.num_entries == 0:
            self.tableView.model().insert_row(0)
            self.tableView.selectRow(0)
            return
        _, highest = self._get_selected_rows_limits()
        if highest is not None:
            self.tableView.model().insert_row(highest + 1)

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

    def _get_hidden_column_names(self):
        return [name for idx, name in enumerate(self.columns_headers)
                if self.tableView.isColumnHidden(idx)]

    def _link_duration_combobox_to_column(self, column_name, combobox):
        combobox.addItems(self.duration_options)
        combobox.currentTextChanged.connect(
            partial(self._on_duration_type_changed, column_name))
        self._on_duration_type_changed(column_name, combobox.currentText())

    @pyqtSlot()
    def on_bulkUpdateButton_clicked(self):
        for index in self.tableView.selectedIndexes():
            self.model.setData(index, self.txtValue.text(), Qt.EditRole)

    def _extract_script_data(self):
        hidden_column_names = self._get_hidden_column_names()
        # Row will contribute to script only if all permanent columns filled
        raw_data = [dict(x) for x in self.model.raw_data
                    if all(map(x.get, self.columns.keys()))]
        for row in raw_data:
            for key in hidden_column_names:
                if key in row:
                    del row[key]
        return raw_data

    @pyqtSlot()
    def on_generateScriptButton_clicked(self):
        if self.is_data_in_hidden_columns():
            self.showError('There is data in optional column(s) which will '
                           'not appear in the script')

        script_data = self._extract_script_data()

        if self._available_trans_options[self.comboTransOrder.currentText()]\
                == TransOrder.SIMULTANEOUS:
            if not all((row['sans_duration'] == row['trans_duration']
                        for row in script_data)):
                self.showError('Different SANS and TRANS duration specified '
                               'in SIMULTANEOUS mode. SANS duration will be '
                               'used in the script.'
                               )

        _trans_order = self._available_trans_options[
            self.comboTransOrder.currentText()]
        template = ScriptFactory.from_trans_order(_trans_order).\
            generate_script(script_data,
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
        column_number = self.columns_headers.index(column_name)
        self.tableView.setColumnHidden(column_number, True)

    def _show_column(self, column_name):
        column_number = self.columns_headers.index(column_name)
        self.tableView.setColumnHidden(column_number, False)

    def _on_duration_type_changed(self, column_name, value):
        column_number = self.columns_headers.index(column_name)
        self._set_column_title(column_number,
                               f'{self.columns[column_name].header}'
                               f'\n({value})')

    def _set_column_title(self, index, title):
        self.model.setHeaderData(index, Qt.Horizontal, title)
