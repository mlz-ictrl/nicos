#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************
import copy

from nicos.guisupport.qt import QAbstractTableModel, Qt, pyqtSignal


class TableModel(QAbstractTableModel):
    data_updated = pyqtSignal()

    def __init__(self, headings, mappings=None, transposed=False):
        """ Constructor.

        :param headings: the column headings.
        :param mappings: maps the headings to the keys in the underlying data.
        :param transposed: whether to display the data rotated (headings on the
                           left side).
        """
        super().__init__()
        self._transposed = transposed
        self._headings = headings
        self._mappings = mappings if mappings else {}
        # raw_data is the underlying NICOS data
        self._raw_data = []
        self._table_data = []

    @property
    def raw_data(self):
        """
        :return: list of dictionaries containing the underlying data.
        """
        return self._raw_data

    @raw_data.setter
    def raw_data(self, data):
        """
        Sets the underlying data for the table.

        If the keys in the data don't match the fields then they are ignored.

        :param data: list of dictionaries containing the data.
        """
        self._raw_data = data

        new_table = self._empty_table(len(self._headings),
                                      len(self._raw_data))

        for i, item in enumerate(self._raw_data):
            for j, heading in enumerate(self._headings):
                key = self._mappings.get(heading, heading)
                new_table[i][j] = str(item.get(key, ''))

        self._table_data = new_table
        self._emit_update()

    @property
    def table_data(self):
        return copy.copy(self._table_data)

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            row, column = self._get_row_and_column(index)
            return self._table_data[row][column]

    def setData(self, index, value, role):
        if role != Qt.EditRole:
            return False

        row, column = self._get_row_and_column(index)

        value = value.strip()
        self._table_data[row][column] = value
        col_name = self._headings[column]
        self._raw_data[row][self._mappings.get(col_name, col_name)] = value
        self._emit_update()
        return True

    def _emit_update(self):
        self.layoutChanged.emit()
        self.data_updated.emit()

    def _get_row_and_column(self, index):
        if self._transposed:
            return index.column(), index.row()
        return index.row(), index.column()

    def columnCount(self, index):
        return len(self._raw_data) if self._transposed else len(self._headings)

    def rowCount(self, index):
        return len(self._headings) if self._transposed else len(self._raw_data)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return section + 1 if self._transposed else self._headings[section]
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self._headings[section] if self._transposed else section + 1

    def _empty_table(self, columns, rows):
        return [[''] * columns for _ in range(rows)]

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

    @property
    def num_entries(self):
        return len(self._raw_data)
