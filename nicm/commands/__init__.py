#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS standard commands package
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Base package for NICOS commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import sys
from functools import wraps

from nicm.errors import NicmError, UsageError


__commands__ = []

def import_all_commands(module):
    mod = __import__(module, None, None, ['__commands__'])
    for command in mod.__commands__:
        __commands__.append(command)
        globals()[command] = getattr(mod, command)

import_all_commands('nicm.commands.basic')
import_all_commands('nicm.commands.device')
import_all_commands('nicm.commands.output')


def user_command(func):
    """Decorator that registers a function as a user command."""
    @wraps(func)
    def wrapped(*args, **kwds):
        try:
            # try executing the original function with the given arguments
            return func(*args, **kwds)
        except TypeError, err:
            # find out if the call itself caused this error, which means that
            # wrong arguments were given to the command
            traceback = sys.exc_info()[2]
            # find last call frame
            while traceback.tb_next:
                traceback = traceback.tb_next
            if traceback.tb_frame.f_code is wrapped.func_code:
                printerror('Usage error: invalid arguments for %s()'
                           % func.__name__)
                help(func)
            else:
                printexception()
        except UsageError:
            # for usage errors, print the error and the help for the command
            printexception()
            help(func)
        except Exception:
            # for other errors, print them a friendly fashion
            printexception()
    wrapped.is_usercommand = True
    # store a reference to the original function, so that help() can find
    # out the argument specification by looking at it
    wrapped.real_func = getattr(func, 'real_func', func)
    return wrapped
