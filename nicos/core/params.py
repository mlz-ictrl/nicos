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

"""Parameter definition helpers and typechecking combinators."""

import re
import copy
from os import path

from nicos.utils import readonlylist, readonlydict
from nicos.core.errors import ProgrammingError, ConfigurationError
from nicos.pycompat import iteritems, text_type, string_types


INFO_CATEGORIES = [
    ('experiment', 'Experiment information'),
    ('sample', 'Sample and alignment'),
    ('instrument', 'Instrument setup'),
    ('offsets', 'Offsets'),
    ('limits', 'Limits'),
    ('precisions', 'Precisions/tolerances'),
    ('status', 'Devices in busy or error status'),
    ('general', 'Device positions and sample environment state'),
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

    - *ext_desc*: extended description for the generated documentation
      (default is '').

      For long extended descriptions, this can also be set after the
      parameters block::

          parameters = {
              'param': Param(...),
              ...
          }

          parameters['param'].ext_desc = '''
          long description
          '''
    """

    _notset = object()

    # pylint: disable=W0622
    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, volatile=False,
                 unit=None, category=None, preinit=False, prefercache=None,
                 userparam=True, chatty=False, ext_desc=''):
        self.type = fixup_conv(type)
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
        self.ext_desc = ext_desc
        self.classname = None  # filled by DeviceMeta

    def __repr__(self):
        return '<Param info>'

    def serialize(self):
        return self.__dict__

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


class Attach(object):
    """Specifies required properties of the attached dev(s) of an device class.

    The `.Device.attached_devices` attribute contains a mapping of internal
    names of attached devices to instances of this class.
    During device creation, attached devices are stored as a mapping of
    internal device name to the attached device itself as `.Device._adevs`.
    Attached devices also contain a set `.Devices._sdevs` which contains
    the names of devices using this particular device as an attached device
    (two way linkage).

    Attributes (equivalent to constructor arguments):

    - *description*: a concise description of the attached devices.

    - *devclass*: the class, the attached Device must be a subclass of.
      This is used to restrict the possible configurations to devices
      possessing a certain interface.  If an attached device is specified
      in the setup file which is not a valid subclass, a
      `ConfigurationError` is raised.

    - *optional*: if True, the attached device does not need to be specified
      in the config file and is assumed to be of the value None.
      Defaults to False.

    - *multiple*: Either False, specifying that there shall be exactly one
      attached device (default), or True, allowing any number (1..N)
      attached devices, an integer requesting exactly that many devices
      or a nonempty list of integers, listing the allowed device counts.

    If multiple is a list containing more than one number and optional is true,
    the list of devices is filled with None's until it is at least as long
    as the max of multiple.

    Only description and class are mandatory parameters.
    """
    def __init__(self, description, devclass, optional=False, multiple=False):
        def complain(multiple, test):
            raise ProgrammingError('devclass %r (%s): multiple should be a '
                                   'bool or a list of integers, but is %r '
                                   '(testing for %s)' % (devclass.__name__,
                                                         description, multiple,
                                                         test))
        # first check all our parameters.
        single = False

        # Do not change the order since bool is a subclass of int
        # see: https://docs.python.org/2/library/functions.html#bool
        if isinstance(multiple, bool):
            single = not multiple
            if single:
                # map False to [1] (single), whereas true is an unlimited list
                # which could not be handled by a python list object
                multiple = [1]
        elif isinstance(multiple, int):
            multiple = [multiple]

        # allowed non-list values are converted to a list above already...
        if isinstance(multiple, list):
            if len(multiple) == 0:
                complain(multiple, 'list should be non-empty')
            for item in multiple:
                try:
                    if item != int(item):
                        complain(multiple, 'list items should be int\'s')
                    if item < 0:
                        complain(multiple, 'list items should be positive')
                except (TypeError, ValueError):
                    complain(multiple, 'list items should be numbers')
        elif not (isinstance(multiple, bool) and multiple):
            complain(multiple, 'is-a-list')
        # multiple is now True or a list of integers
        if not isinstance(optional, bool):
            raise ProgrammingError('optional must be a boolean')
        # now set member values
        self.description = description
        self.devclass = devclass
        self.optional = optional
        self.multiple = multiple
        self.single = single

    def check(self, dev, aname, configargs):
        """Checks if the given arguments are valid for this entry.

        Also returns a list of all attached devices which should be created.
        May raise a configurationError, if something is wrongly configured.
        """
        def check_count(multiple, optional, count):
            if (count == 0) and optional:
                return True
            # Don't change it to more pythonic style since we want to check for
            # the boolean 'True' value
            if self.multiple == True:  # nopep8
                return count > 0
            return (count in multiple)

        if configargs:
            if isinstance(configargs, (tuple, list)):
                args = list(configargs)
            else:
                args = [configargs]
        else:
            args = []

        if self.single:
            if check_count(self.multiple, self.optional, len(args)):
                return args or [None]
            raise ConfigurationError(dev, "device misses device %r in "
                                     "configuration" % aname)

        # Don't change it to more pythonic style since we want to check for
        # the boolean 'True' value
        if self.multiple == True:  # nopep8
            if check_count(self.multiple, self.optional, len(args)):
                return args
            raise ConfigurationError(dev, "wrong number of devices (%d) for %r"
                                     " in configuration (specified=%r)" %
                                     (len(args), aname, args))

        # here we have:
        # - multiple is a list
        # - args has at least one real entry
        mindevs = min(self.multiple)
        maxdevs = max(self.multiple)
        # if optional, fill up to maxdevs with None
        if self.optional:
            args.extend([None] * (maxdevs - len(args)))

        # check number of devices
        if len(args) < mindevs:
            raise ConfigurationError(dev, "not enough devices (%d<%d) for %r"
                                     " in configuration (specified=%r)" %
                                     (len(args), mindevs, aname, args))
        if len(args) > maxdevs:
            raise ConfigurationError(dev, "too many devices (%d>%d) for %r in "
                                          "configuration (specified=%r)" %
                                          (len(args), maxdevs, aname, args))

        if check_count(self.multiple, self.optional, len(args)):
            return args
        raise ConfigurationError(dev, "wrong number of devices (%d) for %r in "
                                      "configuration (specified=%r)" %
                                      (len(args), aname, args))

    def __repr__(self):
        s = 'Attach(%r, %s.%s' % (self.description,
                                  self.devclass.__module__,
                                  self.devclass.__name__)
        if self.multiple:
            s += ', multiple=%s' % self.multiple
        if self.optional:
            s += ', optional=%r' % self.optional
        return s + ')'


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

    # pylint: disable=W0622
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


def fixup_conv(conv):
    """Fix-up a single converter type.

    Currently this converts "str" to "string" which is a version that supports
    Unicode strings by encoding to str on Python 2.
    """
    if conv is str:
        return string
    return conv


def string(s=None):
    """a string"""
    if s is None:
        return ''
    try:
        return str(s)
    except UnicodeError:
        # on Python 2, this converts Unicode to our preferred encoding
        if isinstance(s, text_type):
            return s.encode('utf-8')
        raise


class listof(object):

    def __init__(self, conv):
        self.__doc__ = 'a list of %s' % convdoc(conv)
        if conv is str:
            conv = string
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        val = val if val is not None else []
        if not isinstance(val, (list, tuple)):
            raise ValueError('value needs to be a list')
        return readonlylist(map(self.conv, val))


class nonemptylistof(object):

    def __init__(self, conv):
        self.__doc__ = 'a non-empty list of %s' % convdoc(conv)
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        if val is None:
            return readonlylist([self.conv()])
        if not isinstance(val, (list, tuple)) or len(val) < 1:
            raise ValueError('value needs to be a nonempty list')
        return readonlylist(map(self.conv, val))


def nonemptystring(s):
    """a non-empty string"""
    if not isinstance(s, string_types) or s == '':
        raise ValueError('must be a non-empty string!')
    return s


class tupleof(object):

    def __init__(self, *types):
        if not types:
            raise ProgrammingError('tupleof() needs some types as arguments')
        self.__doc__ = 'a tuple of (' + ', '.join(map(convdoc, types)) + ')'
        self.types = [fixup_conv(typeconv) for typeconv in types]

    def __call__(self, val=None):
        if val is None:
            return tuple(type() for type in self.types)
        if not isinstance(val, (list, tuple)) or not len(self.types) == len(val):
            raise ValueError('value needs to be a %d-tuple' % len(self.types))
        return tuple(t(v) for (t, v) in zip(self.types, val))


def limits(val=None):
    """a tuple of lower and upper limit"""
    val = val if val is not None else (0, 0)
    if not isinstance(val, (list, tuple)) or len(val) != 2:
        raise ValueError('value must be a list or tuple and have 2 elements')
    ll = float(val[0])
    ul = float(val[1])
    if not ll <= ul:
        raise ValueError('upper limit must be greater than lower limit')
    return (ll, ul)


class dictof(object):

    def __init__(self, keyconv, valconv):
        self.__doc__ = 'a dict of %s keys and %s values' % \
                       (convdoc(keyconv), convdoc(valconv))
        self.keyconv = fixup_conv(keyconv)
        self.valconv = fixup_conv(valconv)

    def __call__(self, val=None):
        val = val if val is not None else {}
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        ret = {}
        for k, v in iteritems(val):
            ret[self.keyconv(k)] = self.valconv(v)
        return readonlydict(ret)


class intrange(object):

    def __init__(self, fr, to):
        if isinstance(fr, bool) or isinstance(to, bool):
            raise ValueError('intrange works with integer numbers! '
                             'A boolean was given!')
        fr = int(fr)
        to = int(to)
        if not fr <= to:
            raise ValueError('intrange must fulfill from <= to, given was '
                             '[%f, %f]' % (fr, to))
        self.__doc__ = 'an integer in the range [%d, %d]' % (fr, to)
        self.fr = fr
        self.to = to

    def __call__(self, val=None):
        if val is None:
            return self.fr
        if isinstance(val, bool):
            raise ValueError('value is not an integer!')
        val = int(val)
        if not self.fr <= val <= self.to:
            raise ValueError('value needs to fulfill %d <= x <= %d' %
                             (self.fr, self.to))
        return val


class floatrange(object):

    def __init__(self, fr, to=None):
        fr = float(fr)
        if to is not None:
            to = float(to)
            if not fr <= to:
                raise ValueError('floatrange must fulfill from <= to, given was '
                                 '[%f, %f]' % (fr, to))
            self.__doc__ = 'a float in the range [%f, %f]' % (fr, to)
        else:
            self.__doc__ = 'a float >= %f' % fr
        self.fr = fr
        self.to = to

    def __call__(self, val=None):
        if val is None:
            return self.fr
        val = float(val)
        if self.to is not None:
            if not self.fr <= val <= self.to:
                raise ValueError('value needs to fulfill %d <= x <= %d' %
                                 (self.fr, self.to))
        else:
            if not self.fr <= val:
                raise ValueError('value needs to fulfill %d <= x' % self.fr)
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
        if val in self.vals:
            val = self.vals[val]
        elif val not in self.vals.values():
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, self.vals.values()))))
        return val


class none_or(object):

    def __init__(self, conv):
        self.__doc__ = 'None or %s' % convdoc(conv)
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        if val is None:
            return None
        return self.conv(val)


nicosdev_re = re.compile(r'^[a-z_][a-z_0-9]*$', re.I)  # valid Python identifier


def nicosdev(val=None):
    """a valid NICOS device name"""
    if not val:
        return ''
    val = str(val)
    if not nicosdev_re.match(val):
        raise ValueError('%r is not a valid NICOS device name' % val)
    return val


tacodev_re = re.compile(r'^(//[\w.-]+/)?[\w-]+/[\w-]+/[\w-]+$', re.I)


def tacodev(val=None):
    """a valid taco device"""
    if val in ('', None):
        return ''
    val = str(val)
    if not tacodev_re.match(val):
        raise ValueError('%r is not a valid Taco device name' % val)
    return val

# allow only tango device names according tango spec
# http://www.esrf.eu/computing/cs/tango/tango_doc/kernel_doc/ds_prog/node13.html
# without any attributes and properties
# the device name must begin with 'tango://'
tangodev_re = re.compile(
    r'^(tango://)([\w.-]+:[\d]+/)?([\w-]+/){2}[\w-]+(#dbase=(no|yes))?$', re.I)
#   r'^(tango://)([\w.-]+:[\d]+/)?([\w-]+/){2}[\w-]+(/[\w-]+)?(->[\w-]+)?(#dbase=(no|yes))?$', re.I)


def tangodev(val=None):
    """a valid tango device"""
    if val in ('', None):
        return ''
    val = str(val)
    if not val.startswith('tango://'):
        raise ValueError('%r should start with "tango://"' % val)
    if not tangodev_re.match(val):
        raise ValueError('%r is not a valid Tango device name' % val)
    return val

# see http://stackoverflow.com/questions/3217682/checking-validity-of-email-in-django-python
# for source

mailaddress_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"                # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+([A-Z]{2,99}|XN[A-Z0-9-]+)\.?$',   # domain
    re.IGNORECASE)


def mailaddress(val=None):
    """a valid mail address"""
    if val in ('', None):
        return ''
    val = text_type(val)
    parts = val.split('@')
    parts[-1] = parts[-1].encode('idna').decode('ascii')
    val = '@'.join(parts)
    if '>' in val and not val.strip().endswith('>'):
        raise ValueError('%r is not a valid email address' % val)
    if not mailaddress_re.match(val.strip().partition('<')[-1].rpartition('>')[0] or val):
        raise ValueError('%r is not a valid email address' % val)
    return val


def absolute_path(val=''):
    """an absolute file path"""
    val = str(val)
    if path.isabs(val):
        return val
    raise ValueError('%r is not a valid absolute path (should start with %r)' %
                     (val, path.sep))


def relative_path(val=''):
    """a relative path, may not use ../../.. tricks"""
    val = path.normpath(str(val))
    if path.isabs(val):
        raise ValueError('%r is not a valid relative path (should NOT start '
                         'with %r)' % (val, path.sep))
    if val[:2] != '..':
        return val
    raise ValueError('%r is not a valid relative path (traverses outside)' % val)


def expanded_path(val=''):
    return path.expanduser(path.expandvars(val))


def subdir(val=''):
    """a relative subdir (a string NOT containing any path.sep)"""
    val = str(val)
    for sep in [path.sep, '\\', '/']:
        if sep in val:
            raise ValueError('%r is not a valid subdirectory (contains a %r)' %
                             (val, sep))
    return val


def anytype(val=None):
    """any value"""
    return val


def vec3(val=None):
    """a 3-vector"""
    val = val if val is not None else [0, 0, 0]
    ret = [float(v) for v in val]
    if len(ret) != 3:
        raise ValueError('value needs to be a 3-element vector')
    return readonlylist(ret)

ipv4_re = re.compile(
    r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
)


def ipv4(val='0.0.0.0'):
    """a IP v4 address"""
    if val in ('', None):
        return ''
    val = str(val)
    res = ipv4_re.match(val)
    if not res or res.group() != res.string:
        raise ValueError('%r is not a valid IPv4 address' % val)
    return val


def host(val=''):
    """a host[:port] value"""
    if not isinstance(val, string_types):
        raise ValueError('must be a string!')
    if val.count(':') > 1:
        raise ValueError('%r is not in the form host_name[:port]')
    if ':' in val:
        _, p = val.split(':')
        try:
            p = int(p)
            if not 0 < p < 65536:
                raise ValueError()
        except ValueError:
            raise ValueError('%r does not contain a valid port number' % val)
    return val
