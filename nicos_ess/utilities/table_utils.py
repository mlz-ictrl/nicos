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
import re


def extract_table_from_clipboard_text(text):
    """
    Extracts 2-D tabular data from clipboard text.

    When sent to the clipboard, tabular data from Excel, etc. is represented as
    a text string with tabs for columns and newlines for rows.

    :param text: The clipboard text
    :return: tabular data
    """
    # Uses re.split because "A\n" represents two vertical cells one
    # containing "A" and one being empty.
    # str.splitlines will lose the empty cell but re.split won't
    return [row.split('\t') for row in re.split('\r?\n', text)]


def convert_table_to_clipboard_text(table_data):
    """
    Converts 2-D tabular data to clipboard text.

    :param table_data: 2D tabular data
    :return: clipboard text
    """
    return '\n'.join(['\t'.join(row) for row in table_data])
