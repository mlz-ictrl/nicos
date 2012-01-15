#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""Utilities for the session classes."""

__version__ = "$Revision$"

import os
import time
import socket
import exceptions
import rlcompleter

from nicos import session
from nicos.core.errors import UsageError


class NicosNamespace(dict):
    """
    A dict subclass that has a list of identifiers that cannot be set, except
    using the setForbidden() method.
    """

    def __init__(self):
        self.__forbidden = set()

    def addForbidden(self, name):
        self.__forbidden.add(name)

    def removeForbidden(self, name):
        self.__forbidden.discard(name)

    def setForbidden(self, name, value):
        dict.__setitem__(self, name, value)

    def __setitem__(self, name, value):
        if name in self.__forbidden:
            raise UsageError('%s cannot be assigned to' % name)
        dict.__setitem__(self, name, value)

    def __delitem__(self, name):
        if name in self.__forbidden:
            raise UsageError('%s cannot be deleted' % name)
        dict.__delitem__(self, name)


class SimClock(object):
    """Simulation clock."""

    def __init__(self):
        self.time = 0

    def reset(self):
        self.time = 0

    def wait(self, time):
        if self.time < time:
            self.time = time

    def tick(self, sec):
        self.time += sec


class NicosCompleter(rlcompleter.Completer):
    """
    This is a Completer subclass that doesn't show private attributes when
    completing attribute access.
    """

    attr_hidden = set(['attached_devices', 'parameters', 'hardware_access',
                       'temporary', 'log', 'valuetype', 'mro'])
    global_hidden = set(dir(exceptions))

    def attr_matches(self, text):
        matches = rlcompleter.Completer.attr_matches(self, text)
        textlen = len(text)
        return [m for m in matches if not (m[textlen:].startswith(('_', 'do'))
                                           or m[textlen:] in self.attr_hidden)]

    def global_matches(self, text):
        matches = rlcompleter.Completer.global_matches(self, text)
        return [m for m in matches if m[:-1] not in self.global_hidden]

    def get_matches(self, text):
        if '.' in text:
            return self.attr_matches(text)
        else:
            return self.global_matches(text)


class LoggingStdout(object):
    """
    Standard output stream replacement that tees output to a logger.
    """

    def __init__(self, orig_stdout):
        self.orig_stdout = orig_stdout

    def write(self, text):
        if text.strip():
            session.log.info(text)
        self.orig_stdout.write(text)

    def flush(self):
        self.orig_stdout.flush()


# session id support

def makeSessionId():
    """Create a unique identifier for the current session."""
    try:
        hostname = socket.getfqdn()
    except socket.error:
        hostname = 'localhost'
    pid = os.getpid()
    timestamp = int(time.time())
    return '%s@%s-%s' % (pid, hostname, timestamp)

def sessionInfo(id):
    """Return a string with information gathered from the session id."""
    pid, rest = id.split('@')
    host, timestamp = rest.split('-')
    return 'PID %s on host %s, started on %s' % (
        pid, host, time.asctime(time.localtime(int(timestamp))))
