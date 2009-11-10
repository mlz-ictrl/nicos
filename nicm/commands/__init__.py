# -*- coding: utf-8 -*-
"""
    nicm.commands
    ~~~~~~~~~~~~~

    Base package for NICOS commands.
"""

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
