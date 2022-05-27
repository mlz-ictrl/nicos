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
from copy import deepcopy

from nicos.guisupport.qt import Qt

from nicos_ess.loki.gui.scriptbuilder_model import SAMPLE_INFO_INDEX, \
    LokiScriptModel

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

        assert model.num_entries == 4
        assert model.table_data[position] == [''] * len(HEADERS)
        assert model.raw_data[position] == {}

    def test_removing_rows(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        positions = {0, 1}
        model.remove_rows(positions)

        assert model.num_entries == 1
        assert model.raw_data == [{'COLUMN_1': 21, 'COLUMN_2': 22,
                                   'COLUMN_3': 23}]
        assert model.table_data == [['21', '22', '23']]

    def test_clearing(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
            {'COLUMN_1': 11, 'COLUMN_2': 12, 'COLUMN_3': 13},
            {'COLUMN_1': 21, 'COLUMN_2': 22, 'COLUMN_3': 23},
        ]
        model = create_loki_script_model(len(data), data)

        model.clear()

        assert model.num_entries == 3
        assert model.raw_data == [{}, {}, {}]
        assert model.table_data == [['', '', ''], ['', '', ''], ['', '', '']]

    def test_cannot_set_sample_info_directly(self):
        data = [
            {'COLUMN_1': 1, 'COLUMN_2': 2, 'COLUMN_3': 3},
        ]
        model = create_loki_script_model(len(data), deepcopy(data))

        model.setData(model.index(0, SAMPLE_INFO_INDEX), '999', Qt.EditRole)

        assert model.raw_data[0] == data[0]
