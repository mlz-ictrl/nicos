#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from __future__ import print_function

from nicos.guisupport.qt import QValidator

from nicos.guisupport.utils import DoubleValidator


def test_double_validator():
    inf = float('inf')
    # valid cases
    validator = DoubleValidator()
    for args in [
            ('0', -inf, inf),
            ('0.0', -inf, inf),
            ('0.0e0', -inf, inf),
            ('-0.0', -inf, inf),
            ('1.23456789123456789e130', -inf, inf),
            ('0', -1, 1),
            ('0', 0, inf),
            ('0', -inf, 0),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Acceptable
    # intermediate cases
    for args in [
            ('4', 10, 50),
            ('-4', -50, -10),
            ('1.0e', -inf, inf),
            ('0', 10, 20),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Intermediate
    # invalid cases
    for args in [
            ('-15', 10, 20),
            ('-1', 10, 20),
            ('+15', -20, -10),
            ('+1', -20, -10),
            ('1,5', 0, 10),
    ]:
        validator.setBottom(args[1])
        validator.setTop(args[2])
        assert validator.validate(args[0], 0)[0] == QValidator.Invalid
