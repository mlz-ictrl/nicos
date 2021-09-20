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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""Tests for various APIs in nicos.guisupport."""

import pytest

from nicos.guisupport.qt import QValidator
from nicos.guisupport.utils import DoubleValidator

idmap = {
    QValidator.Acceptable: 'Acceptable', QValidator.Intermediate: 'Intermediate',
    QValidator.Invalid: 'Invalid'
}


def idfn(val):
    if isinstance(val, (
        list,
        tuple,
    )):
        return idmap[val[0]] + '-' + (val[1] or 'inp')


inf = float('inf')


@pytest.mark.parametrize(
    'val, ll, ul, expected',
    [
        ('0', -inf, inf, (QValidator.Acceptable, None)),
        ('0.0', -inf, inf, (QValidator.Acceptable, None)),
        ('0.0e0', -inf, inf, (QValidator.Acceptable, None)),
        ('-0.0', -inf, inf, (QValidator.Acceptable, None)),
        ('1.23456789123456789e130', -inf, inf, (QValidator.Acceptable, None)),
        ('0', -1, 1, (QValidator.Acceptable, None)),
        ('0', 0, inf, (QValidator.Acceptable, None)),
        ('0', -inf, 0, (QValidator.Acceptable, None)),
        ('.1', -1, 1, (QValidator.Acceptable, '0.1')),
        ('-.1', -1, 1, (QValidator.Acceptable, '-0.1')),
        ('+.1', -1, 1, (QValidator.Acceptable, '+0.1')),
        ('.e9', 0, 10, (QValidator.Acceptable, '0.e9')),  # validator prepends 0!
        # intermediate
        ('4', 10, 50, (QValidator.Intermediate, None)),
        ('-4', -50, -10, (QValidator.Intermediate, None)),
        ('1.0e', -inf, inf, (QValidator.Intermediate, None)),
        ('0', 10, 20, (QValidator.Intermediate, None)),
        ('1.e9', 0, 10, (QValidator.Intermediate, '1.e9')),
        # invalid
        ('-15', 10, 20, (QValidator.Invalid, None)),
        ('-1', 10, 20, (QValidator.Invalid, None)),
        ('+15', -20, -10, (QValidator.Invalid, None)),
        ('+1', -20, -10, (QValidator.Invalid, None)),
        ('1,5', 0, 10, (QValidator.Invalid, None)),
    ],
    ids=idfn
)
def test_double_validator(val, ll, ul, expected):
    # valid cases
    validator = DoubleValidator()
    validator.setBottom(ll)
    validator.setTop(ul)
    valres = validator.validate(val, 0)
    assert valres[0] == expected[0]
    assert valres[1] == expected[1] or val
