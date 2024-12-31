# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""Helpers for working with tables."""

from nicos.guisupport.qt import QApplication, Qt

from nicos_ess.utilities.table_utils import convert_table_to_clipboard_text, \
    extract_table_from_clipboard_text


class Clipboard:

    def __init__(self):
        self.clipboard = QApplication.instance().clipboard()

    def set_text(self, text):
        self.clipboard.setText(text)

    def has_text(self):
        return self.clipboard.mimeData().hasText()

    def text(self):
        return self.clipboard.text()


class TableHelper:

    def __init__(self, table_view, model, clipboard):
        self.table_view = table_view
        self.model = model
        self.clipboard = clipboard

    def _select_table_data(self):
        curr_row = -1
        row_data = []
        selected_data = []
        for index in self.table_view.selectedIndexes():
            row = index.row()
            column = index.column()
            if row != curr_row and row_data:
                selected_data.append(row_data)
                row_data = []
            curr_row = row
            row_data.append(str(self.model.table_data[row][column]))

        if row_data:
            selected_data.append(row_data)
        return selected_data

    def copy_selected_to_clipboard(self):
        selected_data = self._select_table_data()
        clipboard_text = convert_table_to_clipboard_text(selected_data)
        self.clipboard.set_text(clipboard_text)

    def clear_selected(self):
        for index in self.table_view.selectedIndexes():
            self.model.setData(index, '', Qt.ItemDataRole.EditRole)

    def cut_selected_to_clipboard(self):
        self.copy_selected_to_clipboard()
        self.clear_selected()

    def paste_from_clipboard(self, expand=True):
        if not self.clipboard.has_text() or \
                not self.table_view.selectedIndexes():
            return

        clipboard_text = self.clipboard.text()
        copied_table = extract_table_from_clipboard_text(clipboard_text)

        if len(copied_table) == 1 and len(copied_table[0]) == 1:
            # Only one value, so put it in all selected cells
            for index in self.table_view.selectedIndexes():
                self.model.setData(index, copied_table[0][0],
                                   Qt.ItemDataRole.EditRole)
            return

        # Copied data is tabular so insert at top-left most position
        top_left = self.table_view.selectedIndexes()[0]
        column_indexes = [
            i for i, _ in enumerate(self.model._headings) if
            not self.table_view.isColumnHidden(i) and i >= top_left.column()
        ]
        for row_index, row_data in enumerate(copied_table):
            current_row = top_left.row() + row_index
            if current_row == self.model.num_entries:
                if not expand:
                    break
                self.model.insert_row(current_row)

            for col_index, value in zip(column_indexes, row_data):
                self.model.setData(self.model.index(current_row, col_index),
                                   value, Qt.ItemDataRole.EditRole)
