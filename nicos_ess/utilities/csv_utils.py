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
import csv


def export_table_to_csv(data, filename, headers=None):
    """Export 2D data list to a text file.

    :param data: 2D data list
    :param filename: file to save as
    :param headers: List of column names.
    """
    with open(filename, "w") as file:
        writer = csv.writer(file)
        if headers:
            writer.writerow(headers)
        writer.writerows(data)


def import_table_from_csv(filename):
    """Import tabular data from a csv file.

    :param filename: path to csv file
    :return: tuple of headers (empty if no headers) and rows
    """
    with open(filename, "r") as file:
        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(file.read(2048))
        file.seek(0)
        rows = list(csv.reader(file))
        if has_header:
            return rows[0], rows[1:]
        return [], rows
