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
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui'))

        self.window = parent

        trans_options = ['TRANS First', 'SANS First', 'Simultaneous']
        self.comboOrder.addItems(trans_options)

        duration_options = ['Mevents', 'seconds', 'frames']
        self.comboDurationType.addItems(duration_options)

        self.columns = ['Position', 'Sample', 'Thickness\n(mm)',
                        'TRANS\nDuration', 'SANS\nDuration', 'Temperature',
                        'Pre-command', 'Post-command']

        self.optional_columns = {
            "temperature": ("Temperature", self.chkShowTempColumn),
            "pre-command": ("Pre-command", self.chkShowPreCommand),
            "post-command": ("Post-command", self.chkShowPostCommand)
        }

        self._init_table()

    def _init_table(self, num_rows=25):
        self.tableScript.setColumnCount(len(self.columns))
        for i, column in enumerate(self.columns):
            self.tableScript.setHorizontalHeaderItem(i, QTableWidgetItem(column))

        # Configure optional columns.
        for _, item in self.optional_columns.items():
            title, checkbox = item
            checkbox.stateChanged.connect(
                partial(self._on_optional_column_toggled, title))
            self._hide_column(title)

        # Table formatting
        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableScript.resizeColumnsToContents()
        self.tableScript.setAlternatingRowColors(True)
        self.tableScript.setStyleSheet(TABLE_QSS)

        self.tableScript.setRowCount(num_rows)

    @pyqtSlot()
    def on_bulkUpdateButton_clicked(self):
        for index in self.tableScript.selectionModel().selectedIndexes():
            self._update_cell(index.row(), index.column(), self.txtValue.text())

    @pyqtSlot()
    def on_clearTableButton_clicked(self):
        # TODO: ask for confirmation
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
        column_number = self.columns.index(column_name)
        self.tableScript.setColumnHidden(column_number, True)

    def _show_column(self, column_name):
        column_number = self.columns.index(column_name)
        self.tableScript.setColumnHidden(column_number, False)
