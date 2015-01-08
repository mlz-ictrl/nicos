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

"""
SPM (Simple Parameter Mode) is an alternate command input mode for NICOS where
entering Python code is not required.

The syntax is very simple and allows no variables, loops or conditionals: a
command line consists of a command and optional arguments, separated by spaces.

Arguments can be numbers, device names, strings and symbols (words that signify
a command option).  Strings can be quoted or unquoted.

Examples::

    read
    move a1 180
    scan sth 10.4 0.4 25 t 2
"""

# XXX SPM todos:
# * figure out how to convert code examples in docstrings
# * add a way to make commands unavailable (e.g. manualscan)

import re
from itertools import chain, cycle, islice

from nicos.core import Device, SPMError
from nicos.pycompat import iteritems, srepr


id_re = re.compile('[a-zA-Z_][a-zA-Z0-9_]*$')
string1_re = re.compile(r"'(\\\\|\\'|[^'])*'")
string2_re = re.compile(r'"(\\\\|\\"|[^"])*"')
spaces_re  = re.compile(r'\s+')
nospace_re = re.compile(r'[^ \t;]+')


def spmsyntax(*arguments, **options):
    """Decorator to give a function specific SPM syntax advice, for parameter
    checking and completion.
    """
    def deco(func):
        func.spmsyntax = arguments, options
        return func
    return deco


class bare(str):
    """String that repr()s as itself without quotes."""
    def __repr__(self):
        return self


class NoParse(Exception):
    def __init__(self, expected, token):
        Exception.__init__(self, expected, token)
        self.token = token
        self.expected = expected


class Token(object):
    desc = 'token'

    def handle(self, arg, session):
        raise NoParse('strange token', arg)

    def complete(self, text, session, argsofar):
        return []


class String(Token):
    desc = 'string'

    def handle(self, arg, session):
        if string1_re.match(arg) or string2_re.match(arg):
            return bare(arg)
        return arg

String = String()


class Bare(Token):
    desc = 'value'

    def handle(self, arg, session):
        if id_re.match(arg):
            if arg not in session.namespace and \
               arg not in session.local_namespace:
                return arg
        return bare('(' + arg + ')')

Bare = Bare()


class Num(Token):
    desc = 'number'

    def handle(self, arg, session):
        try:
            return float(arg)
        except ValueError:
            raise NoParse('number', arg)

Num = Num()


class Int(Token):
    desc = 'integer'

    def handle(self, arg, session):
        try:
            return int(arg)
        except ValueError:
            raise NoParse('integer', arg)

Int = Int()


class Oneof(Token):
    def __init__(self, *choices):
        self.choices = choices

    @property
    def desc(self):
        return 'one of ' + ', '.join(self.choices)

    def handle(self, arg, session):
        if arg.lower() not in self.choices:
            raise NoParse(self.desc, arg)
        return arg.lower()

    def complete(self, text, session, argsofar):
        return [c for c in self.choices if c.startswith(text)]


class Bool(Token):
    desc = 'boolean'

    def handle(self, arg, session):
        if arg.lower() not in ['true', 'false']:
            raise NoParse('true or false', arg)
        return bare(arg.capitalize())

    def complete(self, text, session, argsofar):
        return [c for c in ['true', 'false'] if c.startswith(text)]

Bool = Bool()


class Dev(Token):
    desc = 'device name'

    def __init__(self, devtype=Device):
        self.devtype = devtype

    def clsrep(self, cls):
        if isinstance(cls, tuple):
            return ' or '.join(self.clsrep(c) for c in cls)
        return cls.__name__

    def handle(self, arg, session):
        if arg not in session.explicit_devices:
            raise NoParse('device name', arg)
        if not isinstance(session.devices[arg], self.devtype):
            raise NoParse('%s device' % self.clsrep(self.devtype), arg)
        return bare(arg)

    def complete(self, text, session, argsofar):
        return [dev for dev in session.explicit_devices if dev.startswith(text)
                and isinstance(session.devices[dev], self.devtype)]

AnyDev = Dev()


class DevParam(Token):
    desc = 'parameter name'

    def handle(self, arg, session):
        return arg

    def complete(self, text, session, argsofar):
        try:
            dev = session.getDevice(argsofar[-2])
            return [p for p in dev.parameters if p.startswith(text)]
        except Exception:
            return []

DevParam = DevParam()


class SetupName(Token):
    desc = 'setup name'

    def __init__(self, what):
        self.what = what

    def handle(self, arg, session):
        if arg not in session._setup_info:
            raise NoParse('setup name', arg)
        return arg

    def complete(self, text, session, argsofar):
        all_setups = [name for (name, info) in iteritems(session._setup_info)
                      if info and info['group'] in ('basic', 'optional', '')]
        if self.what == 'all':
            candidates = all_setups
        elif self.what == 'unloaded':
            candidates = [setup for setup in all_setups
                          if setup not in session.explicit_setups]
        elif self.what == 'loaded':
            candidates = session.explicit_setups
        return [c for c in candidates if c.startswith(text)]


class DeviceName(Token):
    desc = 'device name'

    def handle(self, arg, session):
        if arg not in session.configured_devices:
            raise NoParse('device name', arg)
        return arg

    def complete(self, text, session, argsofar):
        return [c for c in session.configured_devices
                if c.startswith(text) and
                c not in session.devices and not
                session.configured_devices[c][1].get('lowlevel')]

DeviceName = DeviceName()


class Multi(object):
    def __init__(self, *types):
        self.types = types


class SPMHandler(object):
    """The main handler for SPM commands."""

    def __init__(self, session):
        self.session = session

    def error(self, msg):
        raise SPMError(msg)

    def complete(self, command, word):
        def select(candidates, word):
            return [c for c in candidates if c.startswith(word)]
        try:
            # XXX could complete "?" too
            if command.startswith(('!', '?')) or command.endswith('?'):
                return []
            if command.startswith(':'):
                return self.complete(command[1:].strip(), word)
            commands = self.tokenize(command, partial=True)
            tokens = commands[-1]  # only last command is interesting
            if not word:
                tokens.append('')
            command = tokens[0]
            if len(tokens) == 1:
                # complete command
                return select([n for (n, o) in iteritems(self.session.namespace)
                               if hasattr(o, 'is_usercommand') or
                               isinstance(o, Device)], word)
            cmdobj = self.session.namespace.get(command)
            if isinstance(cmdobj, Device):
                return []
            if not hasattr(cmdobj, 'is_usercommand'):
                return []
            return self.complete_command(cmdobj, tokens[1:], word)
        except Exception as err:
            self.session.log.debug('error during completion: %s' % err)
            return []

    def complete_command(self, command, args, word):
        syntax = getattr(command, 'spmsyntax', None)
        if syntax is None:
            return []
        arguments, options = syntax
        posargs = len(arguments)
        multargs = 0
        if arguments and isinstance(arguments[-1], Multi):
            multargs = len(arguments[-1].types)
            posargs -= 1
            arguments = chain(arguments[:-1], cycle(arguments[-1].types))
        # assume we're completing the last word on the command line
        if multargs or len(args) <= posargs:
            # is it a positional argument
            el = next(islice(arguments, len(args)-1, len(args)))
            return el.complete(word, self.session, args)
        else:
            # must be an option
            which = (len(args) - posargs) % 2
            if which == 1:
                # option name
                return [n for n in options if n.startswith(word)]
            else:
                # option value
                optname = args[-2]
                if optname in options:
                    return options[optname].complete(word, self.session, args)
                return []

    def handle_script(self, code, fn):
        lines = []
        for lineno, command in enumerate(code.splitlines()):
            try:
                lines.append(self.handle_line(command))
            except SPMError as err:
                err.args = ('in %s, line %d: ' % (fn or 'unnamed',
                                                  lineno + 1) + err.args[0],)
                raise
        return '\n'.join(lines)

    def handle_line(self, command):
        if command.startswith('#'):
            # Comments (only in script files)
            return 'pass'
        if command.startswith('!'):
            # Python escape
            return command[1:].strip()
        if command.startswith('?') or command.endswith('?'):
            # Help escape
            return 'help(%s)' % command.strip('?')
        if command.startswith(':'):
            # Simulation escape
            code = self.handle_line(command[1:])
            return 'sim(%r)' % code
        try:
            commands = self.tokenize(command)
        except NoParse as err:
            return self.error('could not parse starting at %s, expected %s' %
                              (srepr(err.token), err.expected))
        code = []
        for tokens in commands:
            if not tokens:
                code.append('pass')
                continue
            command = tokens[0]
            cmdobj = self.session.namespace.get(command)
            if hasattr(cmdobj, 'is_usercommand'):
                code.append(self.handle_command(cmdobj, tokens[1:]))
            elif isinstance(cmdobj, Device):
                code.append(self.handle_device(cmdobj, tokens[1:]))
            else:
                return self.error('no such command or device: %s' %
                                  srepr(command))
        return '; '.join(code)

    def tokenize(self, command, partial=False):
        rest = command
        commands = [[]]
        tokens = commands[0]
        while rest:
            if rest.startswith("'"):
                m = string1_re.match(rest)
                if not m:
                    if partial:
                        tokens.append(rest)
                        return tokens
                    raise NoParse('single-quoted string', rest)
                tokens.append(m.group())
                rest = rest[m.end():]
            elif rest.startswith('"'):
                m = string2_re.match(rest)
                if not m:
                    if partial:
                        tokens.append(rest)
                        return tokens
                    raise NoParse('double-quoted string', rest)
                tokens.append(m.group())
                rest = rest[m.end():]
            elif rest.startswith('('):
                i = 1
                while i < len(rest):
                    if rest[i] == ')':
                        break
                    i += 1
                else:
                    if partial:
                        tokens.append(rest)
                        return tokens
                    raise NoParse('closing parenthesis', rest)
                tokens.append(rest[:i+1])
                rest = rest[i+1:]
            elif rest.startswith('['):
                i = 1
                while i < len(rest):
                    if rest[i] == ']':
                        break
                    i += 1
                else:
                    if partial:
                        tokens.append(rest)
                        return tokens
                    raise NoParse('closing bracket', rest)
                tokens.append(rest[:i+1])
                rest = rest[i+1:]
            elif rest[0].isspace():
                m = spaces_re.match(rest)
                rest = rest[m.end():]
            elif rest.startswith(';'):
                # serial command execution
                commands.append([])
                tokens = commands[-1]
                rest = rest[1:]
            else:
                m = nospace_re.match(rest)
                tokens.append(m.group())
                rest = rest[m.end():]
        return commands

    def handle_device(self, device, args):
        if not args:
            return 'read(%s)' % device
        elif len(args) == 1:
            return 'maw(%s, %s)' % (device, args[0])
        return self.error('too many arguments for simple device command')

    def handle_command(self, command, args):
        syntax = getattr(command, 'spmsyntax', None)
        if syntax is None:
            syntax = ((Bare,) * len(args), {})
        arguments, options = syntax
        posargs = len(arguments)
        multargs = 1
        if arguments and isinstance(arguments[-1], Multi):
            multargs = len(arguments[-1].types)
            posargs -= 1
            arguments = chain(arguments[:-1], cycle(arguments[-1].types))
        # first, parse positional arguments (all must be given)
        cmdargs = []
        nargs = 0
        for element in arguments:
            if not args:
                if nargs < posargs or (nargs - posargs) % multargs != 0:
                    return self.error('premature end of command, expected %s'
                                      % element.desc)
                break
            try:
                parg = element.handle(args[0], self.session)
            except NoParse as err:
                return self.error('invalid argument at %s, expected %s' %
                                  (srepr(err.token), err.expected))
            cmdargs.append(parg)
            args = args[1:]
            nargs += 1
        # now come options
        cmdopts = {}
        if len(args) % 2:
            return self.error('too many arguments at %s, expected end of '
                              'command' % srepr(args[-1]))
        while args:
            opt, val = args[:2]
            args = args[2:]
            if not id_re.match(opt):
                return self.error('invalid syntax at %s, expected option name'
                                  % srepr(opt))
            if opt in options:
                try:
                    val = options[opt].handle(val, self.session)
                except NoParse as err:
                    return self.error('invalid argument at %s, expected %s' %
                                      (srepr(err.token), err.expected))
            else:
                val = bare(val)
            cmdopts[opt] = val
        # now nothing should be left
        return command.__name__ + '(*%s, **%s)' % (cmdargs, cmdopts)
