from functools import partial

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import pyqtSlot, QTableWidgetItem, QHeaderView, \
    Qt
from nicos.utils import findResource

TABLE_QSS = "alternate-background-color: aliceblue;"


class LokiScriptBuilderPanel(Panel):
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui')
               )

        self.window = parent

        self.trans_options = ['TRANS First', 'SANS First', 'Simultaneous']

        self.duration_options = ['Mevents', 'seconds', 'frames']

        self.permanent_columns = {
            "position": "Position",
            "sample": "Sample",
            "thickness": "Thickness\n(mm)",
            "trans_duration": "TRANS Duration",
            "sans_duration": "SANS Duration"
        }

        self.optional_columns = {
            "temperature": ("Temperature", self.chkShowTempColumn),
            "pre-command": ("Pre-command", self.chkShowPreCommand),
            "post-command": ("Post-command", self.chkShowPostCommand)
        }

        self.columns_in_order = [name for name in self.permanent_columns.keys()]
        self.columns_in_order.extend(self.optional_columns.keys())

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
        self._link_duration_combobox_to_column("sans_duration",
                                               self.comboSansDurationType)
        self._link_duration_combobox_to_column("trans_duration",
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

    def _link_duration_combobox_to_column(self, column_name, combobox):
        combobox.addItems(self.duration_options)
        combobox.currentTextChanged.connect(
            partial(self._on_duration_type_changed, column_name))
        self._on_duration_type_changed(column_name,
                                       combobox.currentText())

    @pyqtSlot()
    def on_bulkUpdateButton_clicked(self):
        for index in self.tableScript.selectionModel().selectedIndexes():
            self._update_cell(index.row(), index.column(), self.txtValue.text())

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
