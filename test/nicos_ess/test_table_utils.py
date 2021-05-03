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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

from nicos_ess.utilities.table_utils import convert_table_to_clipboard_text, \
    extract_table_from_clipboard_text


class TestConvertAndExtractTable:
    def test_one_empty_cell(self):
        clipboard_data = ''
        table_data = [['']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_one_non_empty_cell(self):
        clipboard_data = 'A'
        table_data = [['A']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_empty_row(self):
        clipboard_data = '\t\t'
        table_data = [['', '', '']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_non_empty_row(self):
        clipboard_data = 'A\tB\tC'
        table_data = [['A', 'B', 'C']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_empty_column(self):
        clipboard_data = '\n'
        table_data = [[''],
                      ['']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_non_empty_column(self):
        clipboard_data = 'A\nB'
        table_data = [['A'],
                    ['B']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_multiple_empty_cells(self):
        clipboard_data = '\t\n\t'
        table_data = [['', ''],
                      ['', '']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_multiple_non_empty_cells(self):
        clipboard_data = 'A1\tB1\nA2\tB2'
        table_data = [['A1', 'B1'],
                      ['A2', 'B2']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_multiple_non_empty_cells_with_excel_encoding(self):
        # Excel uses \r\n as the line separator
        clipboard_data = 'A1\tB1\r\nA2\tB2'
        assert extract_table_from_clipboard_text(clipboard_data) \
               == [['A1', 'B1'],
                   ['A2', 'B2']]

    def test_mix_of_non_empty_cells_and_empty_cells(self):
        clipboard_data = '\tB1\nA2\t'
        table_data = [['', 'B1'],
                      ['A2', '']]
        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == clipboard_data

    def test_non_empty_cells_surrounded_by_empty_cells(self):
        clipboard_data = '\t\t\t\n\tB2\tC2\t\n\tB3\tC3\t\r\n\t\t\t'
        table_data = [['', '', '', ''],
                      ['', 'B2', 'C2', ''],
                      ['', 'B3', 'C3', ''],
                      ['', '', '', '']]

        assert extract_table_from_clipboard_text(clipboard_data) == table_data
        assert convert_table_to_clipboard_text(table_data) == \
            '\t\t\t\n\tB2\tC2\t\n\tB3\tC3\t\n\t\t\t'
