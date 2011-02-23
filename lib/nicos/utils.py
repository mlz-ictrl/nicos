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

"""Utilities for the other methods."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import re
import grp
import pwd
import sys
import copy
import time
import errno
import signal
import socket
import linecache
import traceback
import ConfigParser

from nicos.errors import ConfigurationError, ProgrammingError, ModeError


class Param(object):
    """
    This class defines the properties of a device parameter.

    Attributes (and constructor arguments):

    - *description*: a concise parameter description
    - *type*: the parameter type; better a conversion function that either
      returns a value of the correct type, or raises TypeError or ValueError.
    - *default*: a default value, in case the parameter cannot be read from
      the hardware or the cache
    - *mandatory*: if the parameter must be given in the config file
    - *settable*: if the parameter can be set after startup
    - *unit*: unit of the parameter for informational purposes; 'main' is
      replaced by the device unit when presented
    - *category*: category of the parameter when returned by device.info()
      or None to ignore the parameter
    - *preinit*: whether the parameter must be initialized before preinit()
    """

    _notset = object()

    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, unit=None, category=None,
                 preinit=False):
        self.type = type
        if default is self._notset:
            default = type()
        self.default = default
        self.mandatory = mandatory
        self.settable = settable
        self.unit = unit
        self.category = category
        self.description = description
        self.preinit = preinit

    def __repr__(self):
        return '<Param info>'


class Override(object):

    def __init__(self, **kw):
        self._kw = kw

    def apply(self, paraminfo):
        newinfo = copy.copy(paraminfo)
        for attr in self._kw:
            setattr(newinfo, attr, self._kw[attr])
        return newinfo


class MergedAttrsMeta(type):
    """
    A metaclass that allows defining dictionaries as class attributes that are
    automatically merged with those of any ancestors.

    Consider a class hierarchy like the following:

        class Root:
            __metaclass__ = MergedAttrsMeta
            __mergedattrs__ = ['test']

            test = {'attr1': 'arbitrary value'}

        class Child(Root):
            test = {'attr2': 'arbitrary value'}

        class Grandchild(Child):
            test = {'attr3': 'arbitrary value'}

    Now, Grandchild.test is a dictionary with all the keys defined by itself
    and any of its parents, i.e. 'attr1', 'attr2' and 'attr3'.

    Note that the subclasses don't have to set the __metaclass__, it is
    automatically "inherited" from Root.
    """

    def __new__(mcs, name, bases, attrs):
        newtype = type.__new__(mcs, name, bases, attrs)
        for entry in newtype.__mergedattrs__:
            newentry = {}
            for base in reversed(bases):
                if hasattr(base, entry):
                    newentry.update(getattr(base, entry))
            newentry.update(attrs.get(entry, {}))
            setattr(newtype, entry, newentry)
        return newtype


class AutoPropsMeta(MergedAttrsMeta):
    """
    A metaclass that automatically adds properties for the class'
    parameters.
    """

    def __new__(mcs, name, bases, attrs):
        newtype = MergedAttrsMeta.__new__(mcs, name, bases, attrs)
        for param, info in newtype.parameters.iteritems():
            # parameter names are always lowercased
            param = param.lower()
            if not isinstance(info, Param):
                raise ProgrammingError('%r device %r parameter info should be '
                                       'a Param object' % (name, param))

            # process overrides
            override = newtype.parameter_overrides.get(param)
            if override:
                info = newtype.parameters[param] = override.apply(info)

            # create the getter method
            def getter(self, param=param):
                if self._mode == 'simulation':
                    return self._params[param]
                if self._cache:
                    value = self._cache.get(self, param)
                    if value is not None:
                        self._params[param] = value
                        return value
                self._initParam(param)
                return self._params[param]

            # create the setter method
            if not info.settable:
                def setter(self, value, param=param):
                    raise ConfigurationError(
                        self, 'cannot set the %s parameter' % param)
            else:
                wmethodname = 'doWrite' + param.title()
                if getattr(newtype, wmethodname, None) is None:
                    wmethodname = None
                def setter(self, value, param=param, methodname=wmethodname):
                    pconv = self.parameters[param].type
                    try:
                        value = pconv(value)
                    except (ValueError, TypeError), err:
                        raise ConfigurationError(
                            self, '%r is an invalid value for parameter '
                            '%s: %s' % (value, param, err))
                    if self._mode == 'slave':
                        raise ModeError('setting parameter %s not possible in '
                                        'slave mode' % param)
                    elif self._mode == 'simulation':
                        self._params[param] = value
                        return
                    if methodname:
                        # allow doWrite to override the value
                        rv = getattr(self, methodname)(value)
                        if rv is not None:
                            value = rv
                    self._params[param] = value
                    if self._cache:
                        self._cache.put(self, param, value)
                    self._changedparams.add(param)

            # create a property and attach to the new device class
            setattr(newtype, param,
                    property(getter, setter, doc=info.description))
        del newtype.parameter_overrides
        return newtype


def formatDocstring(s, indentation=''):
    """Format a docstring for display on the console."""
    lines = s.expandtabs().splitlines()
    # Find minimum indentation of any non-blank lines after first line.
    margin = sys.maxint
    for line in lines[1:]:
        content = len(line.lstrip())
        if content:
            indent = len(line) - content
            margin = min(margin, indent)
    # Add uniform indentation.
    if lines:
        lines[0] = indentation + lines[0].lstrip()
    if margin == sys.maxint:
        margin = 0
    for i in range(1, len(lines)):
        lines[i] = indentation + lines[i][margin:]
    # Remove any leading blank lines.
    while lines and not lines[0]:
        del lines[0]
    # Remove any trailing blank lines.
    while lines and not lines[-1].strip():
        del lines[-1]
    return '\n'.join(lines)


def printTable(headers, items, printfunc):
    """Print tabular information nicely formatted."""
    if not headers and not items:
        return
    ncolumns = len(headers or items[0])
    rowlens = [0] * ncolumns
    for row in [headers] + items:
        for i, item in enumerate(row):
            rowlens[i] = max(rowlens[i], len(item))
    fmtstr = ('%%-%ds  ' * ncolumns) % tuple(rowlens)
    printfunc(fmtstr % tuple(headers))
    printfunc(fmtstr % tuple('=' * l for l in rowlens))
    for row in items:
        printfunc(fmtstr % tuple(row))


def getVersions(object):
    """Return SVN Revision info for all modules where one of the object's
    class and base classes are in.
    """
    versions = []
    modules = set()
    def _add(cls):
        try:
            if cls.__module__ not in modules:
                ver = sys.modules[cls.__module__].__version__
                ver = ver.strip('$ ').replace('Revision: ', 'Rev. ')
                versions.append((cls.__module__, ver))
            modules.add(cls.__module__)
        except Exception:
            pass
        for base in cls.__bases__:
            _add(base)
    _add(object.__class__)
    return versions


# read nicos.conf files

class NicosConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, key):
        return key

def readConfig(*filenames):
    cfg = NicosConfigParser()
    cfg.read(filenames)
    if cfg.has_section('environment'):
        for name in cfg.options('environment'):
            value = cfg.get('environment', name)
            if name == 'PYTHONPATH':
                # needs to be special-cased
                sys.path.extend(value.split(':'))
            else:
                os.environ[name] = value
    from nicos.sessions import Session
    if cfg.has_section('nicos'):
        for option in cfg.options('nicos'):
            setattr(Session.config, option, cfg.get('nicos', option))


# simple file operations

def readFile(filename):
    fp = open(filename, 'rb')
    try:
        return map(str.strip, fp)
    finally:
        fp.close()

def writeFile(filename, lines):
    fp = open(filename, 'wb')
    try:
        fp.writelines(lines)
    finally:
        fp.close()

def writePidfile(appname):
    from nicos.sessions import Session
    filename = os.path.join(Session.config.control_path, 'pid', appname + '.pid')
    writeFile(filename, [str(os.getpid())])

def removePidfile(appname):
    from nicos.sessions import Session
    filename = os.path.join(Session.config.control_path, 'pid', appname + '.pid')
    try:
        os.unlink(filename)
    except OSError, err:
        if err.errno == errno.ENOENT:
            return
        raise

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


# daemonizing processes

def daemonize():
    """Daemonize the current process."""
    # finish up with the current stdout/stderr
    sys.stdout.flush()
    sys.stderr.flush()

    # do first fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.stdout.close()
            sys.exit(0)
    except OSError, err:
        print >>sys.stderr, 'fork #1 failed:', err
        sys.exit(1)

    # decouple from parent environment
    os.chdir('/')
    os.umask(0002)
    os.setsid()

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.stdout.close()
            sys.exit(0)
    except OSError, err:
        print >>sys.stderr, 'fork #2 failed:', err

    # now I am a daemon!
    from nicos.sessions import Session

    # switch user
    user, group = Session.config.user, Session.config.group
    if group:
        group = grp.getgrnam(group).gr_gid
        os.setegid(group)
    if Session.config.user:
        user = pwd.getpwnam(user).pw_uid
        os.seteuid(user)
        if 'HOME' in os.environ:
            os.environ['HOME'] = pwd.getpwuid(user).pw_dir

    # close standard fds, so that child processes don't inherit them even though
    # we override Python-level stdio
    os.close(0)
    os.close(1)
    os.close(2)

    # redirect standard file descriptors
    sys.stdin = open('/dev/null', 'r')
    sys.stdout = sys.stderr = open('/dev/null', 'w')


# console color utils

_codes = {}

_attrs = {
    'reset':     '39;49;00m',
    'bold':      '01m',
    'faint':     '02m',
    'standout':  '03m',
    'underline': '04m',
    'blink':     '05m',
}

for _name, _value in _attrs.items():
    _codes[_name] = '\x1b[' + _value

_colors = [
    ('black',     'darkgray'),
    ('darkred',   'red'),
    ('darkgreen', 'green'),
    ('brown',     'yellow'),
    ('darkblue',  'blue'),
    ('purple',    'fuchsia'),
    ('turquoise', 'teal'),
    ('lightgray', 'white'),
]

for _i, (_dark, _light) in enumerate(_colors):
    _codes[_dark] = '\x1b[%im' % (_i+30)
    _codes[_light] = '\x1b[%i;01m' % (_i+30)

def colorize(name, text):
    return _codes.get(name, '') + text + _codes.get('reset', '')

def colorcode(name):
    return _codes.get(name, '')


# nice formatting for an exit status

def whyExited(status):
    if os.WIFSIGNALED(status):
        signum = os.WTERMSIG(status)
        try:
            signame = [name for name in dir(signal) if name.startswith('SIG')
                       and getattr(signal, name) == signum][0]
        except IndexError:
            signame = 'signal %d' % signum
        return signame
    else:
        return 'exit code %d' % os.WEXITSTATUS(status)


# traceback utilities

def formatExtendedFrame(frame):
    ret = []
    for key, value in frame.f_locals.iteritems():
        try:
            valstr = repr(value)
        except Exception:
            valstr = '<cannot be displayed>'
        ret.append('        %-20s = %s\n' % (key, valstr))
    ret.append('\n')
    return ret

def formatExtendedTraceback(etype, value, tb):
    ret = ['Traceback (most recent call last):\n']
    while tb is not None:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        item = '  File "%s", line %d, in %s\n' % (filename, tb.tb_lineno,
                                                  frame.f_code.co_name)
        linecache.checkcache(filename)
        line = linecache.getline(filename, tb.tb_lineno, frame.f_globals)
        if line:
            item = item + '    %s\n' % line.strip()
        ret.append(item)
        if filename != '<script>':
            ret += formatExtendedFrame(tb.tb_frame)
        tb = tb.tb_next
    ret += traceback.format_exception_only(etype, value)
    return ''.join(ret).rstrip('\n')


# parameter conversion functions

_notset = object()

def listof(conv):
    def converter(val=[]):
        if not isinstance(val, list):
            raise ValueError('value needs to be a list')
        return map(conv, val)
    return converter

def tupleof(*types):
    def converter(val=None):
        if val is None:
            return tuple(type() for type in types)
        if not isinstance(val, (list, tuple)) or not len(types) == len(val):
            raise ValueError('value needs to be a %d-tuple' % len(types))
        return tuple(t(v) for (t, v) in zip(types, val))
    return converter

def dictof(keyconv, valconv):
    def converter(val={}):
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in val.iteritems():
            ret[keyconv(k)] = valconv(v)
        return ret
    return converter

tacodev_re = re.compile(r'^(//[\w.]+/)?\w+/\w+/\w+$', re.I)

def tacodev(val=None):
    if val is None:
        return ''
    val = str(val)
    if not tacodev_re.match(val):
        raise ValueError('%s is not a valid Taco device name' % val)
    return val

def any(val=None):
    return val

def vec3(val=[0,0,0]):
    ret = map(float, val)
    if len(ret) != 3:
        raise ValueError('value needs to be a 3-element vector')
    return ret

def intrange(fr, to):
    def converter(val=fr):
        val = int(val)
        if not fr <= val < to:
            raise ValueError('value needs to fulfill %d <= x < %d' % (fr, to))
        return val
    return converter

def floatrange(fr, to):
    def converter(val=fr):
        val = float(val)
        if not fr <= val < to:
            raise ValueError('value needs to fulfill %d <= x < %d' % (fr, to))
        return val
    return converter

def oneof(conv, *vals):
    def converter(val=vals[0]):
        val = conv(val)
        if val not in vals:
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(vals)))
        return val
    return converter

def existingdir(val='.'):
    val = str(val)
    if not os.path.isdir(val):
        raise ValueError('value %s is not an existing directory' % val)
    return val
