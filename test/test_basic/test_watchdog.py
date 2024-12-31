# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

from nicos.services.watchdog.conditions import ConditionWithPrecondition, \
    DelayedTrigger, Expression


class DummyLog:
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


def test_expired():
    expr = Expression(DummyLog(), 'a and b', '')

    # no values: not triggered, not expired
    assert not expr.triggered
    assert not expr.is_expired(0)

    expr.update(0, {'a': 1})
    # expires after 6 seconds
    assert not expr.is_expired(5)
    assert expr.is_expired(10)

    # needs to be still expired, not all values given
    expr.update(12, {'a': 1})
    assert expr.is_expired(12)


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
    pre = Expression(DummyLog(), 'pre', '')
    cond = Expression(DummyLog(), 'cond', '')
    cooldown = 0
    combined = ConditionWithPrecondition(DummyLog(), pre, cond, cooldown)

    assert combined.interesting_keys() == set(['pre', 'cond'])

    combined.update(1, {'pre': 0, 'cond': 0})
    assert not combined.triggered
    combined.update(1, {'pre': 0, 'cond': 1})
    assert not combined.triggered
    combined.update(1, {'pre': 1, 'cond': 0})
    assert not combined.triggered
    combined.update(1, {'pre': 1, 'cond': 1})
    assert combined.triggered

    # if condition becomes true the instant precondition becomes false,
    # we are still happy
    combined.update(1, {'pre': 1, 'cond': 0})
    assert not combined.triggered
    combined.update(1, {'pre': 0, 'cond': 1})
    assert combined.triggered


def test_pre_with_cooldown():
    pre = Expression(DummyLog(), 'pre', '')
    pre = DelayedTrigger(DummyLog(), pre, 2)
    cond = Expression(DummyLog(), 'cond', '')
    cond = DelayedTrigger(DummyLog(), cond, 2)
    cooldown = 5
    combined = ConditionWithPrecondition(DummyLog(), pre, cond, cooldown)

    assert combined.interesting_keys() == set(['pre', 'cond'])

    combined.update(0, {'pre': 0, 'cond': 0})
    assert not combined.pre.triggered
    assert not combined.cond.triggered
    assert not combined.triggered
    combined.update(10, {'pre': 1, 'cond': 0})
    assert not combined.pre.triggered
    combined.update(15, {'pre': 1, 'cond': 0})
    assert combined.pre.triggered
    assert not combined.triggered
    combined.update(20, {'pre': 1, 'cond': 1})
    assert not combined.triggered
    combined.update(25, {'pre': 1, 'cond': 1})
    assert combined.triggered
    combined.update(30, {'pre': 0, 'cond': 1})
    assert combined.triggered
    combined.update(36, {'pre': 0, 'cond': 1})
    assert not combined.triggered

    combined.update(100, {'pre': 0, 'cond': 0})
    assert not combined.pre.triggered
    assert not combined.cond.triggered
    assert not combined.triggered
    combined.update(110, {'pre': 1, 'cond': 0})
    assert not combined.pre.triggered
    combined.update(115, {'pre': 1, 'cond': 0})
    assert combined.pre.triggered
    assert not combined.triggered
    combined.update(120, {'pre': 0, 'cond': 1})
    assert not combined.pre.triggered
    assert not combined.triggered
    combined.update(125, {'pre': 0, 'cond': 1})
    assert not combined.pre.triggered
    assert combined.triggered
    combined.update(126, {'pre': 0, 'cond': 1})
    assert not combined.pre.triggered
    assert not combined.triggered
