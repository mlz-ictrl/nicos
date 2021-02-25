from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import pyqtSlot, QTableWidgetItem, QHeaderView, \
    QComboBox, QSizePolicy, Qt
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

        self.chkShowTempColumn.stateChanged.connect(self.chkShowTempColumn_toggled)

        self.columns = ['Sample', 'Thickness\n(mm)', 'TRANS\nDuration', 'SANS\nDuration', 'Test', 'Temperature']
        self._init_table()

    def _init_table(self, num_rows=26):
        self.tableScript.setColumnCount(len(self.columns))
        for i, column in enumerate(self.columns):
            self.tableScript.setHorizontalHeaderItem(i, QTableWidgetItem(column))

        # Hide optional columns? It would be nice to have them stored so
        # if the GUI is restarted it can recall what was hidden...
        self.tableScript.setColumnHidden(5, True)

        # Table formatting
        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableScript.resizeColumnsToContents()
        self.tableScript.setAlternatingRowColors(True)
        # TODO: move this to qss?
        self.tableScript.setStyleSheet("alternate-background-color: aliceblue;")

        # TODO: set the number of rows to a number appropriate for the
        # current sample changer
        self.tableScript.setRowCount(num_rows)
        for i in range(num_rows):
            self.tableScript.setVerticalHeaderItem(i,
                QTableWidgetItem(chr(ord('A') + i)))

        combo = QComboBox()
        combo.addItems(['1', '2'])
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableScript.setCellWidget(0, 3, combo)

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

    def chkShowTempColumn_toggled(self, state):
        # SMELL: need to avoid this breaking if the column name is changed
        column_number = self.columns.index('Temperature')
        if state == Qt.Checked:
            self.tableScript.setColumnHidden(column_number, False)
        else:
            self.tableScript.setColumnHidden(column_number, True)


