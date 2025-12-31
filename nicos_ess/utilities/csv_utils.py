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
import csv


def export_table_to_csv_file(filename, data, headers=None):
    """Export 2D data to a csv text file.

    :param filename: file to save as
    :param data: 2D data list
    :param headers: list of column names
    """
    with open(filename, 'w', encoding='utf-8') as file:
        export_table_to_csv_stream(file, data, headers)


def export_table_to_csv_stream(stream, data, headers=None):
    """Export 2D data to a csv stream.

    Typically, used with an open file-like object where any preceding non-csv
    data has already been written.

    :param stream: the open stream
    :param data: 2D data list
    :param headers: list of column names
    """
    writer = csv.writer(stream)
    if headers:
        writer.writerow(headers)
    writer.writerows(data)


def import_table_from_csv_file(filename):
    """Import tabular data from a csv file.

    :param filename: path to csv file
    :return: tuple of headers (empty if no headers) and rows
    """
    with open(filename, 'r', encoding='utf-8') as file:
        return import_table_from_csv_stream(file)


def import_table_from_csv_stream(stream):
    """Import tabular data from a csv containing stream.

    Typically, used from an open file-like object where any preceding non-csv
    data has already been consumed.

    :param stream: the open stream
    :return: tuple of headers (empty if no headers) and rows
    """
    offset = stream.tell()
    sniffer = csv.Sniffer()
    has_header = sniffer.has_header(stream.read(2048))
    stream.seek(offset)
    rows = list(csv.reader(stream))
    if has_header:
        return rows[0], rows[1:]
    return [], rows
