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

import sys
import linecache
import traceback

from nicm.errors import ConfigurationError, ProgrammingError


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
            param = param.lower()
            # check validity of parameter info
            if not isinstance(info, tuple) or len(info) != 4:
                raise ProgrammingError('%r device %r configuration '
                                       ' parameter info should be a '
                                       '4-tuple' % (name, param))
            def getter(self, param=param):
                methodname = 'doGet' + param.title()
                if hasattr(self, methodname):
                    return getattr(self, methodname)()
                else:
                    return self._params[param.lower()]
            def setter(self, value, param=param):
                pconv = self.parameters[param][0]
                try:
                    value = pconv(value)
                except ValueError, err:
                    raise ConfigurationError(
                        self, '%r is an invalid value for parameter %s: %s' %
                        (value, param, err))
                methodname = 'doSet' + param.title()
                if hasattr(self, methodname):
                    getattr(self, methodname)(value)
                else:
                    raise ConfigurationError(
                        self, 'cannot set the %s parameter' % param)
                self._changedparams.add(param)
            setattr(newtype, param, property(getter, setter, doc=info[2]))
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

def listof(conv):
    def converter(val):
        if not isinstance(val, list):
            raise ValueError('value needs to be a list')
        return map(conv, val)
    return converter

def tacodev(val):
    # XXX check for valid taco device name
    return str(val)

def any(val):
    return val
