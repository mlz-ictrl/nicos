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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS commands tests."""

from __future__ import print_function

import numpy

from nicos.core import UsageError
from nicos.commands.utility import RangeListByStep, RangeListByCount, \
    RangeListLog, floatrange, RangeListGeneral

from test.utils import raises, approx


def test_rangelistbystep():
    # start/stop/step
    l1 = RangeListByStep(1, 2, 0.5)
    assert len(l1) == 3
    assert l1[0] == 1.
    assert l1[-1] == 2.
    assert (l1 == [1., 1.5, 2.]).all()

    l1 = RangeListByStep(1, 2, 0.7)
    assert len(l1) == 3
    assert l1[0] == 1.
    assert l1[-1] == 2.
    assert (l1 == [1., 1.7, 2.]).all()

    # start/stop/step
    l1 = RangeListByStep(-1, -2, -0.5)
    assert len(l1) == 3
    assert l1[0] == -1.
    assert l1[-1] == -2.
    assert (l1 == [-1., -1.5, -2.]).all()

    # start/stop
    l2 = RangeListByStep(1, 3)
    assert len(l2) == 3
    assert l2[0] == 1.
    assert l2[-1] == 3.

    # start/stop
    l2 = RangeListByStep(3, 1)
    assert len(l2) == 3
    assert l2[0] == 3.
    assert l2[-1] == 1.

    # stop
    l2 = RangeListByStep(3)
    assert len(l2) == 4
    assert l2[0] == 0.
    assert l2[-1] == 3.

    assert raises(UsageError, RangeListByStep, 1, 2, -0.5)
    assert raises(UsageError, RangeListByStep, 1, 2, 0)


def test_rangelistbycounts():
    # start/stop/num
    l2 = RangeListByCount(1, 2, 3)
    assert len(l2) == 3
    assert l2[0] == 1.
    assert l2[-1] == 2.

    # start/stop
    l2a = RangeListByCount(3, 7)
    assert len(l2a) == 2
    assert l2a[0] == 3.
    assert l2a[-1] == 7.

    # stop
    l2a = RangeListByCount(3)
    assert len(l2a) == 2
    assert l2a[0] == 0.
    assert l2a[-1] == 3.


def test_floatrange():
    # pylint: disable=unidiomatic-typecheck

    l4 = floatrange(1, 2, step=0.5)
    assert len(l4) == 3
    assert l4[0] == 1.
    assert l4[-1] == 2.
    assert type(l4[0]) == numpy.float64
    assert type(l4[-1]) == numpy.float64

    l4 = floatrange(1, 2, num=5)
    assert len(l4) == 5
    assert l4[0] == 1.
    assert l4[-1] == 2.
    assert type(l4[0]) == numpy.float64
    assert type(l4[-1]) == numpy.float64

    assert raises(UsageError, floatrange, 1, 2, step=-0.5)
    assert raises(UsageError, floatrange, 1, 2, step=0.5, num=2)
    assert raises(UsageError, floatrange, 1, 2)
    assert raises(UsageError, floatrange, 1, 2, num=1)


def test_rangelistlog():
    l3 = RangeListLog(1., 2., 3)
    print(l3)
    assert len(l3) == 3
    assert l3[0] == 1.
    assert l3[-1] == 2.
    assert numpy.allclose(l3, [1.0, 1.4142135623730949, 2.0])

    l3a = RangeListLog(0.1, 200., 3)
    assert len(l3a) == 3
    assert l3a[0] == approx(0.1, abs=1e-5)
    assert l3a[-1] == approx(200., abs=1e-5)
    assert numpy.allclose(l3a, [0.10000000000000001, 4.4721359549995787, 200.0])

    l3b = RangeListLog(200, 2., 5)
    assert len(l3b) == 5
    assert l3b[0] == approx(200., abs=1e-5)
    assert l3b[-1] == approx(2., abs=1e-5)

    assert raises(UsageError, RangeListLog, -1, 2, 10)


def test_rangelistgeneral():
    l1 = RangeListGeneral(1, 2, 5)
    assert len(l1) == 5
    l2 = RangeListGeneral(1, 2, 10, lambda x: 1/x)
    assert len(l2) == 10
    assert numpy.allclose(l2, [1.0, 1.05882352941, 1.125, 1.2,
                               1.28571428571, 1.38461538462, 1.5,
                               1.63636363636, 1.8, 2.0])
    assert raises(RuntimeError, RangeListGeneral, 0, 2, 10, lambda x: 1/x)
