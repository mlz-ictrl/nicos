from functools import partial

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import pyqtSlot, QTableWidgetItem, QHeaderView, \
    Qt
from nicos.utils import findResource


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

        self.chkShowTempColumn.stateChanged.connect(
            partial(self._optional_column_toggled, "Temperature"))
        self.chkShowPreCommand.stateChanged.connect(
            partial(self._optional_column_toggled, "Pre-command"))
        self.chkShowPostCommand.stateChanged.connect(
            partial(self._optional_column_toggled, "Post-command"))

        self.columns = ['Position', 'Sample', 'Thickness\n(mm)',
                        'TRANS\nDuration', 'SANS\nDuration', 'Temperature',
                        'Pre-command', 'Post-command']
        self._init_table()

    def _init_table(self, num_rows=25):
        self.tableScript.setColumnCount(len(self.columns))
        for i, column in enumerate(self.columns):
            self.tableScript.setHorizontalHeaderItem(i, QTableWidgetItem(column))

        # Hide optional columns? It would be nice to have them stored so
        # if the GUI is restarted it can recall what was hidden...
        self.tableScript.setColumnHidden(5, True)
        self.tableScript.setColumnHidden(6, True)
        self.tableScript.setColumnHidden(7, True)

        # Table formatting
        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableScript.resizeColumnsToContents()
        self.tableScript.setAlternatingRowColors(True)
        # TODO: move this to qss file?
        self.tableScript.setStyleSheet("alternate-background-color: aliceblue;")

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

    def _optional_column_toggled(self, column_name, state):
        column_number = self.columns.index(column_name)
        self._toggle_column_visibility(column_number, state)

    def _toggle_column_visibility(self, column_number, state):
        if state == Qt.Checked:
            self.tableScript.setColumnHidden(column_number, False)
        else:
            self.tableScript.setColumnHidden(column_number, True)


