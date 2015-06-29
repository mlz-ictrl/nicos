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

"""Utilities for the NICOS daemon."""

import re
import time
import logging
import linecache

from nicos.utils.loggers import ACTION, TRANSMIT_ENTRIES


TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'

# -- General utilities ---------------------------------------------------------

_excessive_ws_re = re.compile(r'\n\s*\n')


def formatScript(script, prompt='>>>'):
    """Format a script with timestamp."""
    if script.quiet:
        return '%s [%s %s] %s' % (prompt, script.user,
                                  time.strftime(TIMESTAMP_FMT), script.name)
    if script.user:
        prompt = '%s [%s %s] ' % (prompt, script.user,
                                  time.strftime(TIMESTAMP_FMT))
    else:
        prompt = '%s [%s] ' % (prompt, time.strftime(TIMESTAMP_FMT))
    if '\n' not in script.text:
        return prompt + ' ' + script.text
    else:
        if not script.name:
            start = prompt + '-'*20
        else:
            start = prompt + '-'*20 + ' ' + script.name
        end = '-' * (16 + len(prompt)) + ' <<<'
        text = _excessive_ws_re.sub('\n', script.text)
        return '%s\n%s%s' % (start, text, end)


_bare_except = re.compile(r'^([ \t]*)except[ \t]*:', re.MULTILINE)


def fixupScript(script):
    """Perform some fixup operations on the script."""
    # Replace bare except clauses by "except Exception" to prevent
    # catching the ControlStop exception used by pyctl
    return _bare_except.sub(r'\1except Exception:', script)


def updateLinecache(name, script):
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


class DaemonLogHandler(logging.Handler):
    """
    Log handler for transmitting NICOS log messages to the client.
    """

    def __init__(self, daemon):
        logging.Handler.__init__(self)
        self.daemon = daemon
        self.ctrl = daemon._controller

    def emit(self, record, entries=TRANSMIT_ENTRIES):  # pylint: disable=W0221
        msg = [getattr(record, e) for e in entries]
        if not hasattr(record, 'nonl'):
            msg[3] += '\n'
        # record which request caused this message
        msg.append(self.ctrl.reqno_work)
        if record.levelno != ACTION:
            # do not cache ACTIONs, they do not contribute to useful output if
            # received after the fact (this should also lower memory consumption
            # of the daemon a bit)
            self.daemon._messages.append(msg)
            # limit to 100000-110000 messages
            if len(self.daemon._messages) > 110000:
                del self.daemon._messages[:10000]
        self.daemon.emit_event('message', msg)
