from PyQt5 import QtWidgets

from nicos.clients.gui.cmdlets import all_categories, all_cmdlets
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QAction, QMenu, QToolButton, pyqtSlot, \
    QTableWidgetItem, QHeaderView
from nicos.utils import importString, findResource


class LokiScriptBuilderPanel(Panel):
    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/loki_scriptbuilder.ui'))

        self.window = parent
        combo_options = ["TRANS First", "SANS First", "Simultaneous"]
        self.comboOrder.addItems(combo_options)

        self._init_table()

    def _init_table(self):
        self.tableScript.setColumnCount(4)

        # TODO: set the number of columns to a number appropriate for the
        # current sample changer
        self.tableScript.setRowCount(10)

        self.tableScript.horizontalHeader().setStretchLastSection(True)
        self.tableScript.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.tableScript.setHorizontalHeaderItem(0, QTableWidgetItem("Position"))
        self.tableScript.setHorizontalHeaderItem(1, QTableWidgetItem("Sample"))
        self.tableScript.setHorizontalHeaderItem(2, QTableWidgetItem("TRANS"))
        self.tableScript.setHorizontalHeaderItem(3, QTableWidgetItem("SANS"))
        self.tableScript.horizontalHeader().setStretchLastSection(True)

