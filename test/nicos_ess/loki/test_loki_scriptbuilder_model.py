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

from nicos_ess.loki.gui.loki_scriptbuilder_model import LokiScriptModel

HEADERS = ['COLUMN_1', 'COLUMN_2', 'COLUMN_3']


def create_loki_script_model(num_rows=4, data=None):
    model = LokiScriptModel(HEADERS, num_rows)
    if data is not None:
        model.table_data = data
    return model


class TestScriptBuilderModel:
    def test_initialization_done_correctly(self):
        num_rows = 4
        model = create_loki_script_model(num_rows)
        # check if initialized with empty data
        assert not any(data for data in sum(model.table_data, []))
        # check dimensions of the table_data
        assert len(model.table_data) == num_rows
        assert all(len(data) == len(HEADERS) for data in model.table_data)

    def test_inserting_empty_row(self):
        data = [
            ['00', '01', '02'],
            ['10', '11', '12'],
            ['20', '21', '22'],
            ['30', '31', '32'],
        ]
        # Create model with data
        model = create_loki_script_model(len(data), data)

        position = 2
        model.insertRow(position)

        assert len(model.table_data) == len(data) + 1
        assert model.table_data[position - 1] == data[position - 1]
        assert model.table_data[position] == [''] * len(HEADERS)
        assert model.table_data[position + 1] == data[position]

    def test_removing_rows(self):
        data = [
            ['00', '01', '02'],
            ['10', '11', '12'],
            ['20', '21', '22'],
            ['30', '31', '32'],
        ]
        # Create model with data
        model = create_loki_script_model(len(data), data)

        positions = [0, 1]
        model.removeRows(positions)

        assert len(model.table_data) == len(data) - len(positions)
        assert model.table_data == data[2:]

    def test_data_selected_for_selected_indices(self):
        data = [
            ['00', '01', '02'],
            ['10', '11', '12'],
            ['20', '21', '22'],
            ['30', '31', '32'],
        ]
        model = create_loki_script_model(len(data), data)

        selected_indices = [(0, 0), (0, 1), (1, 0), (1, 1)]
        selected_data = model.select_data(selected_indices)

        assert selected_data == [['00', '01'], ['10', '11']]

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

    def test_clipboard_data_gets_pasted_at_index_in_table_with_data(self):
        data = [
            ['00', '01', '02'],
            ['10', '11', '12'],
            ['20', '21', '22'],
            ['30', '31', '32'],
        ]
        # Create model with data
        model = create_loki_script_model(len(data), data)
        clipboard_data = [['A', 'B'], ['C', 'D']]
        index = (1, 0)

        model.update_data_from_clipboard(clipboard_data, index)

        assert model.table_data == [
            ['00', '01', '02'],
            ['A', 'B', '12'],
            ['C', 'D', '22'],
            ['30', '31', '32'],
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
