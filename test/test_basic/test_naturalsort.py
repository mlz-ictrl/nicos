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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""Tests for natural sort."""
from nicos.utils import natural_sort


def test_integers():
    values = [1, 11, 2, 22, 3]
    assert natural_sort(values) == [1, 2, 3, 11, 22]


def test_floats():
    values = [1.0, 3.14, 2.1, 2.000001]
    assert natural_sort(values) == [1.0, 2.000001, 2.1, 3.14]


def test_string_integers():
    values = ['1', '11', '2', '22', '3']
    assert natural_sort(values) == ['1', '2', '3', '11', '22']


def test_string_floats():
    values = ['1.0', '3.14', '2.1', '2.000001']
    assert natural_sort(values) == ['1.0', '2.000001', '2.1', '3.14']


def test_char_then_integers():
    values = ['A1', 'A11', 'A2', 'A22', 'A3']
    assert natural_sort(values) == ['A1', 'A2', 'A3', 'A11', 'A22']


def test_different_chars_then_integers():
    values = ['A1', 'B11', 'A2', 'B22', 'A3', 'B1', 'A11', 'B2', 'A22', 'B3',
              'AA0', 'BB1']
    assert natural_sort(values) == ['A1', 'A2', 'A3', 'A11', 'A22', 'AA0', 'B1',
                                    'B2', 'B3', 'B11', 'B22', 'BB1']


def test_version_numbers():
    values = ['1.0.0', '3.14.0', '2.1.3', '2.000001.5', '2.1.6']
    assert natural_sort(values) == ['1.0.0', '2.000001.5', '2.1.3',
                                    '2.1.6', '3.14.0']


def test_strings():
    values = ['banana', 'xylophone', 'apple', 'zoo']
    assert natural_sort(values) == ['apple', 'banana', 'xylophone', 'zoo']
