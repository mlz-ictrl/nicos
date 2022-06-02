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

    def clear(self):
        """Clears the data but keeps the rows."""
        self._raw_data = [{} for _ in self._raw_data]
        self._table_data = self._empty_table(len(self._headings),
                                             len(self._raw_data))
        self._emit_update()
