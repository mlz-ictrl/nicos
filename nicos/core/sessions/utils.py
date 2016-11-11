#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Utilities for the session classes."""

import os
import re
import time
import socket
import keyword
import rlcompleter

try:
    import readline
except ImportError:
    readline = None

from nicos import session
from nicos.core import Device, UsageError, \
    MASTER, SLAVE, SIMULATION, MAINTENANCE, \
    DeviceAlias
from nicos.pycompat import builtins, iteritems


BUILTIN_EXCEPTIONS = set(name for name in dir(builtins)
                         if name.endswith(('Error', 'Warning')))

EXECUTIONMODES = [MASTER, SLAVE, SIMULATION, MAINTENANCE]


class NicosNamespace(dict):
    """
    A dict subclass that has a list of identifiers that cannot be set, except
    using the setForbidden() method.
    """

    def __init__(self):
        dict.__init__(self)
        self.__forbidden = set()

    def addForbidden(self, name):
        self.__forbidden.add(name)

    def removeForbidden(self, name):
        self.__forbidden.discard(name)

    def setForbidden(self, name, value):
        dict.__setitem__(self, name, value)

    def __setitem__(self, name, value):
        if name in self.__forbidden:
            raise UsageError('%s cannot be assigned; it is either a command '
                             'or a device' % name)
        dict.__setitem__(self, name, value)

    def __delitem__(self, name):
        if name in self.__forbidden:
            raise UsageError('%s cannot be deleted; it is either a command '
                             'or a device' % name)
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


class NicosCompleter(object):
    """
    This is a custom version of rlcompleter.Completer that doesn't show private
    attributes when completing attribute access.

    There is not enough shared code left with the rlcompleter version to
    warrant inheriting from that class.
    """

    attr_hidden = set(['attached_devices', 'parameters', 'hardware_access',
                       'temporary', 'log', 'valuetype', 'mro'])
    global_hidden = set(['basestring', 'buffer', 'bytearray', 'bytes',
                         'callable', 'classmethod', 'coerce', 'cmp', 'compile',
                         'delattr', 'eval', 'execfile', 'filter', 'frozenset',
                         'getattr', 'globals', 'hasattr', 'hash', 'id',
                         'input', 'intern', 'isinstance', 'issubclass', 'iter',
                         'locals', 'long', 'map', 'memoryview', 'property',
                         'raw_input', 'reduce', 'reload', 'setattr', 'slice',
                         'staticmethod', 'super', 'unichr', 'unicode', 'type',
                         'vars', 'xrange']) | BUILTIN_EXCEPTIONS
    hidden_keyword = set(['assert', 'class', 'del', 'exec', 'yield'])
    special_device = set(['move', 'drive', 'maw', 'switch', 'wait', 'read',
                          'status', 'stop', 'reset', 'set', 'get', 'fix',
                          'release', 'adjust', 'version', 'history', 'limits',
                          'resetlimits', 'ListParams', 'ListMethods',
                          'scan', 'cscan', 'contscan'])
    special_readable = set(['read', 'status', 'reset', 'history'])
    special_moveable = set(['move', 'drive', 'maw', 'switch', 'wait', 'stop',
                            'fix', 'release', 'adjust', 'limits',
                            'resetlimits', 'scan', 'cscan', 'contscan'])
    special_setups = set(['NewSetup', 'AddSetup', 'RemoveSetup'])

    def __init__(self, namespace):
        self.namespace = namespace
        self.matches = []

    def _callable_postfix(self, val, word):
        if callable(val) and not isinstance(val, Device):
            word += '('
        return word

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        This is called successively with state == 0, 1, 2, ... until it
        returns None.  The completion should begin with 'text'.
        """
        if state == 0:
            if '.' in text:
                self.matches = self.attr_matches(text)
            else:
                self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    def attr_matches(self, text):
        """Compute matches when text contains a dot.

        Assuming the text is of the form NAME.NAME....[NAME], and is
        evaluatable in self.namespace, it will be evaluated and its attributes
        (as revealed by dir()) are used as possible completions.  (For class
        instances, class members are also considered.)
        """

        match = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        if not match:
            return []
        expr, attr = match.group(1, 3)
        try:
            thisobject = eval(expr, self.namespace)
        except Exception:
            return []

        # get the content of the object, except __builtins__
        words = dir(thisobject)
        if isinstance(thisobject, DeviceAlias):
            words.extend(dir(thisobject._obj))

        if '__builtins__' in words:
            words.remove('__builtins__')

        if hasattr(thisobject, '__class__'):
            words.append('__class__')
            words.extend(rlcompleter.get_class_members(thisobject.__class__))

        matches = []
        n = len(attr)
        for word in words:
            if word[:n] == attr and hasattr(thisobject, word):
                val = getattr(thisobject, word)
                word = self._callable_postfix(val, '%s.%s' % (expr, word))
                matches.append(word)
        textlen = len(text)
        return [m for m in matches if not (m[textlen:].startswith(('_', 'do'))
                                           or m[textlen:] in self.attr_hidden)]

    def global_matches(self, text, line=None):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace that match.
        """
        if line is None:
            line = readline and readline.get_line_buffer() or ''
        if '(' in line:
            command = line[:line.index('(')].lstrip()
            if command in self.special_device:
                from nicos.core import Device, Readable, Moveable
                if command in self.special_moveable:
                    cls = Moveable
                elif command in self.special_readable:
                    cls = Readable
                else:
                    cls = Device
                return [k for k in session.explicit_devices if
                        k.startswith(text) and
                        isinstance(session.devices[k], cls)]
            elif command in self.special_setups:
                all_setups = [name for (name, info) in iteritems(session._setup_info)
                              if info and info['group'] in ('basic',
                                                            'optional',
                                                            'plugplay',
                                                            '')]
                if command == 'NewSetup':
                    candidates = all_setups
                elif command == 'AddSetup':
                    candidates = [setup for setup in all_setups
                                  if setup not in session.explicit_setups]
                else:
                    candidates = session.explicit_setups
                candidates = list(map(repr, candidates))
                if line.endswith('('):
                    return candidates
                return [c[1:-1] for c in candidates if c[1:].startswith(text)]
            elif command == 'SetMode':
                candidates = list(map(repr, EXECUTIONMODES))
                if line.endswith('('):
                    return candidates
                return [c[1:-1] for c in candidates if c[1:].startswith(text)]
        matches = []
        n = len(text)
        for word in keyword.kwlist:
            if word[:n] == text and word not in self.hidden_keyword:
                matches.append(word)
        for nspace in [builtins.__dict__, self.namespace]:
            for word, val in nspace.items():
                if word[:n] == text and word != '__builtins__':
                    matches.append(self._callable_postfix(val, word))
        return [m for m in matches if m[:-1] not in self.global_hidden]

    def get_matches(self, text, line=None):
        if '.' in text:
            return self.attr_matches(text)
        else:
            return self.global_matches(text, line)


class LoggingStdout(object):
    """
    Standard output stream replacement that tees output to a logger.
    """

    def __init__(self, orig_stdout):
        self.orig_stdout = orig_stdout

    def write(self, text):
        if text.strip():
            session.log.info(text)
        try:
            self.orig_stdout.write(text)
        except UnicodeEncodeError:
            self.orig_stdout.write(text.encode('utf-8'))

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


def sessionInfo(sid):
    """Return a string with information gathered from the session id."""
    pid, rest = sid.split('@')
    host, timestamp = rest.rsplit('-', 1)
    return 'PID %s on host %s, started on %s' % (
        pid, host, time.asctime(time.localtime(int(timestamp))))


# command guessing

def guessCorrectCommand(source, attribute=False):
    """Try to guess the command that was meant by *source*.

    Will do a fuzzy match in all usercommands in the top level namespace and
    tries to find attributes if *attribute* is true.
    """
    if source is None:
        return

    from nicos.utils.comparestrings import compare
    try:
        # extract the first dotted item on the line
        match = re.match('[a-zA-Z_][a-zA-Z0-9_.]*', source)
        if match is None:
            return
        object_parts = match.group(0).split('.')
        if attribute and len(object_parts) < 2:
            return

        # compile a list of existing commands
        allowed_keys = set([x for x in session._exported_names
                            if hasattr(session.namespace[x], 'is_usercommand')])
        allowed_keys.update(__builtins__)
        allowed_keys -= NicosCompleter.global_hidden
        allowed_keys.update(session.namespace)
        # for attributes, use a list of existing attributes instead
        if attribute:
            obj = None
            if object_parts[0] in session.namespace:
                obj = session.namespace.globals[object_parts[0]]
            for i in range(1, len(object_parts)):
                try:
                    obj = getattr(obj, object_parts[i])
                except AttributeError:
                    base = '.'.join(object_parts[:i])
                    poi = object_parts[i]
                    allowed_keys = set(dir(obj))
                    break
            else:
                # whole object chain exists -- error comes from somewhere else
                return
        else:
            base = ''
            poi = object_parts[0]

        # compare all allowed keys against given
        comp = {}

        if attribute:
            poi = object_parts[1]
        else:
            poi = object_parts[0]
            if poi in session.configured_devices:
                if poi in session.devices:
                    session.log.info('Use CreateDevice(%r) to export the '
                                     'device of this name', str(poi))
                else:
                    session.log.info('Use CreateDevice(%r) to try creating '
                                     'the device of this name', str(poi))
                return
        for key in allowed_keys:
            if key == poi:
                # the error probably occurred with another object on the line
                return
            comp[key] = compare(poi, key)
        comp = sorted(comp.items(), key=lambda t: t[1], reverse=True)
        suggestions = [(base and base + '.' or '') + m[0]
                       for m in comp[:3] if m[1] > 2]
        if suggestions:
            session.log.info('Did you mean: %s', ', '.join(suggestions))
    except Exception:
        pass


class AttributeRaiser(object):
    """Class that raises an exception on attribute access."""

    def __init__(self, excls, exmsg):
        self.__dict__['excls'] = excls
        self.__dict__['exmsg'] = exmsg

    def __getattr__(self, key):
        raise self.excls(self.exmsg)

    def __setattr__(self, key, value):
        raise self.excls(self.exmsg)

    def __delattr__(self, key):
        raise self.excls(self.exmsg)

    def __nonzero__(self):
        return False

    __bool__ = __nonzero__
