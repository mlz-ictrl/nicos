# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Ebad Kamil <ebad.kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""LoKI Script Model."""
import re

from nicos.core import ConfigurationError
from nicos.guisupport.qt import Qt
from nicos.guisupport.tablemodel import TableModel

from nicos_ess.loki.gui.table_delegates import LimitsDelegate, ReadOnlyDelegate

SAMPLE_INFO_INDEX = 1  # The column where the sample info is displayed


class LokiScriptModel(TableModel):

    def __init__(self, headings, columns, mappings=None, num_rows=25):
        TableModel.__init__(self, headings, mappings)
        self._default_num_rows = num_rows
        self._raw_data = [{} for _ in range(num_rows)]
        self._table_data = self._empty_table(len(headings), num_rows)
        self.samples = {}
        self._columns = columns

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and \
           orientation == Qt.Orientation.Horizontal:
            return self._headings[section]
        if role == Qt.ItemDataRole.DisplayRole and \
           orientation == Qt.Orientation.Vertical:
            return section + 1

    def setHeaderData(self, section, orientation, value,
                      role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and \
           orientation == Qt.Orientation.Horizontal:
            self._headings[section] = value
            self.headerDataChanged.emit(orientation, section, section)
        return True

    def clear(self):
        """Clears the data but keeps the rows."""
        self._raw_data = [{} for _ in self._raw_data]
        self._table_data = self._empty_table(len(self._headings),
                                             len(self._raw_data))
        self._emit_update()

    def setData(self, index, value, role):
        if role != Qt.ItemDataRole.EditRole:
            return False

        row, column = self._get_row_and_column(index)
        mapping = self._mappings.get(self._headings[column],
                                     self._headings[column])
        delegate = self._columns[mapping].delegate
        if isinstance(delegate, ReadOnlyDelegate):
            return False
        value = self._parse_value(delegate, str(value).strip())
        self._table_data[row][column] = value
        self._raw_data[row][mapping] = value
        self._update_sample_info(column, row, value)
        self._emit_update()
        return True

    def _parse_value(self, delegate, value):
        if isinstance(delegate, LimitsDelegate):
            try:
                value = float(value)
                if value < delegate.limits[0] or value > delegate.limits[1]:
                    return ''
            except ValueError:
                # If cast fails then return blank value
                return ''
        return value

    def _update_sample_info(self, column, row, value):
        if column == 0 and value in self.samples:
            mapping = self._mappings.get(self._headings[SAMPLE_INFO_INDEX],
                                         self._headings[SAMPLE_INFO_INDEX])
            as_str = re.sub(r'[{}]', '', str(self.samples[value]))
            self._table_data[row][SAMPLE_INFO_INDEX] = as_str
            self._raw_data[row][mapping] = self.samples[value]

    def update_all_samples(self, raise_error=True):
        invalid_positions = []
        for i, row in enumerate(self._raw_data):
            position = row.get('position', '')
            if not position:
                continue
            if position not in self.samples:
                invalid_positions.append(position)
                continue
            self._update_sample_info(0, i, position)
        if raise_error and invalid_positions:
            raise ConfigurationError('invalid position(s) defined '
                                     f'[{", ".join(invalid_positions)}]')
