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

from nicos_ess.loki.gui.scriptbuilder_model import LokiScriptModel

HEADERS = ['COLUMN_1', 'COLUMN_2', 'COLUMN_3']


def create_loki_script_model(num_rows=4, data=None):
    model = LokiScriptModel(HEADERS, num_rows=num_rows)
    if data is not None:
        model.raw_data = data
    return model


class TestScriptBuilderModel:
    def test_initialization_done_correctly(self):
        num_rows = 4
        model = create_loki_script_model(num_rows)

        # check dimensions of the data
        assert len(model.raw_data) == 4
        assert len(model.table_data) == num_rows
        assert all(len(data) == len(HEADERS) for data in model.table_data)

    def test_inserting_empty_row(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        position = 2
        model.insert_row(position)

        assert model.num_rows == 4
        assert model.table_data[position] == [''] * len(HEADERS)
        assert model.raw_data[position] == {}

    def test_removing_rows(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        positions = [0, 1]
        model.remove_rows(positions)

        assert model.num_rows == 1
        assert model.raw_data == [{'COLUMN_1': 21, 'COLUMN_2': 22,
                                   'COLUMN_3': 23}]
        assert model.table_data == [[21, 22, 23]]

    def test_data_selected_for_selected_indices(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        selected_indices = [(0, 0), (0, 1), (1, 0), (1, 1)]
        selected_data = model.select_table_data(selected_indices)

        assert selected_data == [[1, 2], [11, 12]]

    def test_clipboard_data_gets_pasted_in_empty_table_at_top_left(self):
        model = create_loki_script_model()
        clipboard_data = [['A', 'B'], ['C', 'D']]

        top_left = (0, 0)
        model.update_data_from_clipboard(clipboard_data, top_left)

        assert model.table_data == [
            ['A', 'B', ''],
            ['C', 'D', ''],
            ['', '', ''],
            ['', '', ''],
        ]
        assert model.raw_data == [{'COLUMN_1': 'A', 'COLUMN_2': 'B'},
                                  {'COLUMN_1': 'C', 'COLUMN_2': 'D'}, {}, {}]

    def test_clipboard_data_pasting_outside_the_columns_gets_ignored(self):
        model = create_loki_script_model()
        clipboard_data = [['A', 'B'], ['C', 'D']]

        top_right = (0, len(HEADERS) - 1)
        model.update_data_from_clipboard(clipboard_data, top_right)

        assert model.table_data == [
            ['', '', 'A'],
            ['', '', 'C'],
            ['', '', ''],
            ['', '', ''],
        ]
        assert model.raw_data == [{'COLUMN_3': 'A'}, {'COLUMN_3': 'C'}, {}, {}]

    def test_clipboard_data_pasting_in_bottom_row_expands_the_table(self):
        num_rows = 4
        model = create_loki_script_model(num_rows)

        clipboard_data = [['A', 'B'], ['C', 'D']]
        bottom_left = (num_rows - 1, 0)
        model.update_data_from_clipboard(clipboard_data, bottom_left)

        # Test if a new row was created
        assert len(model.table_data) == num_rows + len(clipboard_data) - 1
        assert model.table_data == [
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            ['A', 'B', ''],
            ['C', 'D', ''],
        ]
        assert model.raw_data == [{}, {}, {},
                                  {'COLUMN_1': 'A', 'COLUMN_2': 'B'},
                                  {'COLUMN_1': 'C', 'COLUMN_2': 'D'}]

    def test_clipboard_data_gets_pasted_at_index_in_table_with_data(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
            {'COLUMN_1': 31, 'COLUMN_2': 32, 'COLUMN_3': 33},
        ]
        model = create_loki_script_model(len(data), data)

        clipboard_data = [['A', 'B'], ['C', 'D']]
        index = (1, 0)
        model.update_data_from_clipboard(clipboard_data, index)

        assert model.table_data == [
            [1, 2, 3],
            ['A', 'B', 13],
            ['C', 'D', 23],
            [31, 32, 33],
        ]
        assert model.raw_data == [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 'A', 'COLUMN_2': 'B', 'COLUMN_3': 13},
            {'COLUMN_1': 'C', 'COLUMN_2': 'D', 'COLUMN_3': 23},
            {'COLUMN_1': 31, 'COLUMN_2': 32, 'COLUMN_3': 33},
        ]

    def test_hidden_column_skipped_when_pasting_clipboard_data(self):
        model = create_loki_script_model()
        hidden_column = 1
        top_left = (0, 0)
        clipboard_data = [['A', 'B'], ['C', 'D']]

        model.update_data_from_clipboard(
            clipboard_data, top_left, hidden_columns=[hidden_column]
        )

        assert model.table_data == [
            ['A', '', 'B'],
            ['C', '', 'D'],
            ['', '', ''],
            ['', '', ''],
        ]
        assert model.raw_data == [{'COLUMN_1': 'A', 'COLUMN_3': 'B'},
                                  {'COLUMN_1': 'C', 'COLUMN_3': 'D'}, {}, {}]

    def test_clearing(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        model.clear()

        assert model.num_rows == 3
        assert model.raw_data == [{}, {}, {}]
        assert model.table_data == [['', '', ''], ['', '', ''], ['', '', '']]
