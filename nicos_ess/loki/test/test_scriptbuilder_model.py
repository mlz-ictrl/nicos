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
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
from collections import OrderedDict
from copy import deepcopy

from nicos.guisupport.qt import QHeaderView, Qt

from nicos_ess.loki.gui.scriptbuilder import Column
from nicos_ess.loki.gui.scriptbuilder_model import LokiScriptModel
from nicos_ess.loki.gui.table_delegates import LimitsDelegate, ReadOnlyDelegate

HEADERS = ['position', 'sample', 'duration']
COLUMNS = OrderedDict({
    'position': Column('position', False, QHeaderView.ResizeMode.ResizeToContents, False,
                       None),
    'sample': Column('sample', False, QHeaderView.ResizeMode.ResizeToContents, False,
                     ReadOnlyDelegate()),
    'duration': Column('duration', False, QHeaderView.ResizeMode.ResizeToContents, False,
                       LimitsDelegate((0, 10), 1))})


def create_loki_script_model(num_rows=4, data=None):
    model = LokiScriptModel(HEADERS, COLUMNS, num_rows=num_rows)
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
            {'position': 'T1', 'sample': 2, 'duration': 3},
            {'position': 'T11', 'sample': 12, 'duration': 13},
            {'position': 'T21', 'sample': 22, 'duration': 23},
        ]
        model = create_loki_script_model(len(data), data)

        position = 2
        model.insert_row(position)

        assert model.num_entries == 4
        assert model.table_data[position] == [''] * len(HEADERS)
        assert model.raw_data[position] == {}

    def test_removing_rows(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
            {'position': 'T11', 'sample': 12, 'duration': 13},
            {'position': 'T21', 'sample': 22, 'duration': 23},
        ]
        model = create_loki_script_model(len(data), data)

        positions = {0, 1}
        model.remove_rows(positions)

        assert model.num_entries == 1
        assert model.raw_data == [{'position': 'T21', 'sample': 22,
                                   'duration': 23}]
        assert model.table_data == [['T21', '22', '23']]

    def test_clearing(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
            {'position': 'T11', 'sample': 12, 'duration': 13},
            {'position': 'T21', 'sample': 22, 'duration': 23},
        ]
        model = create_loki_script_model(len(data), data)

        model.clear()

        assert model.num_entries == 3
        assert model.raw_data == [{}, {}, {}]
        assert model.table_data == [['', '', ''], ['', '', ''], ['', '', '']]

    def test_cannot_set_readonly_column(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, 1), '999', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['sample'] == 2

    def test_setting_numeric_column_to_non_numeric_str_gives_blank(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, 2), 'hello', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['duration'] == ''  # pylint: disable=compare-to-empty-string

    def test_setting_numeric_column_to_numeric_str(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, 2), '5', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['duration'] == 5

    def test_setting_numeric_column_to_too_low_numeric_str_gives_blank(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, 2), '-1', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['duration'] == ''  # pylint: disable=compare-to-empty-string

    def test_setting_numeric_column_to_too_high_numeric_str_gives_blank(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, 2), '12345', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['duration'] == ''  # pylint: disable=compare-to-empty-string

    def test_setting_position_updates_sample_info(self):
        data = [
            {'position': 'T1', 'sample': 2, 'duration': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))
        model.samples = {
            'T1': {'name': 'sample 1'},
            'T11': {'name': 'sample 2'},
            'T21': {'name': 'sample 3'},
        }

        model.setData(model.index(0, 0), 'T21', Qt.ItemDataRole.EditRole)

        assert model.raw_data[0]['sample'] == {'name': 'sample 3'}
