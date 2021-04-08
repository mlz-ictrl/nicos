from nicos.guisupport.qt import QAction, QActionGroup, QByteArray, QColor, \
    QDialog, QFileDialog, QFileSystemModel, QFileSystemWatcher, QFont, \
    QFontMetrics, QHBoxLayout, QHeaderView, QInputDialog, QMenu, QMessageBox, \
    QPen, QPrintDialog, QPrinter, QsciLexerPython, QsciPrinter, \
    QsciScintilla, Qt, QTabWidget, QToolBar, QTreeWidgetItem, QWidget, pyqtSlot, \
    QApplication, QShortcut, QKeySequence

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.utils import findResource


class TestPanel(Panel):
    panelName = 'test'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self,
               findResource('nicos_ess/loki/gui/ui_files/form.ui')
               )
        # self.layout().setMenuBar(self.createPanelToolbar())

        self.menus = None

        # ctrl_c = QShortcut(QKeySequence.Copy, self.tableWidget)
        # ctrl_c.activated.connect(self._handle_copy_cells)
        # ctrl_c.setContext(0)

    def _handle_copy_cells(self):
        print("Copy")

    def createPanelToolbar(self):
        bar = QToolBar('Editor')
        bar.addAction(self.actionCut)
        bar.addAction(self.actionCopy)
        bar.addAction(self.actionPaste)

        return bar

    @pyqtSlot()
    def on_actionCopy_triggered(self):
        print("copy from toolbar")
        if len(self.tableWidget.selectedRanges()) != 1:
            # Can only select one continuous region to copy
            return
        selected_data = self._extract_selected_data()
        QApplication.instance().clipboard().setText('\n'.join(selected_data))

    @pyqtSlot()
    def on_actionCut_triggered(self):
        print("cut from toolbar")
        # if len(self.tableWidget.selectedRanges()) != 1:
        #     # Can only select one continuous region to copy
        #     return
        # selected_data = self._extract_selected_data()
        # QApplication.instance().clipboard().setText('\n'.join(selected_data))

    @pyqtSlot()
    def on_actionPaste_triggered(self):
        print("paste from toolbar")

    def _extract_selected_data(self):
        selected_data = []
        row_data = []
        curr_row = -1
        for index in self.tableWidget.selectionModel().selectedIndexes():
            if self.tableWidget.isColumnHidden(index.column()):
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
        cell = self.tableWidget.item(row, column)
        if cell:
            return cell.text()
        return ''

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
