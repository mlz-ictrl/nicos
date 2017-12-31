#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""
Python interface to the _pyctl module, to control the execution of Python
code via a C trace function.
"""
from __future__ import absolute_import

__all__ = ['LINENO_ALL', 'LINENO_TOPLEVEL', 'LINENO_NAME',
           'Controller', 'ControlStop']

import threading
import traceback

from nicos.protocols.daemon import STATUS_RUNNING, STATUS_INBREAK

# import logic here - please do not change this order:
#    1) try the in-package version (for inplace builds)
#    2) try version from platform specific directory (no package prefix)
try:
    from nicospyctl.pyctl import ControlStop, Controller as _Controller
except ImportError:
    ControlStop = BaseException

    class _Controller(object):
        def __init__(self, *args, **kwds):
            raise ImportError('Please install the nicos-pyctl package.')

# defines from the C module
LINENO_ALL      = 0   # trace all line numbers
LINENO_TOPLEVEL = 1   # trace only line numbers in toplevel frame
LINENO_NAME     = 2   # trace only line numbers in frames with the
                      # filename given by break_only_in_filename


class Controller(_Controller):
    """
    The Controller object allows to execute Python code in a controlled
    environment using the Python tracing mechanism (using a C trace function
    instead of a Python one for speed).

    The running code can therefore be halted and stopped from another thread.
    Additionally, the currently executed line and Python frame can be observed.

    Halting works by calling a custom function ("break function") from the trace
    function -- until this function returns the execution is halted.

    Stopping works by throwing an exception from the trace function into the
    frame executing code, where it should be allowed to propagate to the
    toplevel and exit excecution.  The exception (ControlStop) inherits from
    BaseException.  This works nicely together with "finally:" clauses, but
    requires that bare "except:" clauses are replaced by "except Exception:".

    There are various options to control breaking behavior.  By default, a break
    can occur everywhere.  "break_only_in_toplevel" limits breaking so that a
    break can only occur between two lines of code in the toplevel code.
    "break_only_in_filename" works similar, but if it is set, breaks can occur
    in all frames whose code has the given filename.  Using this, breakpoints in
    non-toplevel code are implemented.

    Using an "observer" callable, changes in the line number and execution need
    not be polled: each time the status or line number changes, the observer is
    called as observer(status, lineno).

    The external interface is usually used like this:

    In the executing thread:
    * instantiate the Controller object
    * call set_observer() to add an observer
    * call start()/start_exec()

    In the controlling thread:
    * when halting is wanted, call set_break()
    * when continuing is wanted, call set_continue()
    * when stopping is wanted, call set_stop()

    Signature of the C class:

    Controller(breakfunc,                     # break function
               break_only_in_toplevel=False,  # see above
               break_only_in_filename=None,   # see above
               lineno_behavior)               # which line numbers to trace

    Methods of the C class:

    - start(callable): start execution, calling the given callable as toplevel
    - start_exec(code, globals[, locals]): start execution of the given code
      object with the global and local scopes
    - set_break(arg): request a break, the breakfunc will be called at the
      next trace function run, the arg is given to the breakfunc; a not-None
      arg is supposed to mean "stop"
    - set_stop(arg): request a stop, the arg will be used as an intializer
      argument to the ControlStop exception
    - set_observer(observer): attach an observer to the instance

    Attributes of the C class:

    - status: execution status
    - currentframe: current execution frame
    - toplevelframe: first and topmost execution frame
    - lineno: current line number (in which frame, see lineno_behavior)
    """

    # pylint: disable=W0231
    def __init__(self, break_only_in_toplevel=False,
                 break_only_in_filename=None, lineno_behavior=None):
        if lineno_behavior is None:
            if break_only_in_toplevel:
                lineno_behavior = LINENO_TOPLEVEL
            elif break_only_in_filename:
                lineno_behavior = LINENO_NAME
            else:
                lineno_behavior = LINENO_ALL
        _Controller.__init__(self, self._breakfunc, break_only_in_toplevel,
                             break_only_in_filename, lineno_behavior)
        self.__continue = threading.Event()
        self.__continue_arg = None

    def _breakfunc(self, frame, arg):
        """Called when execution has been halted."""
        flag = self.wait_for_continue()
        if flag is not None:
            self.set_stop(flag)

    def wait_for_continue(self):
        """Called from the break func: wait for set_continue() to be called."""
        self.__continue.wait()
        self.__continue.clear()
        return self.__continue_arg

    def set_continue(self, arg):
        """Allow continuation of a halted execution."""
        self.__continue_arg = arg
        self.__continue.set()

    def stop(self, arg):
        """Called from outside: stop execution."""
        if arg is None:
            arg = 'stop method called'
        # if execution is running, we set a stop flag ourselves
        if self.status == STATUS_RUNNING:
            self.set_stop(arg)
        # else we let wait_for_continue() return the arg, and the breakfunc
        # must call set_stop()
        elif self.status == STATUS_INBREAK:
            self.set_continue(arg)

    def get_stacktrace(self, limit=None):
        """Return a stacktrace of the currently executed code."""
        frame = self.currentframe
        if frame is None:
            return None
        return ''.join(traceback.format_stack(frame, limit)[2:])
