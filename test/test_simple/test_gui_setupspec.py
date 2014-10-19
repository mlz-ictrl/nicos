#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Tests for the setupSpec tests used to selectively show GUI elements
in dependence of loaded_setups.
"""

from __future__ import print_function

from nicos.clients.gui.utils import checkSetupSpec

# setupspec : loaded_setups : result
CASES = [
    (None,         None,            True),
    (None,         ['a', 'b', 'c'], True),
    ('a',          ['a', 'b', 'c'], True),
    (['a'],        ['a', 'b', 'c'], True),
    ('!a',         ['a', 'b', 'c'], False),
    (['!a'],       ['a', 'b', 'c'], False),
    (['a', 'd'],   ['a', 'b', 'c'], True),
    (['d'],        ['a', 'b', 'c'], False),
    (['!d'],       ['a', 'b', 'c'], True),
    (['a', '!d'],  ['a', 'b', 'c'], True),
    (['!a', 'd'],  ['a', 'b', 'c'], False),
    (['!a', '!d'], ['a', 'b', 'c'], True),
]


def test_checkSetupSpec():
    for spec, setups, result in CASES:
        # print is here to aid in finding the offending input parameters
        # as the stacktrace doesn't output locals
        res = checkSetupSpec(spec, setups)
        print('testing checkSetupSpec(%r, %r) == %r: %r' %
              (spec, setups, result, res), end=' ')
        assert res == result
