#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""LoKI Experiment Configuration dialog."""
from functools import partial

from nicos.clients.flowui.panels import get_icon
from nicos.clients.gui.utils import loadUi
from nicos.core import ConfigurationError
from nicos.guisupport.qt import QAction, QCursor, QHeaderView, QItemDelegate, \
    QKeySequence, QMenu, QShortcut, Qt, QTableView, QTableWidgetItem, \
    pyqtSlot
from nicos.utils import findResource

from nicos_ess.gui.panels.panel import PanelBase
from nicos_ess.loki.gui.samples_model import SamplesTableModel
from nicos_ess.loki.gui.table_delegates import LimitsDelegate, ReadOnlyDelegate
from nicos_ess.loki.gui.table_helper import Clipboard, TableHelper


class LokiSampleHolderPanel(PanelBase):
    panelName = 'LoKI sample holder setup'

    def __init__(self, parent, client, options):
        PanelBase.__init__(self, parent, client, options)
        self.parent = parent
        self.options = options
        self._in_edit_mode = False
        self._dev_name = None
        self._dev_name_old = None
        loadUi(
            self,
            findResource(
                'nicos_ess/loki/gui/ui_files/sample_holder_config.ui'))
        self.cartridge_tables = [
            self.tableTopFirst, self.tableTopSecond, self.tableTopThird,
            self.tableBottomFirst, self.tableBottomSecond,
            self.tableBottomThird
        ]
        self.cartridge_combos = [
            self.comboTopFirst, self.comboTopSecond, self.comboTopThird,
            self.comboBottomFirst, self.comboBottomSecond,
            self.comboBottomThird
        ]
        self.calculate_buttons = [
            self.calculateTopFirstButton, self.calculateTopSecondButton,
            self.calculateTopThirdButton, self.calculateBottomFirstButton,
            self.calculateBottomSecondButton, self.calculateBottomThirdButton
        ]
        self.cell_spacings = {}
        self.number_cells = {}
        self.cartridges = {}
        self.x_delegate = LimitsDelegate()
        self.y_delegate = LimitsDelegate()
        self.labelWarning.setStyleSheet('color: red')
        self.labelWarning.setVisible(False)
        self._configure_combos()
        self._configure_tables()
        self._configure_sample_table()
        self._connect_up_widgets()
        self.initialise_connection_status_listeners()
        self.tabWidget.setStyleSheet('QTabWidget::tab-bar {left: 0px;} '
                                     'QTabWidget::pane {'
                                     'border: 1px solid darkgray; '
                                     'border-radius: 5px}')

    def initialise_connection_status_listeners(self):
        PanelBase.initialise_connection_status_listeners(self)
        self.client.setup.connect(self.on_client_setup)

    def on_client_connected(self):
        self._find_device()
        if self.number_cells:
            self._set_table_height(max(self.number_cells.values()))
        self.setViewOnly(self.client.viewonly)

    def on_client_disconnected(self):
        if not self._in_edit_mode:
            self._clear_data()

    def on_client_setup(self, data):
        self._find_device()

    def _find_device(self):
        devices = self.client.getDeviceList(
            'nicos_ess.loki.devices.thermostated_cellholder.'
            'ThermoStatedCellHolder')
        # Should only be one
        self._dev_name = devices[0] if devices else None
        self.editButton.setEnabled(self._dev_name is not None)
        self.saveButton.setEnabled(self._dev_name is not None)
        self.labelWarning.setVisible(self._dev_name is None)
        if not self._dev_name:
            self._in_edit_mode = False
            self._clear_data()
        self._register_listeners()
        self._read_mode()

    def _register_listeners(self):
        # Only register once unless the device name changes.
        if self._dev_name and self._dev_name != self._dev_name_old:
            self._dev_name_old = self._dev_name
            self.client.register(self, f'{self._dev_name}/cartridges')
            self.client.register(self, f'{self._dev_name}/number_cells')
            self.client.register(self, f'{self._dev_name}/cell_spacings')
            self.client.register(self, f'{self._dev_name}/mapping')
            self.client.register(self, 'sample/samples')
            self.client.on_connected_event()

    def on_keyChange(self, key, value, time, expired):
        if self._dev_name and key.startswith(self._dev_name):
            if key.endswith('/number_cells'):
                self.number_cells = value
                self._update_cartridges()
            if key.endswith('/cartridges'):
                self.cartridges = value
                self._update_cartridges()
            if key.endswith('/cell_spacings'):
                self.cell_spacings = value
            if key.endswith('/mapping'):
                self._update_samples()
        elif key == 'sample/samples':
            self._update_samples()

    def _update_samples(self):
        if self._in_edit_mode or not self._dev_name:
            return
        mapping = self.client.eval(f'{self._dev_name}.mapping', {})
        self.positions = list(mapping.keys())
        self.samples_model.set_positions(self.positions)
        samples = self.client.eval('session.experiment.get_samples()', {})
        self.samples_model.set_samples(samples)

    def setViewOnly(self, viewonly):
        for combo in self.cartridge_combos:
            combo.setEnabled(not viewonly)
        for table in self.cartridge_tables:
            table.setEnabled(not viewonly)
        for button in self.calculate_buttons:
            button.setEnabled(not viewonly)
        self.set_samples_viewonly(viewonly)
        self.cancelButton.setEnabled(not viewonly)
        if viewonly:
            self.saveButton.setEnabled(False)
            self.editButton.setEnabled(False)
        else:
            self.saveButton.setEnabled(self._dev_name is not None)
            self.editButton.setEnabled(self._dev_name is not None)
        if self._in_edit_mode and not viewonly:
            self._edit_mode()
        elif not viewonly:
            self._update_cartridges()
            self._update_samples()
            self._read_mode()

    def set_samples_viewonly(self, viewonly):
        if viewonly:
            self.sampleTable.setItemDelegate(ReadOnlyDelegate())
            self.sampleTable.setStyleSheet(
                'QTableView {background: gainsboro;}')
        else:
            self.sampleTable.setItemDelegate(QItemDelegate())
            self.sampleTable.setStyleSheet('QTableView {background: white;}')

    def _read_mode(self):
        for combo in self.cartridge_combos:
            combo.setEnabled(False)
        for table in self.cartridge_tables:
            table.setEnabled(False)
        for button in self.calculate_buttons:
            button.setEnabled(False)
        self.set_samples_viewonly(True)
        self.editButton.setVisible(True)
        self.cancelButton.setVisible(False)
        self.saveButton.setVisible(False)

    def _edit_mode(self):
        self.x_delegate.limits = self.client.eval(f'{self._dev_name}.xlimits',
                                                  (0, 0))
        self.y_delegate.limits = self.client.eval(f'{self._dev_name}.ylimits',
                                                  (0, 0))
        for combo in self.cartridge_combos:
            combo.setEnabled(True)
        for table in self.cartridge_tables:
            table.setEnabled(True)
        for button in self.calculate_buttons:
            button.setEnabled(True)
        self.set_enabled_controls()
        self.set_samples_viewonly(False)
        self.editButton.setVisible(False)
        self.cancelButton.setVisible(True)
        self.saveButton.setVisible(True)

    def _configure_combos(self):
        for combo in self.cartridge_combos:
            combo.addItems(['blank', 'narrow', 'wide'])
            combo.setCurrentIndex(-1)
        self.comboTopFirst.addItems(['rotation'])
        self.comboBottomFirst.addItems(['rotation'])

    def _configure_sample_table(self):
        columns = {
            'Name': 'name',
            'Formula': 'formula',
            'Concentration': 'concentration',
            'Thickness': 'thickness',
            'Notes': 'notes'
        }
        self.samples_model = SamplesTableModel(columns)
        self.sampleTable.setModel(self.samples_model)
        self.table_helper = TableHelper(self.sampleTable, self.samples_model,
                                        Clipboard())
        self.positions = []

        self.sampleTable.setSelectionMode(QTableView.ContiguousSelection)
        self.sampleTable.horizontalHeader().setStretchLastSection(True)
        self.sampleTable.verticalHeader().setSectionResizeMode(
            QHeaderView.Fixed)
        self._create_keyboard_shortcuts()
        self._init_right_click_context_menu()

    def _configure_tables(self):
        # Not connected yet, so use an aesthetically pleasing number of rows.
        self._set_table_height(8)

    def _set_table_height(self, num_rows):
        row_height = self.tableTopFirst.verticalHeader().defaultSectionSize()
        for table in self.cartridge_tables:
            table.setItemDelegateForColumn(0, self.x_delegate)
            table.setItemDelegateForColumn(1, self.y_delegate)
            # +1 for header
            table.setMinimumHeight(row_height * (num_rows + 1))

    def _connect_up_widgets(self):
        for combo, table, button in zip(self.cartridge_combos,
                                        self.cartridge_tables,
                                        self.calculate_buttons):
            combo.currentTextChanged.connect(
                partial(self.on_cartridge_changed, table, button))
            button.clicked.connect(
                partial(self.on_calculate_clicked, combo, table))

    def _update_cartridges(self):
        if self._in_edit_mode or not self._dev_name:
            return
        if self.cartridges and self.number_cells:
            for settings, table, combo in zip(self.cartridges,
                                              self.cartridge_tables,
                                              self.cartridge_combos):
                combo.setCurrentText(settings.get('type', 'blank'))
                for i, (x, y) in enumerate(settings.get('positions', [])):
                    table.setItem(i, 0, QTableWidgetItem(f'{x}'))
                    table.setItem(i, 1, QTableWidgetItem(f'{y}'))

    def _clear_data(self):
        for combo in self.cartridge_combos:
            combo.setCurrentText('blank')
        for table in self.cartridge_tables:
            table.clearContents()
        self.samples_model.clear()

    def on_cartridge_changed(self, table, button, value):
        if not value:
            return
        table.setRowCount(self.number_cells.get(value, 0))
        self._update_position_headers()
        if self._in_edit_mode:
            self.set_enabled_controls()
        button.setEnabled(value != 'blank')

    def on_calculate_clicked(self, combo, table):
        table.setFocus(False)
        if not table.item(0, 0) or not table.item(0, 1):
            self.showError('Please enter x and y values for the first cell.')
            return
        x = float(table.item(0, 0).text())
        y = float(table.item(0, 1).text())
        num_cells = self.number_cells[combo.currentText()]
        self._check_x_valid(x * num_cells)
        self._check_y_range(y)

        for i in range(1, num_cells):
            x += self.cell_spacings[combo.currentText()]
            table.setItem(i, 0, QTableWidgetItem(f'{x}'))
            table.setItem(i, 1, QTableWidgetItem(f'{y}'))

    def _check_y_range(self, y):
        self._check_in_range(y, self.y_delegate.limits, 'y')

    def _check_x_valid(self, x):
        self._check_in_range(x, self.x_delegate.limits, 'x')

    def set_enabled_controls(self):
        is_rotation = False
        for i, (combo, table, button) in enumerate(
                zip(self.cartridge_combos, self.cartridge_tables,
                    self.calculate_buttons)):
            if i % 3 == 0:
                current_text = combo.currentText()
                is_rotation = current_text == 'rotation'
            else:
                current_text = 'blank' if is_rotation else combo.currentText()
                combo.setCurrentText(current_text)
                combo.setEnabled(not is_rotation)
            table.setEnabled(current_text != 'blank')
            button.setEnabled(current_text != 'blank')
            if current_text == 'blank':
                table.clearContents()

    def _update_position_headers(self):
        self.positions.clear()
        count = 0
        for i, table in enumerate(self.cartridge_tables):
            prefix = 'T' if i < 3 else 'B'
            if i == 3:
                count = 0
            positions = []
            for _ in range(table.rowCount()):
                count += 1
                positions.append(f'{prefix}{count}')
            table.setVerticalHeaderLabels(positions)
            self.positions.extend(positions)
        self.samples_model.set_positions(self.positions)

    @pyqtSlot()
    def on_saveButton_clicked(self):
        self.saveButton.setFocus(True)
        if not self._dev_name:
            return
        if self.mainwindow.current_status != 'idle':
            self.showError('Could not set values as a command/script is in '
                           'progress.')
            return
        try:
            # Extract all data before sending to avoid samples and holders
            # getting out of sync if there are validation errors.
            samples = self.samples_model.extract_samples()
            cartridges = self._extract_cartridges()
            self._write_cartridges(cartridges)
            self._write_samples(samples)
        except ConfigurationError as error:
            self.showError(str(error))
            return

        self._in_edit_mode = False
        self._read_mode()

    def _write_samples(self, samples):
        self.client.run(f'Exp.sample.set_samples({dict(samples)})')

    def _extract_cartridges(self):
        all_positions = set()
        cartridges = []
        i = 0
        for combo, table in zip(self.cartridge_combos, self.cartridge_tables):
            data = {'type': combo.currentText(), 'positions': [], 'labels': []}
            for r in range(table.rowCount()):
                if not table.item(r, 0) or not table.item(r, 0).text() \
                        or not table.item(r, 1) or not table.item(r, 1).text():
                    raise ConfigurationError(
                        'All cell-holder positions must be specified. '
                        f'{self.positions[i]} is not specified.')
                x = float(table.item(r, 0).text())
                y = float(table.item(r, 1).text())
                self._check_x_valid(x)
                self._check_y_range(y)
                if (x, y) in all_positions:
                    raise ConfigurationError('Duplicate cell-holder positions '
                                             'are not allowed. Position '
                                             f'{(x, y)} found multiple times.')
                all_positions.add((x, y))
                data['positions'].append((x, y))
                data['labels'].append(self.positions[i])
                i += 1
            cartridges.append(data)
        return cartridges

    def _write_cartridges(self, cartridges):
        self.client.run(f'{self._dev_name}.cartridges = {cartridges}')

    def _check_in_range(self, value, limits, axis):
        if value < limits[0] or value > limits[1]:
            raise ConfigurationError(
                f'All {axis} values must be in range {limits}')

    @pyqtSlot()
    def on_editButton_clicked(self):
        self._in_edit_mode = True
        self._edit_mode()

    @pyqtSlot()
    def on_cancelButton_clicked(self):
        self.cancelButton.setFocus(True)
        self._in_edit_mode = False
        self._update_cartridges()
        self._update_samples()
        self._read_mode()

    def _init_right_click_context_menu(self):
        self.sampleTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sampleTable.customContextMenuRequested.connect(
            self._show_context_menu)

    def _show_context_menu(self):
        menu = QMenu()

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(
            self.table_helper.copy_selected_to_clipboard)
        copy_action.setIcon(get_icon("file_copy-24px.svg"))
        menu.addAction(copy_action)

        cut_action = QAction("Cut", self)
        cut_action.triggered.connect(self._on_cut)
        cut_action.setIcon(get_icon("cut_24px.svg"))
        menu.addAction(cut_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self._on_paste)
        paste_action.setIcon(get_icon("paste_24px.svg"))
        menu.addAction(paste_action)

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._on_clear)
        clear_action.setIcon(get_icon("remove-24px.svg"))
        menu.addAction(clear_action)

        menu.exec(QCursor.pos())

    def _create_keyboard_shortcuts(self):
        for key, to_call in [
            (QKeySequence.Paste, self._on_paste),
            (QKeySequence.Cut, self._on_cut),
            (QKeySequence.Copy, self.table_helper.copy_selected_to_clipboard),
            ("Ctrl+Backspace", self._on_clear),
        ]:
            self._create_shortcut_key(key, to_call)

    def _create_shortcut_key(self, shortcut_keys, to_call):
        shortcut = QShortcut(shortcut_keys, self.sampleTable)
        shortcut.activated.connect(to_call)
        shortcut.setContext(Qt.WidgetShortcut)

    def _on_paste(self):
        if self._in_edit_mode:
            self.table_helper.paste_from_clipboard(expand=False)

    def _on_cut(self):
        if self._in_edit_mode:
            self.table_helper.cut_selected_to_clipboard()

    def _on_clear(self):
        if self._in_edit_mode:
            self.table_helper.clear_selected()
