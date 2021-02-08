from PyQt5 import QtWidgets

from nicos.clients.gui.cmdlets import all_categories, all_cmdlets
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAction, QMenu, QToolButton, pyqtSlot, \
    QTableWidgetItem, QHeaderView, QComboBox, QSizePolicy, Qt
from nicos.utils import importString, findResource


class LokiScriptBuilderPanel(Panel):
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui'))

        self.window = parent
        combo_options = ["TRANS First", "SANS First", "Simultaneous"]
        self.comboOrder.addItems(combo_options)

        self.chkShowTColumn.stateChanged.connect(self.chkShowTColumn_toggled)

        self.columns = ["Sample", "Trans", "Sans", "Test", "Temperature"]
        self._init_table()

    def _init_table(self, num_rows=10):
        self.tableScript.setColumnCount(len(self.columns))
        for i, column in enumerate(self.columns):
            self.tableScript.setHorizontalHeaderItem(i, QTableWidgetItem(column))

        # Hide optional columns? It would be nice to have them stored so
        # if the GUI is restarted it can recall what was hidden...
        self.tableScript.setColumnHidden(4, True)

        # Table formatting
        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableScript.resizeColumnsToContents()

        # TODO: set the number of rows to a number appropriate for the
        # current sample changer
        self.tableScript.setRowCount(num_rows)
        for i in range(num_rows):
            self.tableScript.setVerticalHeaderItem(i,
                QTableWidgetItem(chr(ord('A') + i)))

        combo = QComboBox()
        combo.addItems(["1", "2"])
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableScript.setCellWidget(0, 3, combo)


    @pyqtSlot()
    def on_testButton_clicked(self):
        for index in self.tableScript.selectionModel().selectedRows():
            row = index.row()
            self.tableScript.setItem(row, 2, QTableWidgetItem("45"))

    def chkShowTColumn_toggled(self, state):
        column_number = self.columns.index("Temperature")
        if state == Qt.Checked:
            self.tableScript.setColumnHidden(column_number, False)
        else:
            self.tableScript.setColumnHidden(column_number, True)

