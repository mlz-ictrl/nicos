# -*- coding: utf-8 -*-
"""
    nicm.commands
    ~~~~~~~~~~~~~

    Base package for NICOS commands.
"""

import sys
from functools import wraps

from nicm.errors import NicmError, UsageError

from nicm.commands.basic import help, NicmSetup, NicmAddSetup, NicmExport, \
     NicmFactory, NicmDestroy, NicmPrint
from nicm.commands.device import move, maw, switch, wait, read, status, \
     stop, count, set, get, listparams, listdevices
from nicm.commands.output import printdebug, printinfo, printwarning, \
     printerror, printexception

__commands__ = [
    'printdebug', 'printinfo', 'printwarning', 'printerror', 'printexception',
    'NicmSetup', 'NicmAddSetup', 'NicmFactory', 'NicmDestroy',
    'NicmPrint', 'NicmExport',
    'help', 'move', 'maw', 'switch', 'wait', 'read', 'status', 'stop',
    'count', 'set', 'get', 'listparams', 'listdevices',
]


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
