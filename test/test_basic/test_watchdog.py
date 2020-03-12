#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS tests for the watchdog condition primitives."""

from __future__ import absolute_import, division, print_function

from nicos.services.watchdog.conditions import DelayedTrigger, Expression, \
    Precondition


class DummyLog(object):
    def __init__(self):
        self.warnings = []

    def warning(self, msg, *args, **kwds):
        self.warnings.append(msg)


def test_expression():
    expr = Expression(DummyLog(), 'a and (b - 1)', 'sa and not sb')
    assert expr.interesting_keys() == set(['a', 'b'])

    # no values: not triggered
    assert not expr.triggered

    expr.new_setups(['sa'])
    # setup matches but still no values
    assert not expr.triggered

    expr.update(0, {'a': 1})
    # still not all values given
    assert not expr.triggered
    assert expr.is_expired(10)

    expr.update(0, {'a': 1, 'b': 2})
    # now we are triggered!
    assert expr.triggered
    assert not expr.is_expired(10)

    expr.update(0, {'a': 1, 'b': 1})
    assert not expr.triggered

    expr.new_setups([])
    expr.update(0, {'a': 1, 'b': 2})
    assert not expr.triggered

    assert not expr.log.warnings
    expr.update(0, {'a': 1, 'b': None})
    assert expr.log.warnings


def test_delayed():
    expr = Expression(DummyLog(), 'a', '')
    delayed = DelayedTrigger(DummyLog(), expr, 5)

    assert delayed.interesting_keys() == set(['a'])

    assert not delayed.triggered
    delayed.update(0, {'a': 1})
    assert not delayed.triggered
    delayed.update(4, {'a': 1})
    assert not delayed.triggered
    delayed.update(5, {'a': 1})
    assert delayed.triggered

    delayed.update(6, {'a': 1})
    assert delayed.triggered
    delayed.update(7, {'a': 0})
    assert not delayed.triggered
    delayed.update(8, {'a': 1})
    assert not delayed.triggered

    delayed.tick(13)
    assert delayed.triggered


def test_precondition():
    aexpr = Expression(DummyLog(), 'a', '')
    bexpr = Expression(DummyLog(), 'b', '')
    precond = Precondition(DummyLog(), aexpr, bexpr)

    assert precond.interesting_keys() == set(['a', 'b'])

    precond.update(0, {'a': 0, 'b': 0})
    assert not precond.triggered
    precond.update(0, {'a': 0, 'b': 1})
    assert not precond.triggered

    precond.update(0, {'a': 1, 'b': 0})
    assert not precond.triggered
    precond.update(0, {'a': 1, 'b': 1})
    assert precond.triggered
