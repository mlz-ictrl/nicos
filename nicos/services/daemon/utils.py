#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
import ast
import time
import logging
import linecache
from threading import Lock, Event

from nicos import session
from nicos.utils.loggers import ACTION, recordToMessage
from nicos.pycompat import text_type


TIMESTAMP_FMT = '%Y-%m-%d %H:%M:%S'

# compile flag to activate new division
CO_DIVISION = 0x2000

# -- General utilities --------------------------------------------------------

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
        end = '-' * (16 + len(prompt)) + (' <<<' if prompt == '>>>' else '----')
        text = _excessive_ws_re.sub('\n', script.text)
        return '%s\n%s%s' % (start, text, end)


_bare_except = re.compile(r'^([ \t]*)except[ \t]*:', re.MULTILINE)


def fixupScript(script):
    """Perform some fixup operations on the script."""
    # Replace bare except clauses by "except Exception" to prevent
    # catching the ControlStop exception used by pyctl
    return _bare_except.sub(r'\1except Exception:', script)


# pylint: disable=redefined-builtin
def parseScript(script, name=None, format=None, compilecode=True):
    if compilecode:
        def compiler(src):
            if not isinstance(src, text_type):
                src = src.decode('utf-8')
            return compile(src + '\n', '<script>', 'single', CO_DIVISION)
    else:
        compiler = lambda src: src
    if '\n' not in script:
        # if the script is a single line, compile it like a line
        # in the interactive interpreter, so that expression
        # results are shown
        code = [session.commandHandler(script, compiler)]
        blocks = None
    else:
        pycode = script
        # check for SPM scripts
        if format != 'py':
            pycode = session.scriptHandler(script, name or '', lambda c: c)
        # replace bare except clauses in the code with "except Exception"
        # so that ControlStop is not caught
        pycode = fixupScript(pycode)
        if not compilecode:
            # no splitting desired
            code = [compiler(pycode)]
            blocks = None
        else:
            # long script: split into blocks
            code, blocks = splitBlocks(pycode)

    return code, blocks


def splitBlocks(text):
    """Parse a script into multiple blocks."""
    codelist = []
    if not isinstance(text, text_type):
        text = text.decode('utf-8')
    mod = ast.parse(text + '\n', '<script>')
    assert isinstance(mod, ast.Module)
    # construct an individual compilable unit for each block
    for toplevel in mod.body:
        new_mod = ast.Module()
        new_mod.body = [toplevel]
        # do not change the name (2nd parameter); the controller
        # depends on that
        codelist.append(compile(new_mod, '<script>', 'exec', CO_DIVISION))
    return codelist, mod.body


def updateLinecache(name, script):
    """
    Set the linecache for a pseudo-module so that the traceback module
    can extract the source code when creating tracebacks.
    """
    linecache.cache[name] = (len(script), None,
                             [l+'\n' for l in script.splitlines()], name)


# -- Logging utilities --------------------------------------------------------

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

    def emit(self, record):
        msg = recordToMessage(record, self.ctrl.reqid_work)
        if record.levelno != ACTION:
            # do not cache ACTIONs, they do not contribute to useful output if
            # received after the fact (this should also lower memory consumption
            # of the daemon a bit)
            self.daemon._messages.append(msg)
            # limit to 100000-110000 messages
            if len(self.daemon._messages) > 110000:
                del self.daemon._messages[:10000]
        self.daemon.emit_event('message', msg)


# -- Script queue -------------------------------------------------------------

class QueueOperator(object):
    """Operations on the queue that must be done while the lock is held."""

    def __init__(self, queue):
        self.queue = queue

    def get_item(self, key):
        for item in self.queue.scripts:
            if item.reqid == key:
                return item
        raise IndexError

    def move_item(self, item_id, newindex):
        for i, item in enumerate(self.queue.scripts):
            if item.reqid == item_id:
                self.queue.scripts.insert(newindex, self.queue.scripts.pop(i))

    def get_ids(self):
        return [item.reqid for item in self.queue.scripts]

    def update(self, reqid, newcode, user):
        self.queue[reqid].text = newcode
        self.queue[reqid].user = user.name


class ScriptQueue(object):
    """Specialized queue for scripts that can be re-sorted and updated."""

    def __init__(self):
        self.scripts = []
        self._lock = Lock()
        self._event = Event()
        self._event.clear()

    def put(self, item):
        """Put a new script onto the queue."""
        with self._lock:
            self.scripts.append(item)
            self._event.set()

    def get(self):
        """Get (blockingly) the next script from the queue."""
        self._event.wait()
        with self._lock:
            temp = self.scripts.pop(0)
            if not self.scripts:
                self._event.clear()
        return temp

    def delete_one(self, key):
        """Delete script with a given reqid from the queue."""
        with self._lock:
            for item in self.scripts:
                if item.reqid == key:
                    self.scripts.remove(item)
                    if not self.scripts:
                        self._event.clear()
                    return
            raise IndexError

    def delete_all(self):
        """Delete all scripts and returns their reqids in a list."""
        with self._lock:
            deleted = [item.reqid for item in self.scripts]
            self.scripts = []
            self._event.clear()
        return deleted

    def serialize_queue(self):
        """Return serialized form of all scripts."""
        with self._lock:
            return [req.serialize() for req in self.scripts]

    def __enter__(self):
        self._lock.acquire()
        return QueueOperator(self)

    def __exit__(self, *exc):
        self._lock.release()
