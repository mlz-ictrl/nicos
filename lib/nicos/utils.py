#  -*- coding: utf-8 -*-
# *****************************************************************************
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
import copy
import errno
import types
import signal
import socket
import inspect
import linecache
import threading
import traceback
import ConfigParser
from os import path
from time import sleep

from nicos import status
from nicos.errors import ConfigurationError, ProgrammingError, ModeError, \
     NicosError


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
    - *volatile*: if the parameter should always be read from hardware
    - *unit*: unit of the parameter for informational purposes; 'main' is
      replaced by the device unit when presented
    - *category*: category of the parameter when returned by device.info()
      or None to ignore the parameter
    - *preinit*: whether the parameter must be initialized before preinit()
    - *prefercache*: whether on initialization, a value from the cache is
      preferred to a value from the config -- the default is true for
      settable parameters and false for non-settable parameters
    - *userparam*: whether this parameter should be shown to the user
      (default is True)
    """

    _notset = object()

    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, volatile=False,
                 unit=None, category=None, preinit=False, prefercache=None,
                 userparam=True):
        self.type = type
        if default is self._notset:
            default = type()
        self.default = default
        self.mandatory = mandatory
        self.settable = settable
        self.volatile = volatile
        self.unit = unit
        self.category = category
        self.description = description
        self.preinit = preinit
        self.prefercache = prefercache
        self.userparam = userparam
        self.classname = None  # filled by DeviceMeta

    def __repr__(self):
        return '<Param info>'

    def formatDoc(self):
        txt = 'Parameter: '
        txt += self.description or ''
        txt += '\n'
        if isinstance(self.type, type(listof)):
            txt += '\n    * Type: ' + (self.type.__doc__ or '')
        else:
            txt += '\n    * Type: ' + self.type.__name__
        txt += '\n    * Default value: ``' + repr(self.default) + '``'
        if self.unit is not None:
            if self.unit == 'main':
                txt += '\n    * Unit: \'main\' -> get unit from Device'
            else:
                txt += '\n    * Unit: ' + self.unit
        if self.settable:
            txt += '\n    * Settable at runtime'
        else:
            txt += '\n    * Not settable at runtime'
        if self.category:
            txt += '\n    * Info category: ' + self.category
        if self.mandatory:
            txt += '\n    * Is mandatory (must be given in setup)'
        if self.volatile:
            txt += '\n    * Is volatile (will always be read from hardware)'
        if self.preinit:
            txt += '\n    * Is initialized before device preinit'
        if self.prefercache is not None:
            txt += '\n    * Prefer value from cache: %s' % self.prefercache
        if not self.userparam:
            txt += '\n    * Not shown to user'
        return txt


class Override(object):

    def __init__(self, **kw):
        self._kw = kw

    def apply(self, paraminfo):
        newinfo = copy.copy(paraminfo)
        for attr in self._kw:
            setattr(newinfo, attr, self._kw[attr])
        return newinfo


class Value(object):
    """
    This class defines the properties of a Measurable read value.
    """

    def __init__(self, name, type='other', errors='none', unit='',
                 fmtstr='%.3f', active=True):
        self.name = name
        self.type = type
        self.errors = errors
        self.unit = unit
        self.fmtstr = fmtstr
        self.active = active

    def __repr__(self):
        return 'value %r' % self.name


class DeviceMeta(type):
    """
    A metaclass that automatically adds properties for the class' parameters,
    and determines a list of user methods ("commands").

    It also merges attached_devices, parameters and parameter_overrides defined
    in the class with those defined in all base classes.
    """

    def __new__(mcs, name, bases, attrs):
        if 'parameters' in attrs:
            for pname, pinfo in attrs['parameters'].iteritems():
                pinfo.classname = attrs['__module__'] + '.' + name
        for base in bases:
            if hasattr(base, 'parameters'):
                for pinfo in base.parameters.itervalues():
                    if pinfo.classname is None:
                        pinfo.classname = base.__module__ + '.' + base.__name__
        newtype = type.__new__(mcs, name, bases, attrs)
        for entry in newtype.__mergedattrs__:
            newentry = {}
            for base in reversed(bases):
                if hasattr(base, entry):
                    newentry.update(getattr(base, entry))
            newentry.update(attrs.get(entry, {}))
            setattr(newtype, entry, newentry)
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
            if not info.volatile:
                def getter(self, param=param):
                    if param not in self._params:
                        self._initParam(param)
                    if self._cache:
                        value = self._cache.get(self, param)
                        if value is not None:
                            self._params[param] = value
                            return value
                    return self._params[param]
            else:
                rmethod = getattr(newtype, 'doRead' + param.title(), None)
                if rmethod is None:
                    raise ProgrammingError('%r device %r parameter is marked '
                                           'as "volatile=True", but has no '
                                           'doRead%s method' %
                                           (name, param, param.title()))
                def getter(self, param=param, rmethod=rmethod):
                    if self._mode == 'simulation':
                        return self._initParam(param)
                    value = rmethod(self)
                    if self._cache:
                        self._cache.put(self, param, value)
                    self._params[param] = value
                    return value

            # create the setter method
            if not info.settable:
                def setter(self, value, param=param):
                    raise ConfigurationError(
                        self, 'cannot set the %s parameter' % param)
            else:
                wmethod = getattr(newtype, 'doWrite' + param.title(), None)
                umethod = getattr(newtype, 'doUpdate' + param.title(), None)
                def setter(self, value, param=param, wmethod=wmethod,
                           umethod=umethod):
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
                        if umethod:
                            umethod(self, value)
                        self._params[param] = value
                        return
                    if wmethod:
                        # allow doWrite to override the value
                        rv = wmethod(self, value)
                        if rv is not None:
                            value = rv
                    if umethod:
                        umethod(self, value)
                    self._params[param] = value
                    if self._cache:
                        self._cache.put(self, param, value)

            # create a property and attach to the new device class
            setattr(newtype, param,
                    property(getter, setter, doc=info.formatDoc()))
        del newtype.parameter_overrides
        if 'parameter_overrides' in attrs:
            del attrs['parameter_overrides']
        if 'valuetype' in attrs:
            newtype.valuetype = staticmethod(attrs['valuetype'])

        newtype.commands = {}
        for methname in attrs:
            if methname.startswith(('_', 'do')):
                continue
            method = getattr(newtype, methname)
            if not isinstance(method, types.MethodType):
                continue
            if not hasattr(method, 'is_usermethod'):
                continue
            argspec = inspect.getargspec(method)
            if argspec[0] and argspec[0][0] == 'self':
                del argspec[0][0]  # get rid of "self"
            args = inspect.formatargspec(*argspec)
            if method.__doc__:
                docline = method.__doc__.strip().splitlines()[0]
            else:
                docline = ''
            newtype.commands[methname] = (args, docline)

        return newtype


def usermethod(func):
    """Decorator that marks a method as a user-visible method."""
    func.is_usermethod = True
    return func


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


# read nicos.conf files

class NicosConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, key):
        return key

def readConfig():
    fn = path.normpath(path.join(path.dirname(__file__), '../../nicos.conf'))
    cfg = NicosConfigParser()
    cfg.read(fn)
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
    for field in field_re.finditer(template):
        result.append(template[:current])
        replacement = keywords.get(field.group('key'))
        if replacement is None:
            replacement = field.group('default')
            if replacement is None:
                raise NicosError('no value given for %r' % field.group('key'))
        result.append(replacement)
        current = field.end()
    result.append(template[current:])
    return ''.join(result)


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


# device utility functions

def multiStatus(devices):
    rettext = []
    retstate = status.OK
    for devname, dev in devices:
        if dev is None:
            continue
        # XXX status or status(0)
        state, text = dev.status()
        rettext.append('%s=%s' % (devname, text))
        if state > retstate:
            retstate = state
    return retstate, ', '.join(rettext)


def waitForStatus(dev, delay=0.3, busystate=status.BUSY):
    # XXX add a timeout?
    # XXX what about error status?
    while True:
        st = dev.status(0)
        if st[0] == busystate:
            sleep(delay)
            # XXX add a breakpoint here?
        else:
            break
    return st


# parameter conversion functions

_notset = object()

def convdoc(conv):
    if isinstance(conv, type(convdoc)):
        return conv.__doc__ or ''
    return conv.__name__

def listof(conv):
    def converter(val=[]):
        if not isinstance(val, list):
            raise ValueError('value needs to be a list')
        return map(conv, val)
    converter.__doc__ = 'a list of %s' % convdoc(conv)
    return converter

def nonemptylistof(conv):
    def converter(val=None):
        if val is None:
            return [conv()]
        if not isinstance(val, list):
            raise ValueError('value needs to be a nonempty list')
        if not val:
            raise ValueError('value needs to be a nonempty list')
        return map(conv, val)
    converter.__doc__ = 'a non-empty list of %s' % convdoc(conv)
    return converter

def tupleof(*types):
    def converter(val=None):
        if val is None:
            return tuple(type() for type in types)
        if not isinstance(val, (list, tuple)) or not len(types) == len(val):
            raise ValueError('value needs to be a %d-tuple' % len(types))
        return tuple(t(v) for (t, v) in zip(types, val))
    converter.__doc__ = 'a tuple of (' + ', '.join(map(convdoc, types)) + ')'
    return converter

def dictof(keyconv, valconv):
    def converter(val={}):
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in val.iteritems():
            ret[keyconv(k)] = valconv(v)
        return ret
    converter.__doc__ = 'a dict of %s keys and %s values' % \
                        (convdoc(keyconv), convdoc(valconv))
    return converter

tacodev_re = re.compile(r'^(//[\w.]+/)?\w+/\w+/\w+$', re.I)

def tacodev(val=None):
    """a valid taco device"""
    if val is None:
        return ''
    val = str(val)
    if not tacodev_re.match(val):
        raise ValueError('%s is not a valid Taco device name' % val)
    return val

def anytype(val=None):
    """any value"""
    return val

def vec3(val=[0,0,0]):
    """a 3-vector"""
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
    converter.__doc__ = 'an integer in the range [%d, %d)' % (fr, to)
    return converter

def floatrange(fr, to):
    def converter(val=fr):
        val = float(val)
        if not fr <= val <= to:
            raise ValueError('value needs to fulfill %d <= x <= %d' % (fr, to))
        return val
    converter.__doc__ = 'a float in the range [%f, %f]' % (fr, to)
    return converter

def oneof(conv, *vals):
    def converter(val=vals[0]):
        val = conv(val)
        if val not in vals:
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, vals))))
        return val
    converter.__doc__ = 'one of ' + ', '.join(map(repr, vals))
    return converter

def oneofdict(vals):
    def converter(val=None):
        if val in vals.keys():
            val = vals[val]
        elif val not in vals.values():
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, vals))))
        return val
    converter.__doc__ = 'one of ' + ', '.join(map(repr, vals.values()))
    return converter

def existingdir(val='.'):
    """an existing directory name"""
    val = str(val)
    if not os.path.isdir(val):
        raise ValueError('value %s is not an existing directory' % val)
    return val

def none_or(conv):
    def converter(val=None):
        if val is None:
            return None
        return conv(val)
    converter.__doc__ = 'None or %s' % convdoc(conv)
    return converter
