# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS utilities independent from an active session."""

import ast
import fnmatch
import inspect
import linecache
import locale
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import traceback
import unicodedata
from collections import OrderedDict
from contextlib import contextmanager
from datetime import date, timedelta
from functools import wraps
from io import BufferedWriter, FileIO
from itertools import chain, islice
from os import path
from stat import S_IRGRP, S_IROTH, S_IRUSR, S_IRWXU, S_IWUSR, S_IXGRP, \
    S_IXOTH, S_IXUSR
from time import localtime, mktime, sleep, strftime, strptime, \
    time as currenttime

import numpy

# do **not** import nicos.session here
# session dependent nicos utilities should be implemented in nicos.core.utils
from nicos import config, get_custom_version, nicos_version

try:
    import grp
    import pwd
except ImportError:
    pwd = grp = None

try:
    LOCALE_ENCODING = locale.getpreferredencoding(False)
except Exception:
    LOCALE_ENCODING = 'utf-8'


# all builtin number types (useful for isinstance checks)
number_types = (int, float)


class AttrDict(dict):
    """Dictionary whose items can be set with attribute access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key) from None


class LCDict(dict):
    """Dictionary with automatic lower-casing of keys."""
    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), value)

    def __delitem__(self, key):
        return dict.__delitem__(self, key.lower())


class lazy_property:
    """A property that calculates its value only once."""
    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, obj_class):
        if obj is None:
            return self
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

    def __reduce__(self):
        return list.__reduce__(self)


class readonlydict(dict):
    def _no(self, *args, **kwds):
        raise TypeError('individual dict values can not be changed')
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = \
        update = _no

    def __getnewargs__(self):
        return (dict(self.items()),)

    def __reduce__(self):
        return dict.__reduce__(self)

    def copy(self):
        return {k: v.copy() if isinstance(v, dict) else v
                for k, v in self.items()}


class BoundedOrderedDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self.maxlen = kwds.pop('maxlen', None)
        OrderedDict.__init__(self, *args, **kwds)
        self._checklen()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._checklen()

    def _checklen(self):
        if self.maxlen is not None:
            while len(self) > self.maxlen:
                self.popitem(last=False)

    def getlast(self):
        (key, value) = self.popitem(last=True)
        self[key] = value
        return value


class AutoDefaultODict(OrderedDict):
    """Ordered dict that automatically creates values for missing keys as
    ordered dicts.

    Useful for creating hierarchical dicts.
    """
    def __missing__(self, key):
        val = self[key] = self.__class__()
        return val


class Repeater:
    def __init__(self, obj):
        self.object = obj
        self._stop = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration
        return self.object

    def __len__(self):
        return 0

    def __getitem__(self, item):
        return self.object

    def stop(self):
        self._stop = True


class HardwareStub:
    """An object that denies all attribute access, used to prevent accidental
    hardware access in simulation mode.
    """

    def __init__(self, dev):
        self.dev = dev

    def __getattr__(self, name):
        from nicos.core import ProgrammingError
        raise ProgrammingError(self.dev, 'accessing hardware method %s in '
                               'simulation mode' % name)


class Device(tuple):
    """Helper class for reading setups, to distinguish device() from
    lists/tuples of devices.

    The class is placed in this module because it is serialized and the client
    should not need to import nicos.core.sessions.
    """


class Secret(tuple):
    """Helper class for reading setups, to distinguish secret() from
    lists/tuples.
    """


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
        hrs = int(secs / 3600.)
        mins = int((secs % 3600) / 60. + 0.5)
        if mins == 60:
            hrs += 1
            mins = 0
        est = '%s h, %s min' % (hrs, mins)
    else:
        days = int(secs / 86400.)
        hrs = int((secs % 86400) / 3600. + 0.5)
        if hrs == 24:
            days += 1
            hrs = 0
        est = '%s day%s, %s h' % (_s(days) + (hrs,))
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


def printTable(headers, items, printfunc, minlen=0, rjust=False):
    """Print tabular information nicely formatted."""
    if not headers and not items:
        return
    ncolumns = len(headers or items[0])
    rowlens = [minlen] * ncolumns
    for row in [headers or []] + items:
        for i, item in enumerate(row):
            rowlens[i] = max(rowlens[i], len(item))
    rfmtstr = ('%%%ds  ' * ncolumns) % tuple(rowlens)
    lfmtstr = ('%%-%ds  ' * ncolumns) % tuple(rowlens)
    if headers:
        printfunc(lfmtstr % tuple(headers))
        printfunc(lfmtstr % tuple('=' * l for l in rowlens))
    for row in items:
        printfunc((rfmtstr if rjust else lfmtstr) % tuple(row))


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
        custom_path=config.setup_package_path,
        custom_version=get_custom_version(),
    )
    nicosroot_key = config.nicos_root.replace('/', '_')
    key = 'sysinfo/%s/%s/%s' % (service, host, nicosroot_key)
    return key, res


def parseHostPort(host, defaultport, missingportok=False):
    """Parse host[:port] string and tuples

    Specify 'host[:port]' or a (host, port) tuple for the mandatory argument.
    If the port specification is missing, the value of the defaultport is used.

    On wrong input, this function will raise a ValueError.
    """
    if isinstance(host, (tuple, list)):
        host, port = host
    elif ':' in host:
        host, port = host.rsplit(':', 1)
    else:
        port = defaultport
    if not missingportok and port is None:
        raise ValueError('a valid port is required')
    if port is not None:
        try:
            port = int(port)
        except ValueError:
            raise ValueError('invalid port number: ' + port) from None
        if not 0 < port < 65536:
            raise ValueError('port number out of range')
    if ':' in host:
        raise ValueError('host name must not contain ":"')
    return host, port


def tcpSocket(host, defaultport, timeout=None, keepalive=None):
    """Helper for opening a TCP client socket to a remote server.

    Specify 'host[:port]' or a (host, port) tuple for the mandatory argument.
    If the port specification is missing, the value of the defaultport is used.
    If timeout is set to a number, the timout of the connection is set to this
    number, else the socket stays in blocking mode.

    If *keepalive* is given, enable TCP keepalive and set the keepalive
    interval to that amount of seconds.
    """
    host, port = parseHostPort(host, defaultport)

    # open socket and set options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if timeout:
            s.settimeout(timeout)
    # connect
        s.connect((host, int(port)))
    except OSError:
        closeSocket(s)
        raise
    if keepalive:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, 'TCP_KEEPCNT'):
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 3)
        if hasattr(socket, 'TCP_KEEPINTVL'):
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, keepalive)
        if hasattr(socket, 'TCP_KEEPIDLE'):
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, keepalive)
    return s


def closeSocket(sock, socket=socket):
    """Do our best to close a socket."""
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


@contextmanager
def tcpSocketContext(host, defaultport, timeout=None):
    """Context manager for `tcpSocket` (for arguments see there).

    Usage::

        with tcpSocketContext(host, port, timeout) as sock:
            do socket operations on sock
    """
    sock = None
    try:
        sock = tcpSocket(host, defaultport, timeout)
        yield sock
    finally:
        closeSocket(sock)


def getfqdn():
    """Get fully qualified hostname."""
    hostname = socket.gethostname()
    if '.' in hostname:
        return hostname
    return socket.getfqdn(hostname)


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


def createSubprocess(cmdline, **kwds):
    """Create a subprocess.Popen with the proper setting of close_fds."""
    if 'close_fds' not in kwds:
        # only supported on Posix and (Windows if not redirected)
        if os.name == 'posix' or not (kwds.get('stdin') or
                                      kwds.get('stdout') or
                                      kwds.get('stderr')):
            kwds['close_fds'] = True
    return subprocess.Popen(cmdline, **kwds)  # pylint: disable=consider-using-with


try:
    MAXFD = os.sysconf('SC_OPEN_MAX')
except Exception:
    MAXFD = 256


def reexecProcess():
    """Re-execute the current process with the same arguments."""
    os.closerange(3, MAXFD)
    os.execv(sys.executable, [sys.executable] + sys.argv)


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
    import fcntl
    import struct
    import termios
    try:
        h, w, _hp, _wp = struct.unpack(
            'HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                struct.pack('HHHH', 0, 0, 0, 0)))
    except OSError:
        return 80, 25
    return w, h


def parseConnectionString(s, defport):
    """Parse a string in the format 'user:pass@host:port"."""
    res = re.match(r'(?:([^:]+)(?::([^@]*))?@)?([\w.-]+)(?::(\d+))?$', s)
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


def importString(import_name):
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
    fromlist = [obj] if obj else []
    try:
        mod = __import__(modname, {}, {}, fromlist)
    except ImportError as err:
        raise ImportError(
            'Could not import %r: %s' % (import_name, err)) from err
    if not obj:
        return mod
    else:
        return getattr(mod, obj)


def resolveClasses(classes):
    """Resolve class(es) from either class instances or strings.

    If the input (list) contains strings, we use the `importString` function
    to resolve this string to a class object.  Anything else is passed through
    unchanged.

    Returns a tuple of classes, usable e.g. in isinstance checks.
    """
    if not isinstance(classes, (list, tuple)):
        classes = [classes]
    return tuple(importString(cls) if isinstance(cls, str) else cls
                 for cls in classes)


# simple file operations
#
# first constants, then functions
#
DEFAULT_DIR_MODE = S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH
DEFAULT_FILE_MODE = S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH


def readFile(filename):
    with open(filename, 'r', encoding='utf-8') as fp:
        return [line.strip() for line in fp]


def writeFile(filename, lines):
    with open(filename, 'w', encoding='utf-8') as fp:
        fp.writelines(lines)


def moveOutOfWay(filepath, maxbackups=10):
    """Move files out of the way , while keeping backups

    if ``maxbackups`` is None, then the highest found number+1 will get appended
    (backup n +1 is newer than backup n)
    if ``maxbackups`` is a positive integer then old backups up to ``maxbackups``
    will get a rolling update (backup n is newer than backup n+1)

    The default is a rolling backup with max. 10 backups
    If ``maxbackups`` == 0, then this will just unlink the file.
    """
    if not path.exists(filepath):
        return None
    if maxbackups == 0:
        os.unlink(filepath)
        return None
    if maxbackups is not None:
        for i in range(maxbackups, 1, -1):
            old_bkup = filepath + '.~%d~' % (i - 1)
            new_bkup = filepath + '.~%d~' % (i)
            if path.exists(old_bkup):
                os.rename(old_bkup, new_bkup)
        os.rename(filepath, filepath + '.~%d~' % 1)
        return old_bkup
    else:
        bu_re = re.compile(filepath + r'\.~([0-9]+)~')
        basedir = path.dirname(filepath) or os.curdir
        existing = os.listdir(basedir)
        exist_matching = [int(bu_re.match(e).group(1)) for e in existing
                          if bu_re.match(e)]
        nxt = max(exist_matching) + 1 if exist_matching else 1
        while True:
            renamename = filepath + '.~%d~' % nxt
            if not path.exists(renamename):
                try:
                    os.rename(filepath, renamename)
                    return renamename
                except os.error as ex:
                    raise RuntimeError('Could not rename %s to backup '
                                       'name %s: %s' %
                                       (filepath, renamename, ex)) from ex
            # retry if backup name was already used
            nxt = nxt + 1


def safeWriteFile(filepath, content, maxbackups=10):
    """(Almost) atomic writing of a file.

    The content is first written to a temporary file and then swapped in while
    keeping a backup file.

    It can take both a plain content blob or a list of lines.
    """

    tmpfile = filepath + '.tmp'
    if isinstance(content, list):
        writeFile(tmpfile, content)
    else:
        with open(tmpfile, 'w', encoding='utf-8') as fp:
            fp.write(content)
    try:
        if maxbackups:
            moveOutOfWay(filepath, maxbackups)
    finally:
        os.rename(tmpfile, filepath)


def getPidfileName(appname):
    return os.path.join(config.nicos_root, config.pid_path, appname + '.pid')


def writePidfile(appname):
    pidpath = getPidfileName(appname)
    try:
        os.makedirs(path.dirname(pidpath))
    except FileExistsError:
        pass
    writeFile(pidpath, [str(os.getpid())])


def removePidfile(appname):
    try:
        os.unlink(getPidfileName(appname))
    except FileNotFoundError:
        pass


def ensureDirectory(dirname, enableDirMode=DEFAULT_DIR_MODE, **kwargs):
    """Make sure a directory exists."""
    if not path.isdir(dirname):
        os.makedirs(dirname)
        os.chmod(dirname, enableDirMode)
        enableDirectory(dirname, enableDirMode, **kwargs)


def enableDisableFileItem(filepath, mode, owner=None, group=None, logger=None):
    """Set mode and maybe change uid/gid of a filesystem item."""
    if (owner or group) and pwd and hasattr(os, 'chown') and hasattr(os, 'stat'):
        try:
            stats = os.stat(filepath)  # only change the requested parts
            owner = owner or stats.st_uid
            group = group or stats.st_gid
            if isinstance(owner, str):
                owner = pwd.getpwnam(owner)[2]
            if isinstance(group, str):
                group = grp.getgrnam(group)[2]
            os.chown(filepath, owner, group)
        except (OSError, KeyError) as e:
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
    owner = kwargs.get('disableOwner', owner)
    group = kwargs.get('disableGroup', group)
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
    owner = kwargs.get('enableOwner', owner)
    group = kwargs.get('enableGroup', group)
    failflag = enableDisableDirectory(startdir,
                                      enableDirMode, enableFileMode,
                                      owner, group, enable=True, logger=logger)
    if failflag:
        if logger:
            logger.warning('Enabling failed for some files, please check '
                           'access rights manually')
    return failflag
    # maybe logging is better done in the caller of enableDirectory


# template handling
T_BEGIN = '{{'
T_END = '}}'
T_SPLITTER = f'({T_BEGIN}|{T_END})'
T_expr_re = re.compile('(?P<key>[^!:#]+)(?:!(?P<replace>[^:#]*))?(?::(?P<default>[^#]*))?'
                      '(?:#(?P<description>.*))?')


def _evaluate_template_expression(expr, keywords, expr_re=T_expr_re):
    """evaluate a single template expression match

    Syntax is key[!replace][:default][#description] where all fields except
    key are optional. If the key exists within the given keywords dictionary,
    the whole string is replaced by the value of either replace (if given)
    or the given dictionary item with the requested key. If the key does not exist,
    default is used instead (or '' if there is no default).

    Returns a tuple (result, how, groupdict) where
    result is the result of the expression,
    how is one of 'replaced', 'resolved', 'defaulted' or 'missing'
    and groupdict contains the matched fields of the expression.
    """
    g = expr_re.match(expr).groupdict()
    key = g['key'].strip()
    if key in keywords:
        if g['replace'] is not None:
            return g['replace'], 'replaced', g
        return str(keywords[key]), 'resolved', g
    if g['default'] is not None:
        return g['default'], 'defaulted', g
    return '', 'missing', g


def expandTemplate(template, keywords):
    """Simple template field replacement engine.

    Syntax is {{expression}} where all expressions are handled by
    `_evaluate_template_expression` and (sub)expressions can be nested.
    The {{expression}} is then replaced by the result of the evaluation
    and the evaluation of the whole template continues, until all
    (sub)expressions are resolved.

    note: if the result of an evaluation contains {{something}},
    this is not re-evaluated to avoid endless loops, i.e. evaluation
    pattern is statically given by the template.

    Returns a ``tuple(<replaced string>, [missed keys where default was used],
    [list of missing keys without default])``.
    Each list item is a dictionary with the matched fields of the expression
    (key, replace, default and description).
    """
    stats = dict(
        missing = [],   # key not in keywords, no default given -> resolved to ''
        defaulted = [], # key not in keywords, literal default value used
        replaced = [],  # key in keywords, literal replacement value used
        resolved = [],  # key in keywords, value from keywords used
    )

    tokens = re.split(T_SPLITTER, template)
    found = True
    while found:
        found = False
        for i in range(0, len(tokens)-4, 2):
            # collate a literal/T_BEGIN/literal/T_END/literal quintuple into a single literal
            if tokens[i+1] == T_BEGIN and tokens[i+3] == T_END:
                res, how, gd = _evaluate_template_expression(tokens[i+2], keywords)
                stats[how].append(gd)

                replacement = ''.join([tokens[i], res, tokens[i+4]])
                del tokens[i+1:i+5]
                tokens[i] = replacement
                found = True
                break
    if len(tokens) > 1:
        # malformed template (number of T_BEGIN != T_END)
        # XXX: improve error msg!
        raise ValueError('malformed template! resolving of %r stopped at position %d'%
                         (''.join(tokens), len(tokens[0])))
    return tokens[0], stats['defaulted'], stats['missing']


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
    # pylint: disable=consider-using-with,unspecified-encoding
    sys.stdin = open('/dev/null', 'r', encoding=None)
    sys.stdout = sys.stderr = open('/dev/null', 'w', encoding=None)


def setuser(recover=True):
    """Do not daemonize, but at least set the current user and group correctly
    to the configured values if started as root.

    Users and groups can be either numeric or strings.
    If no group is supplied, the primary group of the user is used.

    """
    if os.name != 'posix' or os.geteuid() != 0:
        return
    # running as root is not good...
    if not config.user:
        raise RuntimeError('please provide valid entries for user and '
                           'group in nicos.conf if running as root')

    # switch user
    group = config.group
    user = config.user
    if pwd is None:
        raise RuntimeError('pwd and/or grp modules not available')

    userentry = pwd.getpwuid(int(user)) if user.isdigit() else pwd.getpwnam(user)
    if group:
        grentry = grp.getgrgid(group) if group.isdigit() else grp.getgrnam(group)
        gid = grentry.gr_gid
    else:
        gid = userentry.pw_gid
    uid = userentry.pw_uid
    if recover:
        os.setegid(gid)
    else:
        os.setgid(gid)
    # initialize the group access list with all of the groups the
    # configured user is a member plus gid
    os.initgroups(userentry.pw_name, gid)
    if recover:
        os.seteuid(uid)
    else:
        os.setuid(uid)
    if 'HOME' in os.environ:
        os.environ['HOME'] = pwd.getpwuid(uid).pw_dir
    if config.umask is not None and hasattr(os, 'umask'):
        os.umask(int(config.umask, 8))


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
        import colorama
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
    secret_indicators = ('credentials', 'passwd', 'password', 'secret')
    for key, value in frame.f_locals.items():
        if key.startswith(secret_indicators) or key.endswith(secret_indicators):
            continue
        try:
            valstr = repr(value)[:256]
        except Exception:
            valstr = '<cannot be displayed>'
        ret.append('        %-20s = %s\n' % (key, valstr))
    ret.append('\n')
    return ret


ST_HEADER = 'Stack trace (most recent call last):'
TB_HEADER = 'Traceback (most recent call last):'
TB_CAUSE_MSG = ('The above exception was the direct cause of the '
                'following exception:')
TB_CONTEXT_MSG = ('During handling of the above exception, another '
                  'exception occurred:')


def listExtendedTraceback(exc, seen=None):
    seen = seen or set()
    if id(exc) in seen:
        return []
    seen.add(id(exc))

    ret = []
    if exc.__cause__ is not None:
        ret += listExtendedTraceback(exc.__cause__, seen)
        ret.extend(['\n', TB_CAUSE_MSG, '\n\n'])
    elif exc.__context__ is not None:
        ret += listExtendedTraceback(exc.__context__, seen)
        ret.extend(['\n', TB_CONTEXT_MSG, '\n\n'])

    ret.extend([TB_HEADER, '\n'])
    tb = exc.__traceback__
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
            if tb.tb_frame.f_globals.get('__name__', '').startswith('nicos'):
                ret += formatExtendedFrame(tb.tb_frame)
        tb = tb.tb_next
    ret += traceback.format_exception_only(type(exc), exc)
    return ret


def formatExtendedTraceback(exc):
    """Format a traceback for the given exception as a string.

    The traceback will include the source line of each frame, as usual, but
    also the values of local variables in the frames.
    """
    return ''.join(listExtendedTraceback(exc)).rstrip('\n')


def formatExtendedStack(frame=None, level=1):
    """Format a stacktrace, starting at the given *frame* (or the current
    frame), showing source and local variables of each frame.
    """
    if frame is None:
        frame = sys._getframe(level)
    ret = [ST_HEADER, '\n\n']
    while frame is not None:
        lineno = frame.f_lineno
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name
        item = '  File "%s", line %d, in %s\n' % (filename, lineno, name)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        if line:
            item = item + '    %s\n' % line.strip()
        ret.insert(1, item)
        if filename != '<script>':
            ret[2:2] = formatExtendedFrame(frame)
        frame = frame.f_back
    return ''.join(ret).rstrip('\n')


def formatException(cut=0, exc_info=None):
    """Format an exception with traceback, but leave out the first `cut`
    number of frames.
    """
    if exc_info is None:
        typ, val, tb = sys.exc_info()
    else:
        typ, val, tb = exc_info
    res = [TB_HEADER, '\n']
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
    except OSError:
        writeFile(counterpath, [])
        return 0
    for line in lines:
        linekey, value = line.split()
        if key == linekey:
            return int(value)
    # the counter is not yet in the file
    return 0


def updateFileCounter(counterpath, key, value):
    """Update a counter file.

       If the file does not exist, it will get created.
    """
    if not path.isdir(path.dirname(counterpath)):
        os.makedirs(path.dirname(counterpath))
    try:
        lines = readFile(counterpath)
    except OSError:
        lines = []
    new_lines = []
    for line in lines:
        linekey, _ = line.split()
        if linekey != key:
            new_lines.append(line + '\n')
    new_lines.append('%s %d\n' % (key, value))
    writeFile(counterpath, new_lines)


def allDays(fromtime, totime):
    """Determine days of an interval between two timestamps."""
    current = date.fromtimestamp(fromtime)
    final = date.fromtimestamp(totime)
    while current <= final:
        yield f'{current.year}', f'{current.month:02}-{current.day:02}'
        current += timedelta(days=1)


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


def watchFileContent(filenames, log, interval=1.0, sleep=sleep):
    """Watch files until content changes; then return."""
    def get_content():
        # File could be unavailable temporary on nfs mounts,
        # so let's retry it
        result = []
        for filename in filenames:
            localinterval = interval
            while True:
                try:
                    with open(filename, 'rb') as f:
                        result.append(f.read())
                    break
                except OSError as err:
                    log.error('got exception checking for content of %r: %s',
                              filename, err)
                    sleep(localinterval)
                    localinterval = min(2 * localinterval, 300)
                    continue
        return result
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
    if isinstance(string, str):
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
                       tuple(f'com{d}' for d in range(1, 10)) +
                       tuple(f'lpt{d}' for d in range(1, 10)))


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
        s = f'_{s}_'
    return s if s else '_empty_'


# helper to access a certain nicos file which is non-python

def findResource(filepath):
    """Helper to find a certain nicos specific, but non-python file."""
    if path.isabs(filepath):
        return filepath
    # strategy for relative paths: try to find first path component as a Python
    # package, then descend from there
    components = filepath.split('/')
    try:
        mod = __import__(components[0])
        if mod.__file__ is None:
            raise AttributeError
        modpath = path.dirname(mod.__file__)
    except (ImportError, AttributeError):
        # fallback: relative to the nicos_root directory
        return path.join(config.nicos_root, filepath)
    return path.join(path.abspath(modpath), *components[1:])


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
    if not isinstance(x, str):
        return (0, x)
    m = re.match(r'[\d.-]+', x)
    try:
        return (float(m.group()), x) if m else (inf, x)
    except ValueError:
        return (inf, x)


def natural_sort(values):
    """Sorts a list of values using natural ordering.

    :param values: list of values to sort.
    :return: the sorted list.
    """
    def _natural_key(key):
        parts = re.split(r'(\d*\.\d+|\d+)', str(key))
        return tuple((e.swapcase() if i % 2 == 0 else float(e))
                     for i, e in enumerate(parts))
    return sorted(values, key=_natural_key)


class ReaderRegistry:
    readers = {}

    @classmethod
    def registerReader(cls, rdcls):
        for key, ffilter in rdcls.filetypes:
            cls.readers[key] = rdcls, ffilter

    @classmethod
    def getReaderCls(cls, key):
        return cls.readers[key][0]

    @classmethod
    def filetypes(cls):
        return list(cls.readers)

    @classmethod
    def filefilters(cls):
        return [(ftype, ffilter) for ftype, (_cls, ffilter) in
                cls.readers.items()]


class FitterRegistry:
    fitters = {}

    @classmethod
    def registerFitter(cls, rdcls):
        for name in rdcls.names:
            cls.fitters[name] = rdcls

    @classmethod
    def getFitterCls(cls, key):
        try:
            return cls.fitters[key.lower()]
        except KeyError:
            raise KeyError('Unknown fitter name %r, known fitters: %s' %
                           (key, ', '.join(cls.fitters))) from None


class KeyExprTransform(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Div) and \
           isinstance(node.left, ast.Name) and \
           isinstance(node.right, ast.Name):
            return ast.Name(id=node.left.id + '/' + node.right.id,
                            ctx=ast.Load())
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name):
            return ast.Name(id=node.value.id + '.' + node.attr,
                            ctx=ast.Load())
        return node


KEYEXPR_NS = {}
for name in [
        'pi', 'sqrt', 'sin', 'cos', 'tan', 'arcsin', 'arccos',
        'arctan', 'exp', 'log', 'radians', 'degrees', 'ceil', 'floor']:
    KEYEXPR_NS[name] = getattr(numpy, name)
KEYEXPR_NS['numpy'] = numpy


def _split_spec(spec, exprs):
    """Return the code for each *expr* in the code *spec*."""
    offset = 0
    snippets = []
    for expr in exprs[1:]:
        new_offset = expr.col_offset
        snippets.append(spec[offset:new_offset].strip().rstrip(','))
        offset = new_offset
    snippets.append(spec[offset:].strip())
    return snippets


def parseKeyExpression(spec, append_value=True,
                       normalize=lambda s: s.lower().replace('.', '/'),
                       multiple=False):
    """Extract expression(s) depending on cache keys from a string.

    An expression must contain a single cache key (given as "a.b" or "a/b"),
    and can otherwise employ Python expression syntax for indexing, scaling
    etc., converting the value to a final form.  Useful math functions from
    `numpy` (as present in the NICOS namespace) and `numpy` itself are defined.

    `/value` is appended to keys without slash if *append_value* is true, and
    dots are replaced by slashes if *normalize* is not redefined.
    If *multiple* is true, multiple expressions forming a tuple are allowed.

    Returns:

    * the normalized key name (or a list if multiple)
    * a code object that calculates the final value from the cache key which
      must be given the name `x` (or a list if multiple), or None if no
      calculation is needed
    * a string with the cleaned expression

    Raises `ValueError` if the expression can't be parsed or is invalid.
    """
    try:
        expr = ast.parse(spec, mode='eval').body
    except SyntaxError:
        raise ValueError('invalid key spec: %r' % spec) from None
    if isinstance(expr, ast.Tuple) and multiple:
        exprs = expr.elts
        descs = _split_spec(spec, exprs)
    else:
        exprs = [expr]
        descs = [spec]
    keys = []
    funs = []
    transformer = KeyExprTransform()
    for expr in exprs:
        # normalize names occuring in the formula
        expr = ast.fix_missing_locations(transformer.visit(expr))
        # find the variable and replace by "x"
        key = None
        for node in ast.walk(expr):
            if isinstance(node, ast.Name) and node.id not in KEYEXPR_NS:
                key = normalize(node.id)
                if '/' not in key and append_value:
                    key += '/value'
                node.id = 'x'
                break
        if key is None:
            raise ValueError('no variable in key spec %r' % descs[-1])
        keys.append(key)
        # expression can be None to mean "identity"
        if isinstance(expr, ast.Name) and expr.id == 'x':
            funs.append(None)
        else:
            funs.append(compile(ast.Expression(body=expr), '<expr>', 'eval'))

    if multiple:
        return keys, funs, descs
    return keys[0], funs[0], descs[0]


def checkSetupSpec(setupspec, setups, log=None):
    """Check if the given setupspec should be displayed given the loaded setups.
    """
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
    try:
        expr = re.sub(r'[-\w\[\]*?]+', subst_setupexpr, setupspec)
        ns = {'has_setup': has_setup}
        return eval(expr, ns)
    except Exception:  # wrong spec -> visible
        if log:
            log.warning('invalid setup spec: %r', setupspec)
        return True


_bare_except = re.compile(r'^([ \t]*)except[ \t]*:', re.MULTILINE)


def fixupScript(script):
    """Perform some fixup operations on the script."""
    # Replace bare except clauses by "except Exception" to prevent
    # catching the ControlStop exception if running under the daemon
    return _bare_except.sub(r'\1except Exception:', script)


def squeeze(shape, n=0):
    """Removes all 1-dimensional entries for all dimensions > ``n``.

    For negative ``n`` the last ``|n|`` dimensions are sequeezed.
    """
    dims = list(shape[:n])
    for dim in shape[n:]:
        if dim > 1:
            dims.append(dim)
    return type(shape)(dims)


DURATION_RE = re.compile(r"""
    ((?P<days>[0-9]+(\.[0-9]*)?)d(ays?)?   # days as 'xd[ays]'
    \ *:?\ *)?                             # split with '', ' ' and/or ':'
    ((?P<hours>[0-9]+(\.[0-9]*)?)hr?       # hours as 'xh[r]'
    \ *:?\ *)?                             # split with '', ' ' and/or ':'
    ((?P<minutes>[0-9]+(\.[0-9]*)?)m(in)?  # minutes as 'xm[in]'
    \ *:?\ *)?                             # split with '', ' ' and/or ':'
    ((?P<seconds>[0-9]+(\.[0-9]*)?)s(ec)?  # seconds as 'xs[ec]'
    )?$                                    # ensure whole string matches
    """, re.X)

DURATION_HINT = 'Provide value as %s or %s.' % (
    '<number>',
    '[-+][<number>d[ays]][:][<number>h[r]][:][<number>m[in]][:][<number>s[ec]]',
)


def parseDuration(inputvalue, allownegative=False):
    """Convert a string into seconds.
    The string can be provided in denominations of days (d), hours (h),
    minutes (m) and seconds (s) or combinations of these.

    - If "allownegative" is set, prepending "-" will return the negative value;
      "+" will be ignored either way.
    - Each denomination can be omitted.
    - Each present value has to be named.
    - The present values have to be sorted in descending size (d h m s)
    - The values can be divided by spaces and/or ':' or written en block.

    If inputvalue is an int or float, it is assumed it is already in seconds
    and returned as is.
    If the input is a timedelta instance, total_seconds is returned.

    Raises a ValueError if the input cannot or should not get parsed
    (this is typically an error in user input).
    Raises a TypeError if an unhandled input type is passed.
    """

    # time has already been provided as seconds
    if isinstance(inputvalue, (int, float)):
        if not allownegative and inputvalue < 0:
            raise ValueError('Negative numbers are not allowed here.')
        return inputvalue
    if isinstance(inputvalue, timedelta):
        return inputvalue.total_seconds()
    elif not isinstance(inputvalue, str):
        raise TypeError('Wrong input data type')

    invalue = inputvalue.strip()

    negative = False
    if invalue.startswith('-'):
        if not allownegative:
            raise ValueError('Negative numbers are not allowed here.')
        negative = True
        invalue = invalue.lstrip('-')
    elif invalue.startswith('+'):
        invalue = invalue.lstrip('+')

    try:
        val = float(invalue)
    except ValueError:
        m = DURATION_RE.match(invalue)

        if not m:
            raise ValueError('"%s" can not be parsed. ' % inputvalue
                             + DURATION_HINT) from None

        groupdict = m.groupdict()
        timedict = {}
        for key, value in groupdict.items():
            if key not in ['days', 'hours', 'minutes', 'seconds']:
                continue
            if value is not None:
                timedict[key] = float(value)
            else:
                timedict[key] = 0
        val = timedelta(**timedict).total_seconds()

    if negative:
        return -val
    else:
        return val


def formatArgs(obj, strip_self=False):
    """Return a formatted version of the object's argument list, enclosed in
    parentheses.

    If *strip_self* is true, strip the "self" argument if present.
    """
    sig = inspect.signature(obj)
    if strip_self and 'self' in sig.parameters:
        sig = sig.replace(parameters=[p for p in sig.parameters.values()
                                      if p.name != 'self'])
    return str(sig)


def getNumArgs(obj):
    """Return the number of "normal" arguments a callable object takes."""
    sig = inspect.signature(obj)
    return sum(1 for p in sig.parameters.values()
               if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                             inspect.Parameter.POSITIONAL_OR_KEYWORD))


def tupelize(iterable, n=2):
    """Convert an iterable into a pairwise tuple iterable.

    s -> (s0,s1), (s2,s3), (s4, s5), ...  for n=2
    s -> (s0, s1, s2), (s2, s3, s4), ...  for n=3

    Leftover elements at the end are ignored.
    """
    return zip(*(iter(iterable),) * n)


def byteBuffer(obj):
    """Return a byte-based memory view of *obj*."""
    # For numpy arrays, memoryview() keeps info about the element size and
    # shape, so that len() gives unexpected results compared to buffer().
    # Casting to a pure byte view gets rid of that.
    return memoryview(obj).cast('B')


class File(BufferedWriter):
    """File-like class for easy inheritance and customization by data sinks."""

    def __init__(self, filepath, openmode):
        self._raw = FileIO(filepath, openmode)
        BufferedWriter.__init__(self, self._raw)


def toAscii(s):
    return s.encode('unicode-escape').decode('ascii')


def merge_dicts(a, b):
    """Creates new dict with dictionary b merged into dictionary a recursively."""
    out = {}
    for key in set(a).union(b):
        if key in a and key in b:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                # merge dicts
                out[key] = merge_dicts(a[key], b[key])
            else:
                out[key] = b[key]
        elif key in a:
            out[key] = a[key]
        else:
            out[key] = b[key]
    return out
