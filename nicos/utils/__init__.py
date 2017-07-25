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

"""Utilities for the other methods."""

from __future__ import print_function

import os
import re
import sys
import errno
import signal
import socket
import fnmatch
import linecache
import threading
import traceback
import subprocess
import unicodedata
from os import path
from stat import S_IRWXU, S_IRUSR, S_IWUSR, S_IXUSR, S_IRGRP, S_IXGRP, \
    S_IROTH, S_IXOTH
from time import time as currenttime, strftime, strptime, localtime, mktime, \
    sleep
from itertools import islice, chain
from functools import wraps
from collections import OrderedDict

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None

from nicos import config, nicos_version, custom_version, session
from nicos.pycompat import xrange as range  # pylint: disable=W0622
from nicos.pycompat import iteritems, string_types, text_type, exec_


def deprecated(since=nicos_version, comment=''):
    """This is a decorator which can be used to mark functions as deprecated.

    It will result in a warning being emitted when the function is used.

    The parameter ``since`` should contain the NICOS version number on which
    the deprecation starts.

    The ``comment`` should contain a hint to the user, what should be used
    instead.
    """
    def deco(f):
        msg = '%r is deprecated since version %r.' % (f.__name__, since)

        @wraps(f)
        def new_func(*args, **options):
            for l in [msg, comment]:
                session.log.warning(l)
            return f(*args, **options)
        new_func.__doc__ += ' %s %s' % (msg, comment)
        return new_func
    return deco


class attrdict(dict):
    """Dictionary whose items can be set with attribute access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class lc_dict(dict):
    """Dictionary with automatic lower-casing of keys."""
    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)

    def __delitem__(self, key):
        return dict.__delitem__(self, key.lower())


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


class readonlylist(list):
    def _no(self, *args, **kwds):
        raise TypeError('individual list values can not be changed')
    __delitem__ = __setitem__ = append = extend = insert = pop = remove = \
        reverse = sort = _no
    # NOTE: __iadd__ and __imul__ are good because their invocation is always
    # connected to a re-assignment

    def __getnewargs__(self):
        return (list(iter(self)),)

    def __hash__(self):
        return hash(tuple(self))


class readonlydict(dict):
    def _no(self, *args, **kwds):
        raise TypeError('individual dict values can not be changed')
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = \
        update = _no

    def __getnewargs__(self):
        return (dict(iteritems(self)),)

    def __reduce__(self):
        return dict.__reduce__(self)


class BoundedOrderedDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.maxlen = kwds.pop("maxlen", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._checklen()

    def __setitem__(self, key, value):  # pylint: disable=signature-differs
        OrderedDict.__setitem__(self, key, value)
        self._checklen()

    def _checklen(self):
        if self.maxlen is not None:
            while len(self) > self.maxlen:
                self.popitem(last=False)

    def getlast(self):
        (key, value) = self.popitem(last=True)
        self.__setitem__(key, value)
        return value


class AutoDefaultODict(OrderedDict):
    """Ordered dict that automatically creates values for missing keys as
    ordered dicts.

    Useful for creating hierarchical dicts.
    """
    def __missing__(self, key):
        val = self[key] = self.__class__()
        return val


class Repeater(object):
    def __init__(self, obj):
        self.object = obj

    def __iter__(self):
        return self

    def next(self):
        return self.object

    __next__ = next  # Python 3

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
    return int(n), (int(n) != 1 and 's' or '')


def formatDuration(secs, precise=True):
    if secs < 1:
        est = '< 1 second'
    elif 1 <= secs < 60:
        est = '%s second%s' % _s(secs + 0.5)
    elif secs < 3600:
        if precise:
            est = '%s min, %s sec' % (int(secs / 60.), int(secs % 60))
        else:
            est = '%s min' % int(secs / 60. + 0.5)
    elif secs < 86400:
        est = '%s h, %s min' % (int(secs / 3600.), int((secs % 3600) / 60. + 0.5))
    else:
        est = '%s day%s, %s h' % (_s(secs // 86400) +
                                  (int((secs % 86400) / 3600. + 0.5),))
    return est


def formatEndtime(secs):
    if secs > 60 * 60 * 24 * 7:
        return strftime('%A, %d %b %H:%M', localtime(currenttime() + secs))
    else:
        return strftime('%A, %H:%M', localtime(currenttime() + secs))


def formatDocstring(s, indentation=''):
    """Format a docstring into lines for display on the console."""
    lines = s.expandtabs().splitlines()
    # Find minimum indentation of any non-blank lines after first line.
    margin = sys.maxsize
    for line in lines[1:]:
        content = len(line.lstrip())
        if content:
            indent = len(line) - content
            margin = min(margin, indent)
    # Add uniform indentation.
    if lines:
        lines[0] = indentation + lines[0].lstrip()
    if margin == sys.maxsize:
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


def printTable(headers, items, printfunc, minlen=0):
    """Print tabular information nicely formatted."""
    if not headers and not items:
        return
    ncolumns = len(headers or items[0])
    rowlens = [minlen] * ncolumns
    for row in [headers or []] + items:
        for i, item in enumerate(row):
            rowlens[i] = max(rowlens[i], len(item))
    fmtstr = ('%%-%ds  ' * ncolumns) % tuple(rowlens)
    if headers:
        printfunc(fmtstr % tuple(headers))
        printfunc(fmtstr % tuple('=' * l for l in rowlens))
    for row in items:
        printfunc(fmtstr % tuple(row))


def getVersions(obj):
    """Return Revision info for all modules where one of the object's
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


def getSysInfo(service):
    """Query system information.

    Returns key suitable a cache key and
    a dict with path and version information.
    """
    host = getfqdn()
    res = dict(
        instrument=config.instrument,
        service=service,
        host=host,
        nicos_root=config.nicos_root,
        version=nicos_version,
        custom_path=config.custom_path,
        custom_version=custom_version,
    )
    nicosroot_key = config.nicos_root.replace('/', '_')
    key = 'sysinfo/%s/%s/%s' % (service, host, nicosroot_key)
    return key, res


def parseHostPort(host, defaultport):
    """Parse host[:port] string and tuples

    Specify 'host[:port]' or a (host, port) tuple for the mandatory argument.
    If the port specification is missing, the value of the defaultport is used.
    """

    if isinstance(host, (tuple, list)):
        host, port = host
    elif ':' in host:
        host, port = host.rsplit(':', 1)
        port = int(port)
    else:
        port = defaultport
    assert 0 < port < 65536
    assert ':' not in host
    return host, port


def tcpSocket(host, defaultport, timeout=None):
    """Helper for opening a TCP client socket to a remote server.

    Specify 'host[:port]' or a (host, port) tuple for the mandatory argument.
    If the port specification is missing, the value of the defaultport is used.
    If timeout is set to a number, the timout of the connection is set to this
    number, else the socket stays in blocking mode.
    """
    host, port = parseHostPort(host, defaultport)

    # open socket and set options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if timeout:
            s.settimeout(timeout)
    # connect
        s.connect((host, int(port)))
    except socket.error:
        closeSocket(s)
        raise
    return s


def closeSocket(sock, socket=socket):
    """Do our best to close a socket."""
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except socket.error:
        pass
    try:
        sock.close()
    except socket.error:
        pass


def getfqdn(name=''):
    """Get fully qualified hostname."""
    return socket.getfqdn(name)


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


def createThread(name, target, args=(), kwargs=None, daemon=True, start=True):
    """Create, start and return a Python thread."""
    thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
    thread.daemon = daemon
    if start:
        thread.start()
    return thread


def runAsync(func):
    """Decorator that runs the function in a thread when called."""
    def inner(*args, **kwargs):
        createThread('runAsync %s' % func, func, args=args)
    return inner


def createSubprocess(cmdline, **kwds):
    """Create a subprocess.Popen with the proper setting of close_fds."""
    if 'close_fds' not in kwds:
        # only supported on Posix and (Windows if not redirected)
        if os.name == 'posix' or not (kwds.get('stdin') or
                                      kwds.get('stdout') or
                                      kwds.get('stderr')):
            kwds['close_fds'] = True
    return subprocess.Popen(cmdline, **kwds)


def parseDateString(s, enddate=False):
    """Parse a date/time string that can be formatted in different ways."""
    # first, formats with explicit date and time
    for fmt in ('%Y-%m-%d %H:%M:%S', '%y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M', '%y-%m-%d %H:%M'):
        try:
            return mktime(strptime(s, fmt))
        except ValueError:
            pass
    # formats with only date
    for fmt in ('%Y-%m-%d', '%y-%m-%d'):
        try:
            ts = mktime(strptime(s, fmt))
        except ValueError:
            pass
        else:
            # if the date is the end of an interval, we want the interval
            # to end at the next midnight
            return enddate and ts + 86400 or ts
    # formats with only time
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            parsed = strptime(s, fmt)
        except ValueError:
            pass
        else:
            ltime = localtime()
            return mktime(ltime[:3] + parsed[3:6] + ltime[6:])
    # formats like "1 day" etc.
    rex = re.compile(r'^\s*(\d+(?:.\d+)?)\s*(\w+)\s*$')
    units = [
        (1, 'seconds', 'second', 'sec', 's'),
        (60, 'minutes', 'minute', 'min', 'm'),
        (3600, 'hours', 'hour', 'h'),
        (3600 * 24, 'days', 'day', 'd'),
        (3600 * 24 * 7, 'weeks', 'week', 'w'),
    ]
    m = rex.match(s)
    if m is not None:
        for u in units:
            if m.group(2) in u[1:]:
                return currenttime() - float(m.group(1)) * u[0]
    raise ValueError('the given string is not a date/time string')


def terminalSize():
    """Try to find the terminal size as (cols, rows)."""
    import struct
    import fcntl
    import termios
    try:
        h, w, _hp, _wp = struct.unpack(
            'HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                struct.pack('HHHH', 0, 0, 0, 0)))
    except IOError:
        return 80, 25
    return w, h


def parseConnectionString(s, defport):
    """Parse a string in the format 'user:pass@host:port"."""
    res = re.match(r"(?:(\w+)(?::([^@]*))?@)?([\w.-]+)(?::(\d+))?", s)
    if res is None:
        return None
    return {
        'user': res.group(1) or 'guest',
        'password': res.group(2),   # None if no password given
        'host': res.group(3),
        'port': int(res.group(4) or defport),
    }


def chunks(iterable, size):
    """Split an iterable in chunks."""
    sourceiter = iter(iterable)
    while True:
        chunkiter = islice(sourceiter, size)
        nextchunk = next(chunkiter, Ellipsis)
        if nextchunk is Ellipsis:
            return
        yield chain([nextchunk], chunkiter)


def importString(import_name, prefixes=()):
    """Imports an object based on a string.

    The string can be either a module name and an object name, separated
    by a colon, or a (potentially dotted) module name.
    """
    if ':' in import_name:
        modname, obj = import_name.split(':', 1)
    elif '.' in import_name:
        modname, obj = import_name.rsplit('.', 1)
    else:
        modname, obj = import_name, None
    mod = None
    fromlist = [obj] if obj else []
    errors = []
    for fullname in [modname] + [p + modname for p in prefixes]:
        try:
            mod = __import__(fullname, {}, {}, fromlist)
        except ImportError as err:
            errors.append('[%s] %s' % (fullname, err))
        else:
            break
    if mod is None:
        raise ImportError('Could not import %r: %s' %
                          (import_name, ', '.join(errors)))
    if not obj:
        return mod
    else:
        return getattr(mod, obj)


def safeFilename(fn):
    """Make a filename "safe", i.e. remove everything except alphanumerics."""
    return re.compile('[^a-zA-Z0-9_.-]').sub('', fn)


# simple file operations
#
# first constants, then functions
#
DEFAULT_DIR_MODE = S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH
DEFAULT_FILE_MODE = S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH


def readFile(filename):
    with open(filename, 'r') as fp:
        return [line.strip() for line in fp]


def writeFile(filename, lines):
    with open(filename, 'w') as fp:
        fp.writelines(lines)


def getPidfileName(appname):
    return os.path.join(config.nicos_root, config.pid_path, appname + '.pid')


def writePidfile(appname):
    writeFile(getPidfileName(appname), [str(os.getpid())])


def removePidfile(appname):
    try:
        os.unlink(getPidfileName(appname))
    except OSError as err:
        if err.errno == errno.ENOENT:
            return
        raise


def ensureDirectory(dirname, enableDirMode=DEFAULT_DIR_MODE, **kwargs):
    """Make sure a directory exists."""
    if not path.isdir(dirname):
        os.makedirs(dirname)
        os.chmod(dirname, enableDirMode)
        enableDirectory(dirname, enableDirMode, **kwargs)


def enableDisableFileItem(filepath, mode, owner=None, group=None, logger=None):
    """Set mode and maybe change uid/gid of a filesystem item."""
    if (owner or group) and pwd and hasattr(os, 'chown') and hasattr(os, 'stat'):
        stats = os.stat(filepath)  # only change the requested parts
        owner = owner or stats.st_uid
        group = group or stats.st_gid
        if isinstance(owner, string_types):
            owner = pwd.getpwnam(owner)[2]
        if isinstance(group, string_types):
            group = grp.getgrnam(group)[2]
        try:
            os.chown(filepath, owner, group)
        except OSError as e:
            if logger:
                logger.debug('chown(%r, %d, %d) failed: %s',
                             filepath, owner, group, e)
    try:
        os.chmod(filepath, mode)
    except OSError as e:
        if logger:
            logger.debug('chmod(%r, %o) failed: %s', filepath, mode, e)
        return True
    return False


def enableDisableDirectory(startdir, dirMode, fileMode,
                           owner=None, group=None, enable=False,
                           logger=None):
    """Traverse a directory tree and change access rights.

    Returns True if there were some errors and False if everything went OK.
    """
    if not path.isdir(startdir):
        return
    failflag = False

    # to enable, we have to handle 'our' directory first
    if enable:
        failflag |= enableDisableFileItem(startdir, dirMode, owner, group,
                                          logger)

    for root, dirs, files in os.walk(startdir, topdown=enable):
        for d in dirs:
            full = path.join(root, d)
            failflag |= enableDisableFileItem(full, dirMode, owner, group,
                                              logger)
        for f in files:
            full = path.join(root, f)
            failflag |= enableDisableFileItem(full, fileMode, owner, group,
                                              logger)

    # for disable, we have to close 'our' directory last
    if not enable:
        failflag |= enableDisableFileItem(startdir, dirMode, owner, group,
                                          logger)

    return failflag


def disableDirectory(startdir, disableDirMode=S_IRUSR | S_IXUSR,
                     disableFileMode=S_IRUSR, owner=None, group=None,
                     logger=None, **kwargs):  # kwargs eats unused args
    """Traverse a directory tree and remove access rights.

    Returns True if there were some errors and False if everything went OK.
    disableDirMode default to 0500 (dr-x------) and
    disableFileMode default to 0400 (-r--------).
    owner or group will only be changed if specified.
    """
    owner = kwargs.get("disableOwner", owner)
    group = kwargs.get("disableGroup", group)
    failflag = enableDisableDirectory(startdir,
                                      disableDirMode, disableFileMode,
                                      owner, group, enable=False, logger=logger)
    if failflag:
        if logger:
            logger.warning('Disabling failed for some files, please check '
                           'access rights manually')
    return failflag
    # maybe logging is better done in the caller of disableDirectory


def enableDirectory(startdir, enableDirMode=DEFAULT_DIR_MODE,
                    enableFileMode=DEFAULT_FILE_MODE, owner=None, group=None,
                    logger=None, **kwargs):  # kwargs eats unused args
    """Traverse a directory tree and grant access rights.

    Returns True if there were some errors and False if everything went OK.
    enableDirMode default to 0755 (drwxr-xr-x) and
    enableFileMode default to 0644 (-rw-r--r--).
    owner or group will only be changed if specified.
    """
    owner = kwargs.get("enableOwner", owner)
    group = kwargs.get("enableGroup", group)
    failflag = enableDisableDirectory(startdir,
                                      enableDirMode, enableFileMode,
                                      owner, group, enable=True, logger=logger)
    if failflag:
        if logger:
            logger.warning('Enabling failed for some files, please check '
                           'access rights manually')
    return failflag
    # maybe logging is better done in the caller of enableDirectory


field_re = re.compile('{{(?P<key>[^:#}]+)(?::(?P<default>[^#}]*))?'
                      '(?:#(?P<description>[^}]+))?}}')


def expandTemplate(template, keywords, field_re=field_re):
    """Simple template field replacement engine.

    Syntax is {{key:default#description}} where default and description
    are optional. The whole string is replaced by the value of the given
    dictionary item with the requested key. If this does not exist,
    default is used instead.

    Returns a ``tuple(<replaced string>, [missed keys where default was used],
    [list of missing keys without default])``.
    Each list item is a dictionary with three keys:
    key, default and description.
    """
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
    except OSError as err:
        print('fork #1 failed:', err, file=sys.stderr)
        sys.exit(1)

    # decouple from parent environment
    os.chdir('/')
    os.umask(0o002)
    os.setsid()

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.stdout.close()
            sys.exit(0)
    except OSError as err:
        print('fork #2 failed:', err, file=sys.stderr)

    # now I am a daemon!

    # switch user
    setuser(recover=False)

    # close standard fds, so that child processes don't inherit them even though
    # we override Python-level stdio
    os.close(0)
    os.close(1)
    os.close(2)

    # redirect standard file descriptors
    sys.stdin = open('/dev/null', 'r')
    sys.stdout = sys.stderr = open('/dev/null', 'w')


def setuser(recover=True):
    """Do not daemonize, but at least set the current user and group correctly
    to the configured values if started as root.
    """
    if os.name != 'posix' or os.geteuid() != 0:
        return
    # running as root is not good...
    if config.user is None or config.group is None:
        raise RuntimeError('please provide valid entries for user and '
                           'group in nicos.conf if running as root')
    # switch user
    group = config.group
    userentry = None
    if config.user and pwd is not None:
        userentry = pwd.getpwnam(config.user)
    if group and grp is not None and userentry:
        gid = grp.getgrnam(group).gr_gid
        if recover:
            os.setegid(gid)
        else:
            os.setgid(gid)
        # initialize the group access list with all of the groups the
        # configured user is a member plus gid
        os.initgroups(userentry.pw_name, gid)
    if userentry and pwd is not None:
        uid = userentry.pw_uid
        if recover:
            os.seteuid(uid)
        else:
            os.setuid(uid)
        if 'HOME' in os.environ:
            os.environ['HOME'] = pwd.getpwuid(uid).pw_dir
    if config.umask is not None and hasattr(os, 'umask'):
        os.umask(int(config.umask, 8))


# as copied from Python 3.3
def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.

    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    """
    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode) and
                not os.path.isdir(fn))

    # Short circuit. If we're given a full path which matches the mode
    # and it exists, we're done here.
    if _access_check(cmd, mode):
        return cmd

    path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        matches = [cmd for ext in pathext if cmd.lower().endswith(ext.lower())]
        # If it does match, only test that one, otherwise we have to try
        # others.
        files = [cmd] if matches else [cmd + ext.lower() for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir_ in path:
        dir_ = os.path.normcase(dir_)
        if dir_ not in seen:
            seen.add(dir_)
            for thefile in files:
                name = os.path.join(dir_, thefile)
                if _access_check(name, mode):
                    return name
    return None


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
    ('black', 'darkgray'),
    ('darkred', 'red'),
    ('darkgreen', 'green'),
    ('brown', 'yellow'),
    ('darkblue', 'blue'),
    ('purple', 'fuchsia'),
    ('turquoise', 'teal'),
    ('lightgray', 'white'),
]

for _i, (_dark, _light) in enumerate(_colors):
    _codes[_dark] = '\x1b[%im' % (_i + 30)
    _codes[_light] = '\x1b[%i;01m' % (_i + 30)


def colorize(name, text):
    return _codes.get(name, '') + text + _codes.get('reset', '')


def colorcode(name):
    return _codes.get(name, '')


def nocolor():
    for key in list(_codes):
        _codes[key] = ''


if os.name == 'nt':
    try:
        # colorama provides ANSI-colored console output support under Windows
        import colorama  # pylint: disable=F0401
    except ImportError:
        nocolor()
    else:
        colorama.init()


# nice formatting for an exit status

def whyExited(status):
    if os.WIFSIGNALED(status):
        signum = os.WTERMSIG(status)
        try:
            signame = [name for name in dir(signal)
                       if name.startswith('SIG') and
                       getattr(signal, name) == signum][0]
        except IndexError:
            signame = 'signal %d' % signum
        return signame
    else:
        return 'exit code %d' % os.WEXITSTATUS(status)


# traceback utilities

def formatExtendedFrame(frame):
    ret = []
    for key, value in iteritems(frame.f_locals):
        if key in ('credentials', 'password'):
            continue
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
        if filename not in ('<script>', '<string>'):
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


def formatException(cut=0, exc_info=None):
    """Format an exception with traceback, but leave out the first `cut`
    number of frames.
    """
    if exc_info is None:
        typ, val, tb = sys.exc_info()
    else:
        typ, val, tb = exc_info  # pylint: disable=W0633
    res = ['Traceback (most recent call last):\n']
    tbres = traceback.format_tb(tb, sys.maxsize)
    res += tbres[cut:]
    res += traceback.format_exception_only(typ, val)
    return ''.join(res)


def formatScriptError(exc_info, script_name, script_text):
    """Format an error in the script for notifications."""
    exception = formatException(exc_info=exc_info).splitlines()[-1]
    # try to find the offending line
    tb = exc_info[2]
    lineno = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename in ('<script>', '<string>'):
            lineno = tb.tb_lineno
        tb = tb.tb_next
    # try to format the line
    if lineno is not None:
        msg = 'The error was in line %d:\n\n' % lineno
        minline = max(lineno-5, 0)
        lines = script_text.splitlines(True)[minline:lineno+4]
        for i, line in enumerate(lines, start=minline+1):
            msg += '%4d %s | %s' % (i, '*' if i == lineno else ' ', line)
    elif len(script_text) < 10000:
        msg = 'The script was:\n\n' + script_text
    else:
        msg = ''
    if script_name:
        msg = 'Script name: %s\n\n' % script_name + msg
    body = 'An error occurred in the executed script:\n\n' + \
           exception + '\n\n' + msg
    return body, exception


# file counter utilities

def readFileCounter(counterpath, key):
    """Read a counter from a "counter" file.

    The counter file consists of lines with ``key value`` pairs.  If the key
    does not exist in the file, return 0; other exceptions are not handled.
    """
    try:
        lines = readFile(counterpath)
    except IOError:
        writeFile(counterpath, [])
        return 0
    for line in lines:
        linekey, value = line.split()
        if key == linekey:
            return int(value)
    # the counter is not yet in the file
    return 0


def updateFileCounter(counterpath, key, value):
    """Update a counter file."""
    if not path.isdir(path.dirname(counterpath)):
        os.makedirs(path.dirname(counterpath))
    lines = readFile(counterpath)
    new_lines = []
    for line in lines:
        linekey, _ = line.split()
        if linekey != key:
            new_lines.append(line + '\n')
    new_lines.append('%s %d\n' % (key, value))
    writeFile(counterpath, new_lines)


def allDays(fromtime, totime):
    """Determine days of an interval between two timestamps."""
    tmfr = int(mktime(localtime(fromtime)[:3] + (0, 0, 0, 0, 0, -1)))
    tmto = int(min(currenttime(), totime))
    for tmday in range(tmfr, tmto, 86400):
        lt = localtime(tmday)
        yield str(lt[0]), '%02d-%02d' % lt[1:3]


# Note, binding "sleep" as a local here since this function usually is run
# in a thread, and to avoid tracebacks on shutdown we have to avoid using
# globals that are set to None by Python on shutdown.
def watchFileTime(filename, log, interval=1.0, sleep=sleep):
    """Watch a file until its mtime changes; then return."""
    def get_mtime(getmtime=path.getmtime):
        # os.path.getmtime() can raise "stale NFS file handle", so we
        # guard against it
        while 1:
            try:
                return getmtime(filename)
            except OSError as err:
                log.error('got exception checking for mtime of %r: %s',
                          filename, err)
                sleep(interval / 2)
                # it's not a big problem if we never get out of the loop
                continue
    mtime = get_mtime()
    sleep(interval)
    while True:
        if get_mtime() != mtime:
            return
        sleep(interval)


def watchFileContent(filename, log, interval=1.0, sleep=sleep):
    """Watch a file until its content changes; then return."""
    def get_content():
        # File could be unavailable temporary on nfs mounts,
        # so let's retry it
        while True:
            try:
                with open(filename, 'r') as f:
                    return f.read().strip()
            except IOError as err:
                log.error('got exception checking for content of %r: %s',
                          filename, err)
                sleep(interval / 2)
                continue
    content = get_content()
    sleep(interval)
    while True:
        if get_content() != content:
            return
        sleep(interval)


def syncFile(fileObj):
    fileObj.flush()
    os.fsync(fileObj.fileno())


def decodeAny(string):
    """Try to decode the string from UTF-8 or latin9 encoding."""
    if isinstance(string, text_type):
        return string
    try:
        return string.decode('utf-8')
    except UnicodeError:
        # decoding latin9 never fails, since any byte is a valid
        # character there
        return string.decode('latin9')


_SAFE_FILE_CHARS = frozenset('-=+_.,()[]{}0123456789abcdefghijklmnopqrstuvwxyz'
                             'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
_BAD_NAMES = frozenset(('.', '..', 'con', 'prn', 'aux', 'nul') +
                       tuple('com%d' for d in range(1, 10)) +
                       tuple('lpt%d' for d in range(1, 10)))


def safeName(what, _SAFE_FILE_CHARS=_SAFE_FILE_CHARS):
    """Return a cleaned up version of the given string, which could e.g. be
    used for filenames.
    """
    # normalize: é -> e, Â->A, etc.
    s = unicodedata.normalize('NFKD', decodeAny(what))
    # map unwanted characters (including space) to '_'
    s = ''.join(c if c in _SAFE_FILE_CHARS else '_' for c in s)
    # collate multiple '_'
    while '__' in s:
        s = s.replace('__', '_')
    # avoid special bad names
    if s.lower() in _BAD_NAMES:
        s = '_%s_'
    return s if s else '_empty_'


# helper to access a certain nicos file which is non-python

def findResource(filepath):
    """Helper to find a certain nicos specific, but non-python file."""
    rmPrefix = 'custom/'
    if filepath.startswith(rmPrefix):
        return path.join(config.custom_path, filepath[len(rmPrefix):])
    return path.join(config.nicos_root, filepath)


def clamp(value, minval, maxval):
    """Return a value clamped to the given interval [minval, maxval]."""
    minval, maxval = min(minval, maxval), max(minval, maxval)
    return min(max(value, minval), maxval)


def uniq(lst):
    """Return a list with unique elements (but preserved order)."""
    new = []
    seen = set()
    for item in lst:
        if item not in seen:
            new.append(item)
            seen.add(item)
    return new


def timedRetryOnExcept(max_retries=1, timeout=1, ex=None, actionOnFail=None):
    """Wrapper: Try a call and retry it on an exception.

    max_retries: how often to retry
    timeout: how long to sleep between tries
    ex: only catch specified exceptions, if None, only catch `Exception`
    actionOnFail: will be called when an exception occured

    All other args are passed to wrapped function.  If max_retries is
    exhausted, the exception is reraised.
    """

    if ex is None:
        ex = Exception

    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            assert max_retries > 0
            x = max_retries
            while x:
                try:
                    return func(*args, **kwargs)
                except ex:
                    x -= 1

                    if actionOnFail:
                        actionOnFail()

                    sleep(timeout)
                    raise
        return wrapper
    return outer


def make_load_config(filepath):
    """Create a load_config function for use in setups."""
    def load_config(name):
        from nicos.core.errors import ConfigurationError
        try:
            setupname, element = name.split('.')
        except ValueError:
            raise ConfigurationError('configdata() argument must be in the '
                                     'form \'module.valuename\'')
        fullname = path.join(path.dirname(filepath), setupname + '.py')
        ns = {}
        if path.isfile(fullname):
            with open(fullname) as fp:
                exec_(fp, ns)
        try:
            return ns[element]
        except KeyError:
            raise ConfigurationError('value named %s not found in config '
                                     'setup %s' % (element, setupname))
    return load_config


def tabulated(widths, iterable, maxwidth=20):
    """Return strings from iterable spaced as columns with given widths.

    When an entry is is wider than the current width, update the widths.
    """
    result = []
    for i, item in enumerate(iterable):
        result.append(item)
        if i < len(widths):
            width = widths[i]
            if len(item) > width:
                width = widths[i] = min(len(item), maxwidth)
            result.append(' ' * (width - len(item) + 1))
        else:
            result.append(' ')
    return ''.join(result).rstrip()


def num_sort(x, inf=float('inf')):
    """A sort key function to sort strings by a numeric prefix, then
    lexically.
    """
    if not isinstance(x, string_types):
        return (0, x)
    m = re.match(r'[\d.-]+', x)
    try:
        return (float(m.group()), x) if m else (inf, x)
    except ValueError:
        return (inf, x)


class ReaderRegistry(object):
    readers = dict()

    @classmethod
    def registerReader(cls, rdcls):
        for key in rdcls.filetypes:
            cls.readers[key] = rdcls

    @classmethod
    def getReaderCls(cls, key):
        return cls.readers[key]

    @classmethod
    def filetypes(cls):
        return list(cls.readers)


keyexpr_re = re.compile(r'(?P<dev_or_key>[a-zA-Z_0-9./]+)'
                        r'(?P<indices>(?:\[[0-9]+\])*)'
                        r'(?P<scale>\*[0-9.]+(?:[eE][+-]?[0-9]+)?)?'
                        r'(?P<offset>[+-][0-9.]+(?:[eE][+-]?[0-9]+)?)?$')


def extractKeyAndIndex(spec):
    """Extract a key and possibly subindex from a cache key specification
    given by the user.  This takes into account the following changes:

    * '/' can be replaced by '.'
    * If it is not in the form 'dev/key', '/value' is automatically appended.
    * Subitems can be specified: ``dev.keys[10], det.rates[0][1]``.
    * A scale factor can be added with ``*X``.
    * An offset can be added with ``+X`` or ``-X``.
    """
    match = keyexpr_re.match(spec.replace(' ', ''))
    if not match:
        return spec.lower().replace('.', '/'), (), 1.0, 0
    groups = match.groupdict()
    key = groups['dev_or_key'].lower().replace('.', '/')
    if '/' not in key:
        key += '/value'
    indices = groups['indices']
    try:
        if indices is not None:
            indices = tuple(map(int, indices[1:-1].split('][')))
        else:
            indices = ()
    except ValueError:
        indices = ()
    scale = groups['scale']
    try:
        scale = float(scale[1:]) if scale is not None else 1.0
    except ValueError:
        scale = 1.0
    offset = groups['offset']
    try:
        offset = float(offset) if offset is not None else 0.0
    except ValueError:
        offset = 0.0
    return key, indices, scale, offset


def checkSetupSpec(setupspec, setups, compat='or', log=None):
    """Check if the given setupspec should be displayed given the loaded setups.
    """
    def fixup_old(s):
        if s.startswith('!'):
            return 'not %s' % s[1:]
        return s

    def subst_setupexpr(match):
        if match.group() in ('has_setup', 'and', 'or', 'not'):
            return match.group()
        return 'has_setup(%r)' % match.group()

    def has_setup(spec):
        return bool(fnmatch.filter(setups, spec))

    if not setupspec:
        return True  # no spec -> always visible
    if not setups:
        return False  # no setups -> not visible (safety)
    if isinstance(setupspec, list):
        setupspec = (' %s ' % compat).join(fixup_old(v) for v in setupspec)
    if setupspec.startswith('!'):
        setupspec = fixup_old(setupspec)
    expr = re.sub(r'[\w\[\]*?]+', subst_setupexpr, setupspec)
    ns = {'has_setup': has_setup}
    try:
        return eval(expr, ns)
    except Exception:  # wrong spec -> visible
        if log:
            log.warning('invalid setup spec: %r', setupspec)
        return True
