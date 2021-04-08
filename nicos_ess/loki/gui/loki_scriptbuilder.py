import os.path as osp
from functools import partial

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QApplication, QFileDialog, QHeaderView, \
    QKeySequence, QShortcut, Qt, QTableWidgetItem, pyqtSlot, QMenu
from nicos.utils import findResource
from nicos_ess.gui.utilities.load_save_tables import load_table_from_csv, \
    save_table_to_csv

TABLE_QSS = 'alternate-background-color: aliceblue;'


class LokiScriptBuilderPanel(Panel):
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui')
               )

        self.window = parent
        self.menus = None

        self.trans_options = ['TRANS First', 'SANS First', 'Simultaneous']

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

        self.columns_in_order = [name for name in self.permanent_columns.keys()]
        self.columns_in_order.extend(self.optional_columns.keys())
        self.last_save_location = None
        self._init_panel()

    def _init_panel(self, num_rows=25):
        # Create columns
        self.tableScript.setColumnCount(len(self.columns_in_order))
        for i, name in enumerate(self.columns_in_order):
            if name in self.permanent_columns:
                title = self.permanent_columns[name]
            else:
                title = self.optional_columns[name][0]
            self._set_column_title(i, title)

        # Link optional columns with corresponding check-boxes
        for name, details in self.optional_columns.items():
            _, checkbox = details
            checkbox.stateChanged.connect(
                partial(self._on_optional_column_toggled, name))
            self._hide_column(name)

        # Configure duration type combo-boxes
        self._link_duration_combobox_to_column('sans_duration',
                                               self.comboSansDurationType)
        self._link_duration_combobox_to_column('trans_duration',
                                               self.comboTransDurationType)

        # Set up trans order combo-box
        self.comboTransOrder.addItems(self.trans_options)

        # General table formatting
        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableScript.resizeColumnsToContents()
        self.tableScript.setAlternatingRowColors(True)
        self.tableScript.setStyleSheet(TABLE_QSS)

        self.tableScript.setRowCount(num_rows)

        # QShortcut(QKeySequence.Paste, self.tableScript).activated.connect(
        #     self._handle_table_paste)
        #
        # QShortcut(QKeySequence.Cut, self.tableScript).activated.connect(
        #     self._handle_cut_cells)
        #
        # QShortcut(QKeySequence.Delete, self.tableScript).activated.connect(
        #     self._handle_delete_cells)
        #
        # # TODO: this doesn't work on a Mac? How about Linux?
        # QShortcut(QKeySequence.Backspace, self.tableScript).activated.connect(
        #     self._handle_delete_cells)
        #
        # # TODO: Cannot do keyboard copy as it is ambiguous - investigate
        # QShortcut(QKeySequence.Copy, self.tableScript).activated.connect(
        #     self._handle_copy_cells)

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

        try:
            headers_from_file = load_table_from_csv(
                self.tableScript, self.columns_in_order, filename)

            for optional in set(headers_from_file).intersection(
                set(self.optional_columns.keys())):
                self.optional_columns[optional][1].setChecked(True)
        except Exception as ex:
            self.showError(f"Cannot read table contents from {filename}:\n{ex}")

    @pyqtSlot()
    def on_saveTableButton_clicked(self):
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
            save_table_to_csv(
                self.tableScript, filename, headers=self.columns_in_order)
        except Exception as ex:
            self.showError(f"Cannot write table contents to {filename}:\n{ex}")

    def _delete_rows(self):
        rows_to_remove = set()
        for index in self.tableScript.selectionModel().selectedIndexes():
            rows_to_remove.add(index.row())
        rows_to_remove = list(rows_to_remove)
        rows_to_remove.sort(reverse=True)
        for row_num in rows_to_remove:
            self.tableScript.removeRow(row_num)

    def _insert_row_above(self):
        lowest, _ = self._get_selected_rows_limits()
        if lowest is not None:
            self.tableScript.insertRow(lowest)

    def _insert_row_below(self):
        _, highest = self._get_selected_rows_limits()
        if highest is not None:
            self.tableScript.insertRow(highest + 1)

    def _get_selected_rows_limits(self):
        if self.tableScript.rowCount() == 0:
            return 0, -1

        lowest = None
        highest = None
        for index in self.tableScript.selectionModel().selectedIndexes():
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
        for index in self.tableScript.selectionModel().selectedIndexes():
            self._update_cell(index.row(), index.column(), '')

    def _handle_copy_cells(self):
        if len(self.tableScript.selectedRanges()) != 1:
            # Can only select one continuous region to copy
            return
        selected_data = self._extract_selected_data()
        QApplication.instance().clipboard().setText('\n'.join(selected_data))

    def _extract_selected_data(self):
        selected_data = []
        row_data = []
        curr_row = -1
        for index in self.tableScript.selectionModel().selectedIndexes():
            if self.tableScript.isColumnHidden(index.column()):
                # Don't copy hidden columns
                continue
            if curr_row != index.row():
                if row_data:
                    selected_data.append('\t'.join(row_data))
                    row_data.clear()
                curr_row = index.row()
            cell_text = self._get_cell_text(index.row(), index.column())
            row_data.append(cell_text)
        if row_data:
            selected_data.append('\t'.join(row_data))
            row_data.clear()
        return selected_data

    def _get_cell_text(self, row, column):
        cell = self.tableScript.item(row, column)
        if cell:
            return cell.text()
        return ''

    def _handle_table_paste(self):
        indices = []
        for index in self.tableScript.selectionModel().selectedIndexes():
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

        # Copied data is tabular so insert at top-left most position
        for row_index, row_data in enumerate(copied_table):
            col_index = 0
            for value in row_data:
                while top_left[1] + col_index < self.tableScript.columnCount():
                    current_column = top_left[1] + col_index
                    current_row = top_left[0] + row_index
                    col_index += 1
                    # Only paste into visible columns
                    if not self.tableScript.isColumnHidden(current_column):
                        self._update_cell(current_row, current_column, value)
                        self._select_cell(current_row, current_column)
                        break

    def _select_cell(self, row, column):
        item = self.tableScript.item(row, column)
        item.setSelected(True)

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
        for index in self.tableScript.selectionModel().selectedIndexes():
            if not self.tableScript.isColumnHidden(index.column()):
                self._update_cell(index.row(), index.column(), value)

    @pyqtSlot()
    def on_clearTableButton_clicked(self):
        for row in range(self.tableScript.rowCount()):
            for column in range(self.tableScript.columnCount()):
                self._update_cell(row, column, '')

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
        self.tableScript.setColumnHidden(column_number, True)

    def _show_column(self, column_name):
        column_number = self.columns_in_order.index(column_name)
        self.tableScript.setColumnHidden(column_number, False)

    def _on_duration_type_changed(self, column_name, value):
        column_number = self.columns_in_order.index(column_name)
        self._set_column_title(column_number,
            f'{self.permanent_columns[column_name]}\n({value})')

    def _set_column_title(self, index, title):
        self.tableScript.setHorizontalHeaderItem(index, QTableWidgetItem(title))

    def getMenus(self):
        menuEdit = QMenu('&Edit', self)
        menuEdit.addAction(self.actionCut)
        menuEdit.addAction(self.actionCopy)
        menuEdit.addAction(self.actionPaste)

        # if self.toolconfig:
        #     menuTools = QMenu('Editor t&ools', self)
        #     createToolMenu(self, self.toolconfig, menuTools)
        #     menus = [menuFile, menuView, menuEdit, menuScript, menuTools]
        # else:

        menus = [menuEdit]

        self.menus = menus
        return self.menus
