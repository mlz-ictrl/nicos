#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS utility routines
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Utilities for the other methods."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import sys
import time
import socket
import linecache
import traceback
import ConfigParser

from numpy import array, power, linspace
from scipy.odr import RealData, Model, ODR
from scipy.optimize import leastsq

from nicm.errors import ConfigurationError, ProgrammingError, ModeError


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
    """

    _notset = object()

    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, unit=None, category=None):
        self.type = type
        if default is self._notset:
            default = type()
        self.default = default
        self.mandatory = mandatory
        self.settable = settable
        self.unit = unit
        self.category = category
        self.description = description


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


# read nicm.conf files

class NicmConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, key):
        return key

def readConfig(*filenames):
    cfg = NicmConfigParser()
    cfg.read(filenames)
    if cfg.has_section('environment'):
        for name in cfg.options('environment'):
            value = cfg.get('environment', name)
            if name == 'PYTHONPATH':
                # needs to be special-cased
                sys.path.extend(value.split(':'))
            else:
                os.environ[name] = value
    if cfg.has_option('nicm', 'setup_path'):
        from nicm.interface import NICOS
        NICOS.default_setup_path = cfg.get('nicm', 'setup_path')


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

def dictof(keyconv, valconv):
    def converter(val={}):
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in val.iteritems():
            ret[keyconv(k)] = valconv(v)
        return ret
    return converter

def tacodev(val=None):
    # XXX check for valid taco device name
    return str(val)

def any(val=None):
    return val

def vec3(val=[0,0,0]):
    ret = map(float, val)
    if len(ret) != 3:
        raise ValueError('value needs to be a 3-element vector')
    return ret


# fitting utilities

class FitResult(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        if self._failed:
            return 'Fit %-20s failed' % self._name
        elif self._method == 'ODR':
            return 'Fit %-20s success (  ODR  ), chi2: %8.3g, params: %s' % (
                self._name or '', self.chi2,
                ', '.join('%s = %8.3g +/- %8.3g' % v for v in zip(*self._pars)))
        else:
            return 'Fit %-20s success (leastsq), chi2: %8.3g, params: %s' % (
                self._name or '', self.chi2,
                ', '.join('%s = %8.3g' % v[:2] for v in zip(*self._pars)))

    def __nonzero__(self):
        return not self._failed


class Fit(object):
    def __init__(self, model, parnames=None, parstart=None,
                 xmin=None, xmax=None, allow_leastsq=True, ifixb=None):
        self.model = model
        self.parnames = parnames or []
        self.parstart = parstart or []
        self.ifixb = ifixb
        self.xmin = xmin
        self.xmax = xmax
        self.allow_leastsq = allow_leastsq
        if len(self.parnames) != len(self.parstart):
            raise ProgrammingError('number of param names must match number '
                                   'of starting values')

    def par(self, name, start):
        self.parnames.append(name)
        self.parstart.append(start)

    def run(self, name, x, y, dy):
        if len(x) < 2:
            # need at least two points to fit
            return self.result(name, None, x, y, dy, None, None)
        xn, yn, dyn = [], [], []
        for i, v in enumerate(x):
            if self.xmin is not None and v < self.xmin:
                continue
            if self.xmax is not None and v > self.xmax:
                continue
            xn.append(v)
            yn.append(y[i])
            dyn.append(dy[i])
        xn, yn, dyn = array(xn), array(yn), array(dyn)
        # try fitting with ODR
        data = RealData(xn, yn, sy=dyn)
        # fit with fixed x values
        odr = ODR(data, Model(self.model), beta0=self.parstart,
                  ifixx=array([0]*len(xn)), ifixb=self.ifixb)
        out = odr.run()
        if 1 <= out.info <= 3:
            return self.result(name, 'ODR', xn, yn, dyn, out.beta, out.sd_beta)
        else:
            # if it doesn't converge, try leastsq (doesn't consider errors)
            try:
                if not self.allow_leastsq:
                    raise TypeError
                out = leastsq(lambda v: self.model(v, xn) - yn, self.parstart)
            except TypeError:
                return self.result(name, None, xn, yn, dyn, None, None)
            if out[1] <= 4:
                if isinstance(out[0], float):
                    parerrors = [0]
                    parvalues = [out[0]]
                else:
                    parerrors = [0]*len(out[0])
                    parvalues = out[0]
                return self.result(name, 'leastsq', xn, yn, dyn, parvalues,
                                   parerrors=parerrors)
            else:
                return self.result(name, None, xn, yn, dyn, None, None)

    def result(self, name, method, x, y, dy, parvalues, parerrors):
        if method is None:
            dct = {'_name': name, '_failed': True}
        else:
            dct = {'_name': name, '_method': method, '_failed': False,
                   '_pars': (self.parnames, parvalues, parerrors)}
            for name, val, err in zip(self.parnames, parvalues, parerrors):
                dct[name] = val
                dct['d' + name] = err
            if self.xmin is None:
                xmin = x[0]
            else:
                xmin = self.xmin
            if self.xmax is None:
                xmax = x[-1]
            else:
                xmax = self.xmax
            dct['curve_x'] = linspace(xmin, xmax, 1000)
            dct['curve_y'] = self.model(parvalues, dct['curve_x'])
            ndf = len(x) - len(parvalues)
            residuals = self.model(parvalues, x) - y
            dct['chi2'] = sum(power(residuals, 2) / power(dy, 2)) / ndf
        return FitResult(**dct)
