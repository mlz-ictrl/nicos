#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Flexible Timers, thread free."""

import time


# XXX
# also use a singleton to 'register' all timer objects and
# one single thread regularly checking all timers 'is_running'
#
# XXX: do we need locking? (multithreads?)

class Timer(object):
    """Flexible Timer class."""

    _started = 0
    _stopped = 0
    _active = False
    _run_for = None
    _cb_func = None

    def __init__(self, run_for=None, cb_func=None, *cb_args, **cb_kwds):
        """
        Constructor for timers.

        optional arguments (default to None):
        - run_for: How many seconds until the timer stops.
                   If not specified, the timer is just a 'stopwatch'.
        - cb_func: callback function to be called once the timer times out.
                   signature is cb_func(timer, *cb_args, **cb_kwds)

        As the Timer is implemented thread free, the callback may be delayed
        and is ONLY ever called if the timer runs out and ``is_running`` is
        called or the ``wait`` method is used.
        """
        self.start(run_for, cb_func, *cb_args, **cb_kwds)

    def start(self, run_for=None, cb_func=Ellipsis, *cb_args, **cb_kwds):
        """
        Start the timer.

        arguments (default to None):
        - run_for: How many seconds until the timer (auto) stops.
                   If not specified, the timer is just a 'stopwatch'.
        - cb_func: callback function to be called once the timer times out.
                   signature is cb_func(timer, *cb_args, **cb_kwds)
                   if you want to just update the cb_args or cb_kwds you
                   have to provide cb_func as well!

        As the Timer is implemented thread free, the callback may be delayed
        and is ONLY ever called if the timer runs out and ``is_running`` is
        called or the ``wait`` method is used.

        Any parameter overwrites earlier ones.
        (so to stop from using a callback and instantly (re-)starting the timer
         for 5s use start(5))

        If called while the timer is still 'running', the timer will be
        restarted, i.e. no 'timeoutaction' will be performed and no callback
        called.
        """
        if cb_func is not Ellipsis:
            self._cb_args = cb_args
            self._cb_kwds = cb_kwds
            self._cb_func = cb_func
        self._run_for = run_for
        self._started = time.time()
        self._active = True

    def stop(self):
        """Stop the timer.

        Do nothing if already stopped.
        """
        if self._active:
            self._stopped = time.time()
            self._active = False

    def is_running(self):
        """Return True if the timer is still 'running'.

        Will trigger running the callback if the timer is just now beyond its
        intended running time.
        """
        if self._run_for is None:
            # runs until stopped explicitly
            return self._active
        if self._active:
            if self._started + self._run_for < time.time():
                # time is up !
                self.stop()
                self._run_cb()
        return self._active

    def elapsed_time(self):
        """Return the time the timer already run."""
        if self._active:
            return time.time() - self._started
        if self._run_for is None:
            return self._stopped - self._started
        return min(self._run_for, self._stopped - self._started)

    def remaining_time(self):
        """Return the remaining time or None (if timer will run forever)."""
        if self._run_for is None:
            return None
        return self._run_for - self.elapsed_time()

    def _run_cb(self):
        if callable(self._cb_func):
            self._cb_func(self, *self._cb_args, **self._cb_kwds)

    def wait(self, interval=5, notify_func=None, *notify_args):
        """Wait until the timer is finished.

        The timer must be already started with a run_for argument
        (or we return immediately).
        Waiting is done in time slices of ``interval`` seconds.
        If the optional ``notify_func`` is a callable,
        we call it at the end of the slice with the timer object
        and the remaining arguments.
        """
        if self._run_for is None or not self._active:
            return
        while self.is_running():
            remaining = self.remaining_time()
            if remaining > interval:
                time.sleep(interval)
            else:
                if remaining > 0:
                    time.sleep(remaining)
            if callable(notify_func):
                notify_func(self, *notify_args)

    def restart(self):
        """Continue a prematurely stopped timer."""
        if self._active:
            return
        # adjust timestamp so that it looks as nothing had ever happened
        if self._run_for is None:
            self._started = time.time() - self.elapsed_time()
        elif self.remaining_time():
            self._started  = time.time() + self.elapsed_time() - self._run_for
        self._active = True
