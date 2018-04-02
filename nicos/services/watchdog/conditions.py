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

"""Condition objects for the NICOS watchdog."""

from __future__ import absolute_import, division, print_function

import ast

from nicos.utils import checkSetupSpec


class Condition(object):
    """Represents the current state of a watchdog condition.

    An Entry has a single condition that is triggered or not.  Whenever its
    state changes to triggered, the watchdog device will act (add condition to
    warn list, call notifiers, execute action).  When the state changes to not
    triggered, it will remove the condition from the warn list and execute the
    ok action, if configured.

    The complex logic regarding preconditions and gracetime is handled by
    stacking Condition objects on top of each other.

    Besides triggered, the condition can also be "expired": if some cache keys
    used to calculate the triggered state are not available any more, the
    condition becomes expired and the user is notified.

    Finally, conditions can be disabled, which means that their triggered
    state is ignored.  They can be disabled by the user directly, or by
    configuring them to be specific to certain setups.
    """

    # true if enabled by user
    enabled = True

    # true if triggered, can be a property in derived classes
    triggered = False

    def __init__(self, log):
        self.log = log

    def is_expired(self, time):
        """Return true if the condition is expired at the given time."""

    def interesting_keys(self):
        """Return cache keys that this instance needs to be notified about."""

    def new_setups(self, setups):
        """Must be called when the list of setups changes."""

    def tick(self, time):
        """Must be called to notify that some time has passed.

        Return true if triggered-status *may* have changed.
        """

    def update(self, time, keydict):
        """Must be called to notify about a cache key-value change."""


class Expression(Condition):
    """A condition that evaluates an expression made up of cache keys."""

    def __init__(self, log, expr, setup_expr):
        Condition.__init__(self, log)
        self.expr = expr
        self.keys = set()
        self.setup_expr = setup_expr
        # if we don't have a specific setup expression, we're enabled,
        # otherwise wait for new_setups() to be called
        self.setup_enabled = not self.setup_expr
        self.expires_at = 0
        cond_parse = ast.parse(expr)
        for node in ast.walk(cond_parse):
            if isinstance(node, ast.Name):
                self.keys.add(node.id.lower())

    def is_expired(self, time):
        return self.expires_at and time > self.expires_at

    def interesting_keys(self):
        return set(self.keys)

    def new_setups(self, setups):
        self.setup_enabled = checkSetupSpec(self.setup_expr, setups)
        self.expires_at = 0

    def update(self, time, keydict):
        try:
            value = eval(self.expr, keydict)
        except NameError:
            if self.setup_enabled and self.enabled:
                self.expires_at = time + 6
        except Exception:
            self.log.warning('error evaluating %r warning '
                             'condition', self.expr, exc=1)
        else:
            self.expires_at = 0
            self.triggered = bool(value) and self.enabled and self.setup_enabled


class DelayedTrigger(Condition):
    """A condition that takes another condition and passes through its
    triggered state, but only after a certain delay time.
    """

    def __init__(self, log, cond, delay):
        Condition.__init__(self, log)
        self.cond = cond
        self.delay = delay
        self.t_trigger = 0

    @property
    def triggered(self):
        return self.enabled and self.cond.triggered and self.t_trigger == 0

    def is_expired(self, time):
        return self.cond.is_expired(time)

    def new_setups(self, setups):
        self.cond.new_setups(setups)

    def interesting_keys(self):
        return self.cond.interesting_keys()

    def tick(self, time):
        self.cond.tick(time)
        if self.t_trigger and time >= self.t_trigger:
            # delay elapsed, reset trigger
            self.t_trigger = 0
            return True

    def update(self, time, keydict):
        prev_triggered = self.cond.triggered
        self.cond.update(time, keydict)
        if not prev_triggered and self.cond.triggered:
            # rising edge: set trigger
            self.t_trigger = time + self.delay
        elif prev_triggered and not self.cond.triggered:
            # falling edge: clear trigger
            self.t_trigger = 0
        elif self.t_trigger and time >= self.t_trigger:
            # delay elapsed, reset trigger
            self.t_trigger = 0


class Precondition(Condition):
    """A condition that passes through another condition's triggered state,
    but only if a different condition (the precondition) was triggered before
    the main one triggered.
    """

    def __init__(self, log, pre, cond):
        Condition.__init__(self, log)
        self.pre = pre
        self.cond = cond
        self.pre_latch = False

    @property
    def triggered(self):
        return self.enabled and self.pre_latch and self.cond.triggered

    def is_expired(self, time):
        return self.pre.is_expired(time) or self.cond.is_expired(time)

    def new_setups(self, setups):
        self.pre.new_setups(setups)
        self.cond.new_setups(setups)

    def interesting_keys(self):
        return self.pre.interesting_keys() | self.cond.interesting_keys()

    def tick(self, time):
        return self.pre.tick(time) or self.cond.tick(time)

    def update(self, time, keydict):
        prev_pre_triggered = self.pre.triggered
        self.pre.update(time, keydict)
        self.cond.update(time, keydict)
        if (prev_pre_triggered or self.pre.triggered) and self.cond.triggered:
            self.pre_latch = True
        if not self.cond.triggered:
            self.pre_latch = False
