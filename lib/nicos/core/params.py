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

"""Parameter definition helpers and typechecking combinators."""

__version__ = "$Revision$"

import os
import re
import copy

from nicos import session
from nicos.core.errors import ProgrammingError


INFO_CATEGORIES = [
    ('experiment', 'Experiment information'),
    ('sample', 'Sample and alignment'),
    ('instrument', 'Instrument setup'),
    ('offsets', 'Offsets'),
    ('limits', 'Limits'),
    ('precisions', 'Precisions'),
    ('status', 'Instrument status'),
    ('general', 'Instrument state at first scan point'),
]


class Param(object):
    """This class defines the properties of a device parameter.

    The `.Device.parameters` attribute contains a mapping of parameter names to
    instances of this class.

    Attributes (equivalent to constructor arguments):

    - *description*: a concise parameter description.

    - *type*: the parameter type; either a standard Python type (`int`, `float`,
      `str`) or one of the type converter functions from this module that either
      return a value of the correct type, or raises `TypeError` or `ValueError`.

    - *default*: a default value, in case the parameter cannot be read from
      the hardware or the cache.

    - *mandatory*: true if the parameter must be given in the config file.

    - *settable*: true if the parameter can be set by NICOS or the user after
      startup.

    - *volatile*: true if the parameter should always be read from hardware.
      For this, a ``doReadParamname`` method on the device is needed.

    - *unit*: unit of the parameter for informational purposes; in there, the
      substring 'main' is replaced by the device unit when presented.

    - *category*: category of the parameter when returned by `.Device.info()` or
      ``None`` to ignore the parameter.  See `INFO_CATEGORIES` for the list of
      possible categories.

    - *preinit*: whether the parameter must be initialized before
      `.Device.preinit()` is called.

    - *prefercache*: whether on initialization, a value from the cache is
      preferred to a value from the config -- the default is true for
      settable parameters and false for non-settable parameters.

    - *userparam*: whether this parameter should be shown to the user
      (default is True).

    - *chatty*: wether changes of the parameter should produce a message
      (default is False).
    """

    _notset = object()

    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, volatile=False,
                 unit=None, category=None, preinit=False, prefercache=None,
                 userparam=True, chatty=False):
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
        self.chatty = chatty
        self.classname = None  # filled by DeviceMeta

    def __repr__(self):
        return '<Param info>'

    def formatDoc(self):
        txt = 'Parameter: '
        txt += self.description or ''
        txt += '\n'
        if isinstance(self.type, type):
            txt += '\n    * Type: ' + self.type.__name__
        else:
            txt += '\n    * Type: ' + (self.type.__doc__ or '')
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
        if self.chatty:
            txt += '\n    * Will print a message when changed'
        return txt


class Override(object):
    """This class defines the overridden properties of a base class parameter.

    The `.Device.parameter_overrides` attribute contains a mapping of parameter
    names to instances of this class.

    Overriding parameters allows to share parameters with the base class, but
    still have slightly different behavior for the parameters.  For example, for
    a general `.Moveable` device the *unit* parameter is mandatory.  However,
    for some subclasses this will not be necessary, since the unit can either be
    automatically determined from the device, or the value never has any unit.
    Instead of redefining the *unit* parameter in subclasses, you only need to
    override its *mandatory* property in the subclass like this::

        parameter_overrides = {'unit': Override(mandatory=False)}

    The constructor takes all keywords that the `Param` constructor accepts.
    These properties of the parameter are then overridden compared to the base
    class.
    """

    def __init__(self, **kw):
        self._kw = kw

    def apply(self, paraminfo):
        newinfo = copy.copy(paraminfo)
        for attr in self._kw:
            setattr(newinfo, attr, self._kw[attr])
        return newinfo


class Value(object):
    """This class defines the properties of the "value" read from `.Readable`
    and `.Measurable` classes.  Their `.valueInfo` method must return a tuple of
    instances of this class.

    * The *name* parameter is the name of the value.  By convention, if only one
      value is returned, this is the name of the device.  Otherwise, if the
      values are collected from subdevices, the value names should be the
      subdevice names.  In all other cases, they should be called
      "devname.valuename" where *devname* is the device name.

    * The *type* parameter can be one of:

      - ``'counter'`` -- some counter value
      - ``'monitor'`` -- some monitor value
      - ``'time'`` -- some timing value
      - ``'other'`` -- other numeric value
      - ``'error'`` -- standard error for previous value
      - ``'info'`` -- non-numeric info value

    * The *errors* parameter can be one of:

      - ``'none'`` -- no errors known
      - ``'next'`` -- errors are in next value
      - ``'sqrt'`` -- counter-like value: errors are square root

    * The *unit* parameter is the unit of the value, or '' if it has no unit.
      This will generally be ``device.unit`` for Readables.

    * The *fmtstr* parameter selects how to format the value for display.  This
      will generally be ``device.fmtstr`` for Readables.

    * The *active* parameter is reserved.
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

    def copy(self):
        return Value(self.name, self.type, self.errors, self.unit,
                     self.fmtstr, self.active)


# parameter conversion functions

_notset = object()

def convdoc(conv):
    if isinstance(conv, type):
        return conv.__name__
    return conv.__doc__ or ''

class listof(object):

    def __init__(self, conv):
        self.__doc__ = 'a list of %s' % convdoc(conv)
        self.conv = conv

    def __call__(self, val=None):
        val = val if val is not None else list()
        if not isinstance(val, list):
            raise ValueError('value needs to be a list')
        return map(self.conv, val)

class nonemptylistof(object):

    def __init__(self, conv):
        self.__doc__ = 'a non-empty list of %s' % convdoc(conv)
        self.conv = conv

    def __call__(self, val=None):
        if val is None:
            return [self.conv()]
        if not isinstance(val, list):
            raise ValueError('value needs to be a nonempty list')
        if not val:
            raise ValueError('value needs to be a nonempty list')
        return map(self.conv, val)

class tupleof(object):

    def __init__(self, *types):
        if not types:
            raise ProgrammingError('tupleof() needs some types as arguments')
        self.__doc__ = 'a tuple of (' + ', '.join(map(convdoc, types)) + ')'
        self.types = types

    def __call__(self, val=None):
        if val is None:
            return tuple(type() for type in self.types)
        if not isinstance(val, (list, tuple)) or not len(self.types) == len(val):
            raise ValueError('value needs to be a %d-tuple' % len(self.types))
        return tuple(t(v) for (t, v) in zip(self.types, val))

def limits(val=None):
    """ a tuple of lower and upper limit """
    val = val if val is not None else (0, 0)
    if not isinstance(val, (list, tuple)) or len(val) != 2:
        raise ValueError('value must be a list or tuple and have 2 elements')
    ll = float(val[0])
    ul = float(val[1])
    if not ll <= ul:
        raise ValueError('upper limit must be greater then lower limit')
    return (ll, ul)

class dictof(object):

    def __init__(self, keyconv, valconv):
        self.__doc__ = 'a dict of %s keys and %s values' % \
                        (convdoc(keyconv), convdoc(valconv))
        self.keyconv = keyconv
        self.valconv = valconv

    def __call__(self, val=None):
        val = val if val is not None else dict()
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in val.iteritems():
            ret[self.keyconv(k)] = self.valconv(v)
        return ret

class intrange(object):

    def __init__(self, fr, to):
        fr = int(fr)
        to = int(to)
        if not fr <= to:
            raise ValueError('intrange must fulfill from <= to, given was [%f, %f]' % (fr, to))
        self.__doc__ = 'an integer in the range [%d, %d]' % (fr, to)
        self.fr = fr
        self.to = to

    def __call__(self, val=None):
        if val is None:
            return self.fr
        val = int(val)
        if not self.fr <= val <= self.to:
            raise ValueError('value needs to fulfill %d <= x <= %d' % (self.fr, self.to))
        return val

class floatrange(object):

    def __init__(self, fr, to):
        fr = float(fr)
        to = float(to)
        if not fr <= to:
            raise ValueError('floatrange must fulfill from <= to, given was [%f, %f]' % (fr, to))
        self.__doc__ = 'a float in the range [%f, %f]' % (fr, to)
        self.fr = fr
        self.to = to

    def __call__(self, val=None):
        if val is None:
            return self.fr
        val = float(val)
        if not self.fr <= val <= self.to:
            raise ValueError('value needs to fulfill %d <= x <= %d' % (self.fr, self.to))
        return val

class oneof(object):

    def __init__(self, *vals):
        self.__doc__ = 'one of ' + ', '.join(map(repr, vals))
        self.vals = vals

    def __call__(self, val=None):
        if val is None:
            return self.vals[0]
        if val not in self.vals:
            raise ValueError('invalid value: %s, must be one of %s' %
                                 (val, ', '.join(map(repr, self.vals))))
        return val

class oneofdict(object):

    def __init__(self, vals):
        self.__doc__ = 'one of ' + ', '.join(map(repr, vals.values()))
        self.vals = vals

    def __call__(self, val=None):
        if val in self.vals.keys():
            val = self.vals[val]
        elif val not in self.vals.values():
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, self.vals.values()))))
        return val

class none_or(object):

    def __init__(self, conv):
        self.__doc__ = 'None or %s' % convdoc(conv)
        self.conv = conv

    def __call__(self, val=None):
        if val is None:
            return None
        return self.conv(val)

tacodev_re = re.compile(r'^(//[\w.-]+/)?[\w-]+/[\w-]+/[\w-]+$', re.I)

def tacodev(val=None):
    """a valid taco device"""
    if val is None:
        return ''
    val = str(val)
    if not tacodev_re.match(val):
        raise ValueError('%r is not a valid Taco device name' % val)
    return val

tangodev_re = re.compile(r'^(tango:)?//[\w.-]+:[\d]+/[\w-]+/[\w-]+/[\w-]+$', re.I)

def tangodev(val=None):
    """a valid tango device"""
    if val is None:
        return ''
    val = str(val)
    if not tangodev_re.match(val):
        raise ValueError('%r is not a valid Tango device name' % val)
    return val

def control_path_relative(val=''):
    return os.path.join(session.config.control_path, str(val))

def anytype(val=None):
    """any value"""
    return val

def vec3(val=None):
    """a 3-vector"""
    val = val if val is not  None else [0,0,0]
    ret = map(float, val)
    if len(ret) != 3:
        raise ValueError('value needs to be a 3-element vector')
    return ret
