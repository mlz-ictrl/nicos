#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

"""LoKI Script Model."""

import copy

from nicos.guisupport.qt import QAbstractTableModel, QModelIndex, Qt


class LokiScriptModel(QAbstractTableModel):
    def __init__(self, header_data, num_rows=25):
        QAbstractTableModel.__init__(self)

        self._header_data = header_data
        self._default_num_rows = num_rows
        self._table_data = self.empty_table(num_rows, len(header_data))

    @property
    def table_data(self):
        return copy.deepcopy(self._table_data)

    @table_data.setter
    def table_data(self, new_data):
        # Extend the list with empty rows if new data has less rows than the
        # default
        self._table_data = copy.deepcopy(new_data)
        if len(self._table_data) < self._default_num_rows:
            self._table_data.extend(self.empty_table(
                self._default_num_rows - len(self._table_data),
                len(self._header_data)))
        self.layoutChanged.emit()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._table_data[index.row()][index.column()]

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._table_data[index.row()][index.column()] = value
            return True

    def rowCount(self, index):
        return len(self._table_data)

    def columnCount(self, index):
        return len(self._header_data)

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

    def update_data_from_clipboard(self, copied_data, top_left_index,
                                   hidden_columns=None):
        # Copied data is tabular so insert at top-left most position
        for row_index, row_data in enumerate(copied_data):
            col_index = 0
            current_row = top_left_index[0] + row_index
            if current_row >= len(self._table_data):
                self.create_empty_row(current_row)

            index = 0
            while index < len(row_data):
                if top_left_index[1] + col_index < len(self._header_data):
                    current_column = top_left_index[1] + col_index
                    col_index += 1
                    if hidden_columns and current_column in hidden_columns:
                        continue
                    self._table_data[current_row][
                        current_column] = row_data[index]
                    index += 1
                else:
                    break

        self.layoutChanged.emit()

    def select_data(self, selected_indices):
        curr_row = -1
        row_data = []
        selected_data = []
        for row, column in selected_indices:
            if row != curr_row:
                if row_data:
                    selected_data.append(row_data)
                    row_data = []
            curr_row = row
            row_data.append(self._table_data[row][column])

        if row_data:
            selected_data.append(row_data)
            row_data = []
        return selected_data

    def clear(self):
        self.table_data = self.empty_table(
            len(self._table_data), len(self._header_data))

    def empty_table(self, rows, columns):
        return [[""] * columns for _ in range(rows)]

    @property
    def num_rows(self):
        return len(self._table_data)
