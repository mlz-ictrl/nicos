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

"""Utilities for the other methods."""

__version__ = "$Revision$"

import os
import re
import grp
import pwd
import sys
import time
import errno
import signal
import socket
import linecache
import threading
import traceback
import ConfigParser
from os import path


class lazy_property(object):
    """A property that calculates its value only once."""
    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, obj_class):
        if obj is None:
            return obj
        obj.__dict__[self.__name__] = self._func(obj)
        return obj.__dict__[self.__name__]


class Repeater(object):
    def __init__(self, obj):
        self.object = obj

    def __iter__(self):
        return self

    def next(self):
        return self.object

    def __len__(self):
        return 0

    def __getitem__(self, item):
        return self.object


class HardwareStub(object):
    """An object that denies all attribute access, used to prevent accidental
    hardware access in simulation mode.
    """

    def __init__(self, dev):
        self.dev = dev

    def __getattr__(self, name):
        from nicos.core import ProgrammingError
        raise ProgrammingError(self.dev, 'accessing hardware method %s in '
                               'simulation mode' % name)


def _s(n):
    return int(n), (n != 1 and 's' or '')

def formatDuration(secs):
    if 0 <= secs < 60:
        est = '%s second%s' % _s(secs)
    elif secs < 3600:
        est = '%s minute%s' % _s(secs // 60 + 1)
    elif secs < 86400:
        est = '%s hour%s, %s minute%s' % (_s(secs // 3600) +
                                          _s((secs % 3600) // 60))
    else:
        est = '%s day%s, %s hour%s' % (_s(secs // 86400) +
                                       _s((secs % 86400) // 3600))
    return est


def formatDocstring(s, indentation=''):
    """Format a docstring into lines for display on the console."""
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
    return lines


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


def getVersions(obj):
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
    _add(obj.__class__)
    return versions


def closeSocket(sock):
    """Do our best to close a socket."""
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except socket.error:
        pass
    try:
        sock.close()
    except socket.error:
        pass


def bitDescription(bits, *descriptions):
    """Return a description of a bit-wise value."""
    ret = []
    for desc in descriptions:
        if len(desc) == 2:
            yes, no = desc[1], None
        else:
            yes, no = desc[1:3]
        if bits & (1 << desc[0]):
            if yes:
                ret.append(yes)
        else:
            if no:
                ret.append(no)
    return ', '.join(ret)


def runAsync(func):
    def inner(*args, **kwargs):
        thr = threading.Thread(target=func, args=args, kwargs=kwargs)
        thr.setDaemon(True)
        thr.start()
    return inner


def parseDateString(s, enddate=False):
    """Parse a date/time string that can be formatted in different ways."""
    # first, formats with explicit date and time
    for fmt in ('%Y-%m-%d %H:%M:%S', '%y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M', '%y-%m-%d %H:%M'):
        try:
            return time.mktime(time.strptime(s, fmt))
        except ValueError:
            pass
    # formats with only date
    for fmt in ('%Y-%m-%d', '%y-%m-%d'):
        try:
            ts = time.mktime(time.strptime(s, fmt))
        except ValueError:
            pass
        else:
            # if the date is the end of an interval, we want the interval
            # to end at the next midnight
            return enddate and ts + 86400 or ts
    # formats with only time
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            parsed = time.strptime(s, fmt)
        except ValueError:
            pass
        else:
            ltime = time.localtime()
            return time.mktime(ltime[:3] + parsed[3:6] + ltime[6:])
    raise ValueError('the given string is not a date/time string')


# read nicos.conf files

class NicosConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, key):
        return key

def readConfig():
    fn = path.normpath(path.join(path.dirname(__file__),
                                 '../../../nicos.conf'))
    cfg = NicosConfigParser()
    cfg.read(fn)
    if cfg.has_section('environment'):
        for name in cfg.options('environment'):
            value = cfg.get('environment', name)
            if name == 'PYTHONPATH':
                # needs to be special-cased
                sys.path[:0] = value.split(':')
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
    filename = os.path.join(Session.config.control_path, 'pid', appname+'.pid')
    writeFile(filename, [str(os.getpid())])

def removePidfile(appname):
    from nicos.sessions import Session
    filename = os.path.join(Session.config.control_path, 'pid', appname+'.pid')
    try:
        os.unlink(filename)
    except OSError, err:
        if err.errno == errno.ENOENT:
            return
        raise

def ensureDirectory(dirname):
    """Make sure a directory exists."""
    if not path.isdir(dirname):
        os.makedirs(dirname)

def disableDirectory(startdir):
    """Traverse a directory tree and remove access rights."""
    # handle files first, then subdirs and then work on the current dir
    assert path.isdir(startdir)
    for child in os.listdir(startdir):
        full = path.join(startdir, child)
        if path.isdir(full):
            disableDirectory(full)
        else:
            os.chmod(full, 0)
    os.chmod(startdir, 0)

def enableDirectory(startdir):
    """Traverse a directory tree and grant access rights."""
    assert path.isdir(startdir)
    os.chmod(startdir, 0755)  # drwxr-xr-x
    for child in os.listdir(startdir):
        full = path.join(startdir, child)
        if path.isdir(full):
            enableDirectory(full)
        else:
            os.chmod(full, 0644)  # drw-r--r--

field_re = re.compile('{{(?P<key>[^:#}]+)(?::(?P<default>[^#}]*))?'
                      '(?:#(?P<description>[^}]+))?}}')

def expandTemplate(template, keywords, field_re=field_re):
    """Simple template field replacement engine."""
    result = []
    current = 0
    missing = []
    defaulted = []
    for field in field_re.finditer(template):
        result.append(template[current:field.start()])
        replacement = keywords.get(field.group('key'))
        if replacement is None:
            replacement = field.group('default')
            if replacement is None:
                missing.append(field.groupdict())
                replacement = ''
            else:
                defaulted.append(field.groupdict())
        result.append(replacement)
        current = field.end()
    result.append(template[current:])
    return ''.join(result), defaulted, missing


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
        print >> sys.stderr, 'fork #1 failed:', err
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
        print >> sys.stderr, 'fork #2 failed:', err

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

def setuser():
    """Do not daemonize, but at least set the current user and group correctly
    to the configured values if started as root.
    """
    if os.geteuid() != 0:
        return
    # switch user
    from nicos.sessions import Session
    user, group = Session.config.user, Session.config.group
    if group:
        group = grp.getgrnam(group).gr_gid
        os.setegid(group)
    if Session.config.user:
        user = pwd.getpwnam(user).pw_uid
        os.seteuid(user)
        if 'HOME' in os.environ:
            os.environ['HOME'] = pwd.getpwuid(user).pw_dir


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

def nocolor():
    for key in _codes.keys():
        _codes[key] = ''


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
            valstr = repr(value)[:256]
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

def formatExtendedStack(level=1):
    f = sys._getframe(level)
    ret = ['Stack trace (most recent call last):\n\n']
    while f is not None:
        lineno = f.f_lineno
        co = f.f_code
        filename = co.co_filename
        name = co.co_name
        item = '  File "%s", line %d, in %s\n' % (filename, lineno, name)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            item = item + '    %s\n' % line.strip()
        ret.insert(1, item)
        if filename != '<script>':
            ret[2:2] = formatExtendedFrame(f)
        f = f.f_back
    return ''.join(ret).rstrip('\n')


# file counter utilities

def readFileCounter(counterpath):
    try:
        currentcounter = int(readFile(counterpath)[0])
    except IOError, err:
        # if the file doesn't exist yet, this is ok, but reraise all other
        # exceptions
        if err.errno == errno.ENOENT:
            currentcounter = 0
        else:
            raise
    return currentcounter

def updateFileCounter(counterpath, value):
    if not path.isdir(path.dirname(counterpath)):
        os.makedirs(path.dirname(counterpath))
    writeFile(counterpath, [str(value)])
