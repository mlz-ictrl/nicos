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

"""Parameter definition helpers and typechecking combinators."""

__version__ = "$Revision$"

import os
import re
import copy

from nicos.core.errors import ProgrammingError


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

    *type* can be one of:

    - ``counter`` -- some counter value
    - ``monitor`` -- some monitor value
    - ``time`` -- some timing value
    - ``other`` -- other numeric value
    - ``error`` -- standard error for previous value
    - ``info`` -- non-numeric info value

    *errors* can be one of:

    - ``none`` -- no errors known
    - ``next`` -- errors are in next value
    - ``sqrt`` -- counter-like value: errors are square root
    """

    def __init__(self, name, type='other', errors='none', unit='',
                 fmtstr='%.3f', active=True):
        if type not in ('counter', 'monitor', 'time', 'other', 'error', 'info'):
            raise ProgrammingError('invalid Value type parameter')
        if errors not in ('none', 'next', 'sqrt'):
            raise ProgrammingError('invalid Value errors parameter')
        self.name = name
        self.type = type
        self.errors = errors
        self.unit = unit
        self.fmtstr = fmtstr
        self.active = active

    def __repr__(self):
        return 'value %r' % self.name


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
        raise ValueError('%r is not a valid Taco device name' % val)
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

def none_or(conv):
    def converter(val=None):
        if val is None:
            return None
        return conv(val)
    converter.__doc__ = 'None or %s' % convdoc(conv)
    return converter
