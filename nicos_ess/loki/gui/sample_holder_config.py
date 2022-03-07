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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""LoKI Experiment Configuration dialog."""
from functools import partial

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAbstractSpinBox, QDoubleSpinBox, \
    QItemDelegate, QTableWidgetItem, pyqtSlot
from nicos.utils import findResource

from nicos_ess.gui.panels.panel import PanelBase


def add_spinbox_limits(spinbox, minimum, maximum, precision):
    spinbox.setMinimum(minimum)
    spinbox.setMaximum(maximum)
    spinbox.setDecimals(precision)


class TableDelegate(QItemDelegate):
    def __init__(self, x_limits=(0, 0), y_limits=(0, 0), x_precision=3,
                 y_precision=3):
        QItemDelegate.__init__(self)
        self.x_limits = x_limits
        self.y_limits = y_limits
        self.x_precision = x_precision
        self.y_precision = y_precision

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        if index.column() == 0:
            minimum, maximum = self.x_limits
            precision = self.x_precision
        else:
            minimum, maximum = self.y_limits
            precision = self.y_precision
        add_spinbox_limits(editor, minimum, maximum, precision)
        return editor


class LokiSampleHolderPanel(PanelBase):
    panelName = 'LoKI sample holder setup'

    def __init__(self, parent, client, options):
        PanelBase.__init__(self, parent, client, options)
        self.parent = parent
        self.options = options
        self._in_edit_mode = False
        self._dev_name = None
        self._dev_name_old = None
        loadUi(self, findResource(
            'nicos_ess/loki/gui/ui_files/sample_holder_config.ui'))
        self.cartridge_tables = [self.tableTopFirst, self.tableTopSecond,
                                 self.tableTopThird, self.tableBottomFirst,
                                 self.tableBottomSecond, self.tableBottomThird]
        self.cartridge_combos = [self.comboTopFirst, self.comboTopSecond,
                                 self.comboTopThird, self.comboBottomFirst,
                                 self.comboBottomSecond, self.comboBottomThird]
        self.calculate_buttons = [self.calculateTopFirstButton,
                                  self.calculateTopSecondButton,
                                  self.calculateTopThirdButton,
                                  self.calculateBottomFirstButton,
                                  self.calculateBottomSecondButton,
                                  self.calculateBottomThirdButton]
        self.cell_spacings = {}
        self.number_cells = {}
        self.cartridges = {}
        self.delegate = TableDelegate()
        self.labelWarning.setStyleSheet('color: red')
        self.labelWarning.setVisible(False)
        self._configure_combos()
        self._configure_tables()
        self._connect_up_widgets()
        self.initialise_connection_status_listeners()

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
        self._populate_data()
        self._read_mode()

    def _register_listeners(self):
        # Only register once unless the device name changes.
        if self._dev_name and self._dev_name != self._dev_name_old:
            self._dev_name_old = self._dev_name
            self.client.register(self, f'{self._dev_name}/cartridges')
            self.client.register(self, f'{self._dev_name}/number_cells')
            self.client.register(self, f'{self._dev_name}/cell_spacings')
            self.client.on_connected_event()

    def on_keyChange(self, key, value, time, expired):
        if self._dev_name and key.startswith(self._dev_name):
            if key.endswith('/number_cells'):
                self.number_cells = value
            if key.endswith('/cartridges'):
                self.cartridges = value
            if key.endswith('/cell_spacings'):
                self.cell_spacings = value
                return
            self._populate_data()

    def setViewOnly(self, viewonly):
        for combo in self.cartridge_combos:
            combo.setEnabled(not viewonly)
        for table in self.cartridge_tables:
            table.setEnabled(not viewonly)
        for button in self.calculate_buttons:
            button.setEnabled(not viewonly)
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
            self._populate_data()
            self._read_mode()

    def _read_mode(self):
        for combo in self.cartridge_combos:
            combo.setEnabled(False)
        for table in self.cartridge_tables:
            table.setEnabled(False)
        for button in self.calculate_buttons:
            button.setEnabled(False)

        self.editButton.setVisible(True)
        self.cancelButton.setVisible(False)
        self.saveButton.setVisible(False)

    def _edit_mode(self):
        self.delegate.x_limits = self.client.eval(f'{self._dev_name}.xlimits',
                                                  (0, 0))
        self.delegate.y_limits = self.client.eval(f'{self._dev_name}.ylimits',
                                                  (0, 0))
        labels = [str(x + 1) for x in range(max(self.number_cells.values()))]
        for combo in self.cartridge_combos:
            combo.setEnabled(True)
        for table in self.cartridge_tables:
            table.setEnabled(True)
            table.setVerticalHeaderLabels(labels)
        for button in self.calculate_buttons:
            button.setEnabled(True)
        self.set_enabled_controls()

        self.editButton.setVisible(False)
        self.cancelButton.setVisible(True)
        self.saveButton.setVisible(True)

    def _configure_combos(self):
        for combo in self.cartridge_combos:
            combo.addItems(['blank', 'narrow', 'wide'])
            combo.setCurrentIndex(-1)
        self.comboTopFirst.addItems(['rotation'])
        self.comboBottomFirst.addItems(['rotation'])

    def _configure_tables(self):
        # Not connected yet, so use an aesthetically pleasing number of rows.
        self._set_table_height(8)

    def _set_table_height(self, num_rows):
        row_height = self.tableTopFirst.verticalHeader().defaultSectionSize()
        for table in self.cartridge_tables:
            table.setItemDelegate(self.delegate)
            # +1 for header
            table.setMinimumHeight(row_height * (num_rows + 1))

    def _connect_up_widgets(self):
        for combo, table, button in zip(self.cartridge_combos,
                                        self.cartridge_tables,
                                        self.calculate_buttons):
            combo.currentTextChanged.connect(partial(self.on_cartridge_changed,
                                                     table, button))
            button.clicked.connect(partial(self.on_calculate_clicked,
                                           combo, table, button))

    def _populate_data(self):
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
                table.setVerticalHeaderLabels(settings.get('labels', []))

    def _clear_data(self):
        for combo in self.cartridge_combos:
            combo.setCurrentText('blank')
        for table in self.cartridge_tables:
            table.clearContents()

    def on_cartridge_changed(self, table, button, value):
        if not value:
            return
        table.setRowCount(self.number_cells.get(value, 0))
        if self._in_edit_mode:
            self.set_enabled_controls()
        button.setEnabled(value != 'blank')

    def on_calculate_clicked(self, combo, table, button):
        button.setFocus(True)
        if not table.item(0, 0) or not table.item(0, 1):
            self.showError('Please enter x and y values for the first cell.')
            return
        x = float(table.item(0, 0).text())
        y = float(table.item(0, 1).text())
        num_cells = self.number_cells[combo.currentText()]
        if not self._check_x_valid(x * num_cells) or not self._check_y_range(y):
            return

        for i in range(1, num_cells):
            x += self.cell_spacings[combo.currentText()]
            table.setItem(i, 0, QTableWidgetItem(f'{x}'))
            table.setItem(i, 1, QTableWidgetItem(f'{y}'))

    def _check_y_range(self, y):
        return self._check_in_range(y, self.delegate.y_limits, 'y')

    def _check_x_valid(self, x):
        return self._check_in_range(x, self.delegate.x_limits, 'x')

    def set_enabled_controls(self):
        is_rotation = False
        for i, (combo, table, button) in enumerate(zip(self.cartridge_combos,
                                                       self.cartridge_tables,
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

    @pyqtSlot()
    def on_saveButton_clicked(self):
        self.saveButton.setFocus(True)
        if not self._dev_name:
            return
        all_positions = set()
        settings = []
        count = 1
        for i, (combo, table) in enumerate(zip(self.cartridge_combos,
                                               self.cartridge_tables)):
            data = {
                'type': combo.currentText(),
                'positions': [],
                'labels': []
            }
            prefix = 'T' if i < 3 else 'B'
            if i == 3:
                count = 1
            for r in range(table.rowCount()):
                x = float(table.item(r, 0).text()) if table.item(r, 0) else 0
                y = float(table.item(r, 1).text()) if table.item(r, 1) else 0
                if not self._check_x_valid(x) or not self._check_y_range(y):
                    return
                if (x, y) in all_positions:
                    self.showError(f'Could not set values as non-unique '
                                   f'position {(x, y)} found.')
                    return
                all_positions.add((x, y))
                data['positions'].append((x, y))
                data['labels'].append(f'{prefix}{count}')
                count += 1
            settings.append(data)

        if self.client.run(f'{self._dev_name}.cartridges = {settings}',
                           noqueue=True) is None:
            self.showError('Could not set values as a command/script is in '
                           'progress.')
            return
        self._in_edit_mode = False
        self._read_mode()

    def _check_in_range(self, value, limits, axis):
        if value < limits[0] or value > limits[1]:
            self.showError(f'All {axis} values must be in range {limits}')
            return False
        return True

    @pyqtSlot()
    def on_editButton_clicked(self):
        self._in_edit_mode = True
        self._edit_mode()

    @pyqtSlot()
    def on_cancelButton_clicked(self):
        self.cancelButton.setFocus(True)
        self._in_edit_mode = False
        self._populate_data()
        self._read_mode()
