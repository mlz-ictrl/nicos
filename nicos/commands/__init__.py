#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Base package for NICOS commands."""

import sys
from functools import wraps

from nicos import session
from nicos.core.errors import UsageError


def usercommand(func):
    """Decorator that marks a function as a user command."""
    func.is_usercommand = True
    func.is_hidden = False
    return func


def hiddenusercommand(func):
    """Decorator that marks a function as a user command that should not be
    displayed by the online help.
    """
    func.is_usercommand = True
    func.is_hidden = True
    return func


def helparglist(args):
    """Decorator that supplies a custom argument list to be displayed by
    the online help.
    """
    def deco(func):
        func.help_arglist = args
        return func
    return deco


def parallel_safe(func):
    """Decorator that marks a user command as safe for execution in
    parallel to the main script.
    """
    func.is_parallel_safe = True
    return func


RERAISE_EXCEPTIONS = (
    EnvironmentError,
    MemoryError,
    SystemError,
)


def usercommandWrapper(func):
    """Wrap a function as a user command.

    This is not done in the "usercommand" decorator since the function
    should stay usable as a regular function from nicos code.
    """
    from nicos.commands.output import printerror
    parallel_safe = getattr(func, 'is_parallel_safe', False)

    @wraps(func)
    def wrapped(*args, **kwds):
        if not parallel_safe and session.checkParallel():
            raise UsageError('the %s command cannot be used with "execute now"'
                             % func.__name__)
        try:
            try:
                # try executing the original function with the given arguments
                return func(*args, **kwds)
            except TypeError:
                # find out if the call itself caused this error, which means
                # that wrong arguments were given to the command
                traceback = sys.exc_info()[2]
                # find last call frame
                while traceback.tb_next:
                    traceback = traceback.tb_next
                if traceback.tb_frame.f_code is wrapped.__code__:
                    printerror('Invalid arguments for %s()' % func.__name__)
                    help(func)
                raise
            except UsageError:
                # for usage errors, print the error and the help for the
                # command
                help(func)
                raise
        except RERAISE_EXCEPTIONS:
            # don't handle these, they should lead to an unconditional abort
            raise
        except Exception:
            # all others we'll handle and continue, if wanted
            if hasattr(session.experiment, 'errorbehavior') and \
               session.experiment.errorbehavior == 'report':
                session.scriptEvent('exception', sys.exc_info())
            else:
                raise
    wrapped.is_usercommand = True
    # store a reference to the original function, so that help() can find
    # out the argument specification by looking at it
    wrapped.real_func = getattr(func, 'real_func', func)
    return wrapped
