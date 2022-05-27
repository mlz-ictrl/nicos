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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

from unittest import mock

import pytest

from nicos.guisupport.qt import QTableView
from nicos.guisupport.tablemodel import TableModel

from nicos_ess.loki.gui.table_helper import Clipboard, TableHelper
from nicos_ess.utilities.table_utils import convert_table_to_clipboard_text

HEADERS = ['COLUMN_1', 'COLUMN_2', 'COLUMN_3']


class TestTableHelper:
    @pytest.fixture(autouse=True)
    def prepare(self):
        data = [
            {'COLUMN_1': '', 'COLUMN_2': '', 'COLUMN_3': ''},
            {'COLUMN_1': '', 'COLUMN_2': '', 'COLUMN_3': ''},
            {'COLUMN_1': '', 'COLUMN_2': '', 'COLUMN_3': ''},
        ]
        self.model = TableModel(HEADERS)
        self.model.raw_data = data
        self.table = mock.create_autospec(QTableView)
        self.clipboard = mock.create_autospec(Clipboard)
        self.table_helper = TableHelper(self.table, self.model, self.clipboard)

    def test_selected_items_copied_to_clipboard(self):
        data = [
            {'COLUMN_1': '11', 'COLUMN_2': '12', 'COLUMN_3': '13'},
            {'COLUMN_1': '21', 'COLUMN_2': '22', 'COLUMN_3': '23'},
            {'COLUMN_1': '31', 'COLUMN_2': '32', 'COLUMN_3': '33'},
        ]
        self.model.raw_data = data
        self.table_helper = TableHelper(self.table, self.model, self.clipboard)

        selected_indices = []
        for row, column in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            selected_indices.append(self.model.index(row, column))
        self.table.selectedIndexes.return_value = selected_indices

        self.table_helper.copy_selected_to_clipboard()

        self.clipboard.set_text.assert_called_once_with('11\t12\n21\t22')

    def test_selected_items_cut_to_clipboard(self):
        data = [
            {'COLUMN_1': '11', 'COLUMN_2': '12', 'COLUMN_3': '13'},
            {'COLUMN_1': '21', 'COLUMN_2': '22', 'COLUMN_3': '23'},
            {'COLUMN_1': '31', 'COLUMN_2': '32', 'COLUMN_3': '33'},
        ]
        self.model.raw_data = data
        self.table_helper = TableHelper(self.table, self.model, self.clipboard)

        selected_indices = []
        for row, column in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            selected_indices.append(self.model.index(row, column))
        self.table.selectedIndexes.return_value = selected_indices

        self.table_helper.cut_selected_to_clipboard()

        self.clipboard.set_text.assert_called_once_with('11\t12\n21\t22')
        assert self.model.table_data == [
            ['', '', '13'],
            ['', '', '23'],
            ['31', '32', '33'],
        ]

    def test_selected_items_cleared(self):
        data = [
            {'COLUMN_1': '11', 'COLUMN_2': '12', 'COLUMN_3': '13'},
            {'COLUMN_1': '21', 'COLUMN_2': '22', 'COLUMN_3': '23'},
            {'COLUMN_1': '31', 'COLUMN_2': '32', 'COLUMN_3': '33'},
        ]
        self.model.raw_data = data
        self.table_helper = TableHelper(self.table, self.model, self.clipboard)

        selected_indices = []
        for row, column in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            selected_indices.append(self.model.index(row, column))
        self.table.selectedIndexes.return_value = selected_indices

        self.table_helper.clear_selected()

        assert self.model.table_data == [
            ['', '', '13'],
            ['', '', '23'],
            ['31', '32', '33'],
        ]

    def test_clipboard_data_gets_pasted_at_index(self):
        self.table.selectedIndexes.return_value = [self.model.index(0, 0)]
        self.table.isColumnHidden.return_value = False
        self.clipboard.text.return_value = \
            convert_table_to_clipboard_text([['A', 'B'], ['C', 'D']])

        self.table_helper.paste_from_clipboard()

        assert self.model.table_data == [
            ['A', 'B', ''],
            ['C', 'D', ''],
            ['', '', ''],
        ]

    def test_clipboard_data_pasted_outside_the_columns_gets_ignored(self):
        self.table.selectedIndexes.return_value = \
            [self.model.index(0, len(HEADERS) - 1)]
        self.table.isColumnHidden.return_value = False
        self.clipboard.text.return_value = \
            convert_table_to_clipboard_text([['A', 'B'], ['C', 'D']])

        self.table_helper.paste_from_clipboard()

        assert self.model.table_data == [
            ['', '', 'A'],
            ['', '', 'C'],
            ['', '', ''],
        ]

    def test_clipboard_data_pasted_in_bottom_row_expands_the_table(self):
        self.table.selectedIndexes.return_value = [self.model.index(2, 0)]
        self.table.isColumnHidden.return_value = False
        self.clipboard.text.return_value = \
            convert_table_to_clipboard_text([['A', 'B'], ['C', 'D']])

        self.table_helper.paste_from_clipboard()

        assert self.model.table_data == [
            ['', '', ''],
            ['', '', ''],
            ['A', 'B', ''],
            ['C', 'D', ''],
        ]

    def test_clipboard_data_pasted_in_bottom_row_does_not_expand_the_table(self):
        self.table.selectedIndexes.return_value = [self.model.index(2, 0)]
        self.table.isColumnHidden.return_value = False
        self.clipboard.text.return_value = \
            convert_table_to_clipboard_text([['A', 'B'], ['C', 'D']])

        self.table_helper.paste_from_clipboard(expand=False)

        assert self.model.table_data == [
            ['', '', ''],
            ['', '', ''],
            ['A', 'B', ''],
        ]

    def test_hidden_column_skipped_when_pasting_clipboard_data(self):
        self.table.selectedIndexes.return_value = [self.model.index(0, 0)]
        self.table.isColumnHidden.side_effect = [False, True, False]
        self.clipboard.text.return_value = \
            convert_table_to_clipboard_text([['A', 'B'], ['C', 'D']])

        self.table_helper.paste_from_clipboard()

        assert self.model.table_data == [
            ['A', '', 'B'],
            ['C', '', 'D'],
            ['', '', ''],
        ]
