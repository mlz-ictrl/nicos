#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""
Utilities for the NICOS daemon.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import re
import sys
import time
import logging
import linecache
import traceback
import __builtin__


TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'

# -- General utilities ---------------------------------------------------------

def format_exception_cut_frames(cut=0):
    """
    Format an exception with traceback, but leave out the first `cut`
    number of frames.
    """
    typ, val, tb = sys.exc_info()
    res = ['Traceback (most recent call last):\n']
    tbres = traceback.format_tb(tb, sys.maxint)
    res += tbres[cut:]
    res += traceback.format_exception_only(typ, val)
    return ''.join(res)


def format_script(script, prompt='>>>'):
    """Format a script with timestamp."""
    prompt = '%s [%s] ' % (prompt, time.strftime(TIMESTAMP_FMT))
    if '\n' not in script.text:
        return prompt + ' ' + script.text
    else:
        if not script.name:
            start = prompt + '-'*20
        else:
            start = prompt + '-'*20 + ' ' + script.name
        end = '-' * (16 + len(prompt)) + ' <<<'
        return '%s\n%s%s <<<' % (start, script.text, end)


def format_timestamp(prompt='<<<'):
    """Print a timestamp to stdout."""
    return '%s [%s]' % (prompt, time.strftime(TIMESTAMP_FMT))


_bare_except = re.compile(r'^([ \t]*)except[ \t]*:', re.MULTILINE)

def fixup_script(script):
    """Perform some fixup operations on the script."""
    # Replace bare except clauses by "except Exception" to prevent
    # catching the ControlStop exception used by pyctl
    return _bare_except.sub(r'\1except Exception:', script)


def update_linecache(name, script):
    """
    Set the linecache for a pseudo-module so that the traceback module
    can extract the source code when creating tracebacks.
    """
    linecache.cache[name] = (len(script), None,
                             [l+'\n' for l in script.splitlines()], name)


# -- Logging utilities ---------------------------------------------------------

class LoggerWrapper(object):
    """
    Adds more information to logging records.  Similar to LoggerAdapter,
    which is new in Python 2.5.
    """
    def __init__(self, logger, prepend):
        self.logger = logger
        self.prepend = prepend

        for name in ('debug', 'info', 'warning', 'error',
                     'critical', 'exception'):
            def getlogfunc(name=name):
                def logfunc(msg, *args, **kwds):
                    getattr(self.logger, name)(prepend+msg, *args, **kwds)
                return logfunc
            setattr(self, name, getlogfunc())


TRANSMIT_ENTRIES = ['name', 'created', 'levelno', 'message', 'exc_text']

class DaemonLogHandler(logging.Handler):
    """
    Log handler for transmitting NICOS log messages to the client.
    """

    def __init__(self, daemon):
        logging.Handler.__init__(self)
        self.daemon = daemon

    def emit(self, record, entries=TRANSMIT_ENTRIES):
        # "message" is by convention created by a handler; let's assume that
        # the logfile handler already did that
        #record.message = record.getMessage()
        msg = [getattr(record, e) for e in entries]
        if not hasattr(record, 'nonl'):
            msg[3] += '\n'
        self.daemon._messages.append(msg)
        self.daemon.emit_event('message', msg)


# -- Module reloading handling -------------------------------------------------

class ModuleManager(object):
    """
    Remembers which modules were imported at its creation time, and
    restores sys.modules to that on purge().
    """
    def __init__(self, protect=[]):
        self._modules = set(sys.modules.keys())
        print [k for k in sys.modules if sys.modules[k]]
        self._protect = set(protect)

    def purge(self):
        for key in sys.modules.keys():
            if key not in self._modules and key not in self._protect:
                del sys.modules[key]
