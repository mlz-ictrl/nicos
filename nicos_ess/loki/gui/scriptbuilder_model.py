#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.qt import Qt
from nicos.guisupport.tablemodel import TableModel as BasicTableModel


class LokiScriptModel(BasicTableModel):
    def __init__(self, headings, mappings=None, num_rows=25):
        BasicTableModel.__init__(self, headings, mappings)
        self._default_num_rows = num_rows
        self._raw_data = [{} for _ in range(num_rows)]
        self._table_data = self._empty_table(len(headings), num_rows)

    @property
    def table_data(self):
        return copy.copy(self._table_data)

    def insert_row(self, position):
        self._raw_data.insert(position, {})
        self._table_data.insert(position, [''] * len(self._headings))
        self._emit_update()

    def remove_rows(self, row_indices):
        for index in sorted(row_indices, reverse=True):
            del self._raw_data[index]
            del self._table_data[index]
        self._emit_update()
        return True

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headings[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return section + 1

    def setHeaderData(self, section, orientation, value, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            self._headings[section] = value
            self.headerDataChanged.emit(orientation, section, section)
        return True

    def update_data_from_clipboard(self, copied_data, top_left_index,
                                   hidden_columns=None):
        hidden_columns = hidden_columns if hidden_columns else []
        visible_headings = [x for i, x in enumerate(self._headings)
                            if i not in hidden_columns]

        # Copied data is tabular so insert at top-left most position
        for row_index, row_data in enumerate(copied_data):
            col_index = 0
            current_row = top_left_index[0] + row_index
            if current_row >= len(self._table_data):
                self.insert_row(current_row)

            for value in row_data:
                if top_left_index[1] + col_index < len(visible_headings):
                    heading = visible_headings[top_left_index[1] + col_index]
                    col_index += 1
                    self._raw_data[current_row][
                        self._mappings.get(heading, heading)] = value
                    current_column = self._headings.index(heading)
                    self._table_data[current_row][current_column] = value
                else:
                    break
        self._emit_update()

    def select_table_data(self, selected_indices):
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
        return selected_data

    @property
    def num_rows(self):
        return len(self._raw_data)

    def clear(self):
        """Clears the data but keeps the rows."""
        self._raw_data = [{} for _ in self._raw_data]
        self._table_data = self._empty_table(len(self._headings),
                                             len(self._raw_data))
        self._emit_update()
