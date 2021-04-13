import os.path as osp
from collections import OrderedDict
from functools import partial
from itertools import groupby

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAbstractTableModel, QApplication, \
    QFileDialog, QHeaderView, QKeySequence, QModelIndex, QShortcut, Qt, \
    QTableWidgetItem, pyqtSlot
from nicos.utils import findResource

from nicos_ess.gui.utilities.load_save_tables import load_table_from_csv, \
    save_table_to_csv
from nicos_ess.loki.gui.script_generator import ScriptGenerator, TransOrder

TABLE_QSS = 'alternate-background-color: aliceblue;'


class LokiScriptModel(QAbstractTableModel):
    def __init__(self, header_data, num_rows=25):
        super().__init__()

        self._header_data = header_data
        self._num_rows = num_rows
        self._table_data = []
        for _ in range(num_rows):
            self.create_empty_row(0)

    @property
    def table_data(self):
        return self._table_data

    @table_data.setter
    def table_data(self, value):
        if isinstance(value, list) and all(
            [isinstance(val, list) and len(val) == len(self._header_data)
             for val in value]):
            # Extend the list with empty rows if value has less than n_rows
            if len(value) < self._num_rows:
                value.extend(self.empty_2d_list(
                        self._num_rows - len(value), len(self._header_data)))
            self._table_data = value
            self.layoutChanged.emit()
        else:
            raise AttributeError(
                f"Attribute must be a 2D list of shape (_, {len(self._header_data)})"
            )

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._table_data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._table_data[index.row()][index.column()] = value
            return True

    def rowCount(self, index):
        return len(self._table_data)

    def columnCount(self, index):
        return len(self._table_data[0])

    def create_empty_row(self, position):
        self._table_data.insert(position, [''] * len(self._header_data))

    def update_data_at_index(self, row, column, value):
        self._table_data[row][column] = value
        self.layoutChanged.emit()

    def insertRow(self, position, index=QModelIndex()):
        self.beginInsertRows(index, position, position)
        self.create_empty_row(position)
        self.endInsertRows()
        return True

    def removeRows(self, rows, index=QModelIndex()):
        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._table_data[row]
            self.endRemoveRows()
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._header_data[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return section + 1

    def setHeaderData(self, section, orientation, value, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            self._header_data[section] = value
            self.headerDataChanged.emit(orientation, section, section)
        return True

    def update_data_from_clipboard(
        self, copied_data, top_left_index, avoid=None):
        # Copied data is tabular so insert at top-left most position
        for row_index, row_data in enumerate(copied_data):
            col_index = 0
            for value in row_data:
                if top_left_index[1] + col_index < len(self._table_data[0]):
                    current_column = top_left_index[1] + col_index
                    current_row = top_left_index[0] + row_index
                    col_index += 1
                    if current_row >= len(self._table_data):
                        self.create_empty_row(current_row)

                    if avoid is not None and current_column in avoid:
                        continue
                    self._table_data[current_row][current_column] = value

        self.layoutChanged.emit()

    def select_data(self, selected_indices):
        curr_row = -1
        row_data = []
        selected_data = []
        for row, column in selected_indices:
            if row != curr_row:
                if row_data:
                    selected_data.append('\t'.join(row_data))
                    row_data.clear()
            curr_row = row
            row_data.append(self._table_data[row][column])

        if row_data:
            selected_data.append('\t'.join(row_data))
            row_data.clear()
        return selected_data

    def clear(self):
        self.table_data = self.empty_2d_list(
            len(self._table_data), len(self._header_data))

    @staticmethod
    def empty_2d_list(rows, columns):
        return [[""] * columns for _ in range(rows)]


class LokiScriptBuilderPanel(Panel):
    _available_trans_options = OrderedDict({
        "All TRANS First": TransOrder.TRANSFIRST,
        "All SANS First": TransOrder.SANSFIRST,
        "TRANS then SANS":TransOrder.TRANSTHENSANS,
        "SANS then TRANS": TransOrder.SANSTHENTRANS,
        "Simultaneous": TransOrder.SIMULTANEOUS
    })

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
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

        self.columns_in_order = [name for name in self.permanent_columns.keys()]
        self.columns_in_order.extend(self.optional_columns.keys())
        self.last_save_location = None
        self._init_table_panel()

    def _init_table_panel(self):
        headers = [
            self.permanent_columns[name]
            if name in self.permanent_columns else self.optional_columns[name][0]
            for name in self.columns_in_order]

        self.model = LokiScriptModel(headers)
        self.tableView.setModel(self.model)

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
        filename = QFileDialog.getOpenFileName(
            self,
            'Open table',
            osp.expanduser("~") if self.last_save_location is None \
                else self.last_save_location,
            'Table Files (*.txt *.csv)')[0]

        if not filename:
            return

        data = load_table_from_csv(filename)
        headers_from_file = data.pop(0)

        if not set(headers_from_file).issubset(set(self.columns_in_order)):
            self.showError(f"{filename} is not compatible with the table")
            return
        # Clear existing table before populating from file
        self.on_clearTableButton_clicked()
        self._fill_table(headers_from_file, data)

        for optional in set(headers_from_file).intersection(
            set(self.optional_columns.keys())):
            self.optional_columns[optional][1].setChecked(True)

    def _fill_table(self, headers, data):
        # corresponding indices of elements in headers_from_file list to headers
        indices = [i for i, e in enumerate(self.columns_in_order)
                   if e in headers]

        table_data = []
        for idx, row in enumerate(data):
            # create appropriate length list to fill the table row
            row = self._fill_elements(row, indices, len(self.columns_in_order))
            table_data.append(row)

        self.model.table_data = table_data

    def _fill_elements(self, row, indices, length):
        """Returns a list of len length, with elements of row placed at
        given indices.
        """
        if len(row) == length:
            return row
        r = [""] * length
        # Slicing similar to numpy arrays r[indices] = row
        for index, value in zip(indices, row):
            r[index] = value
        return r

    @pyqtSlot()
    def on_saveTableButton_clicked(self):
        if self.is_data_in_hidden_columns():
            self.showError("Cannot save because data in optional column(s)."
                           "Select the optional column or clear the column.")
            return

        filename = QFileDialog.getSaveFileName(
            self,
            'Save table',
            osp.expanduser("~") if self.last_save_location is None \
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
            save_table_to_csv(data, filename, headers)
        except Exception as ex:
            self.showError(f"Cannot write table contents to {filename}:\n{ex}")

    def is_data_in_hidden_columns(self):
        optional_indices = [i for i, e in enumerate(self.columns_in_order)
                            if e in self.optional_columns.keys()]
        # Transform table_data to allow easy access to columns like data[0]
        data = list(zip(*self.model.table_data))
        return any(
            [any(data[column])
             for column in optional_indices
             if self.tableView.isColumnHidden(column)])

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
        lowest, highest = self._get_selected_rows_limits()
        if lowest is not None:
            self.tableView.model().insertRow(lowest)

    def _insert_row_below(self):
        _, highest = self._get_selected_rows_limits()
        if highest is not None:
            self.tableView.model().insertRow(highest + 1)

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
            self.model.update_data_at_index(index.row(), index.column(), "")

    def _handle_copy_cells(self):
        indices = [(index.row(), index.column())
                   for index in self.tableView.selectedIndexes()]
        if len(set(
            [len(list(group))
             for _, group in groupby(indices, lambda x: x[0])])) != 1:
            # Can only select one continuous region to copy
            return

        selected_data = self._extract_selected_data()
        QApplication.instance().clipboard().setText('\n'.join(selected_data))

    def _extract_selected_data(self):
        selected_indices = []
        for index in self.tableView.selectedIndexes():
            if self.tableView.isColumnHidden(index.column()):
                # Don't select hidden columns
                continue
            selected_indices.append((index.row(), index.column()))

        selected_data = self.model.select_data(selected_indices)
        return selected_data

    def _handle_table_paste(self):
        indices = []
        for index in self.tableView.selectedIndexes():
            indices.append((index.row(), index.column()))
        top_left = indices[0]

        clipboard_text = QApplication.instance().clipboard().text()
        data_type = QApplication.instance().clipboard().mimeData()

        if not data_type.hasText():
            # Don't paste images etc.
            return

        copied_table = [[x for x in row.split('\t')]
                        for row in clipboard_text.splitlines()]
        if len(copied_table) == 1 and len(copied_table[0]) == 1:
            # Only one value, so put it in all selected cells
            self._do_bulk_update(copied_table[0][0])
            return
        hidden_columns = [idx for idx in range(len(self.columns_in_order))
                          if self.tableView.isColumnHidden(idx)]
        self.model.update_data_from_clipboard(
            copied_table, top_left, hidden_columns)

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
            # TODO: Handle hidden columns
            self.model.update_data_at_index(index.row(), index.column(), value)

    @pyqtSlot()
    def on_clearTableButton_clicked(self):
        self.model.clear()

    def _extract_labeled_data(self):
        labeled_data = []
        for row_data in self.model.table_data:
            labeled_row_data = dict(zip(self.columns_in_order, row_data))
            # Row will contribute to script only if all permanent columns
            # values are present
            if all(map(labeled_row_data.get, self.permanent_columns.keys())):
                labeled_data.append(labeled_row_data)
        return labeled_data

    @pyqtSlot()
    def on_generateScriptButton_clicked(self):
        labeled_data = self._extract_labeled_data()

        if self._available_trans_options[self.comboTransOrder.currentText()] ==\
            TransOrder.SIMULTANEOUS:
                if not all([data['sans_duration'] == data['trans_duration']
                            for data in labeled_data]):
                    self.showError(
                        "Different SANS and TRANS duration specified in "
                        "SIMULTANEOUS mode. SANS duration will be used in the script.")

        template = ScriptGenerator().generate_script(
            labeled_data,
            self._available_trans_options[self.comboTransOrder.currentText()],
            self.comboTransDurationType.currentText(),
            self.comboSansDurationType.currentText())

        self.mainwindow.codeGenerated.emit(template)

    def _update_cell(self, row, column, new_value):
        item = self.tableScript.item(row, column)
        if not item:
            self.tableScript.setItem(row, column, QTableWidgetItem(new_value))
        else:
            item.setText(new_value)

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
            f'{self.permanent_columns[column_name]}\n({value})')

    def _set_column_title(self, index, title):
        self.model.setHeaderData(index, Qt.Horizontal, title)
