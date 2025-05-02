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

"""Parameter definition helpers and typechecking combinators."""

import copy
import os
import re
from os import path

import numpy as np

from nicos.core.errors import ConfigurationError, ProgrammingError
from nicos.utils import Secret, decodeAny, parseHostPort, readonlydict, \
    readonlylist

INFO_CATEGORIES = [
    ('experiment', 'Experiment information'),
    ('sample', 'Sample and alignment'),
    ('instrument', 'Instrument setup'),
    ('offsets', 'Offsets'),
    ('limits', 'Limits'),
    ('precisions', 'Precisions/tolerances'),
    ('status', 'Device status'),
    ('general', 'Device positions and sample environment state'),
    ('presets', 'Detector preset information'),
    ('result', 'Updated values after counting'),
]


class Param:
    """This class defines the properties of a device parameter.

    The `.Device.parameters` attribute contains a mapping of parameter names to
    instances of this class.

    Attributes (equivalent to constructor arguments):

    - *description*: a concise parameter description.

    - *type*: the parameter type; either a standard Python type (`int`,
      `float`, `str`) or one of the :ref:`type-converter-functions` from this
      module that either return a value of the correct type, or raises
      `TypeError` or `ValueError`.

    - *default*: a default value, in case the parameter cannot be read from
      the hardware or the cache.

    - *mandatory*: true if the parameter must be given in the config file.

    - *settable*: true if the parameter can be set by NICOS or the user after
      startup.

    - *volatile*: true if the parameter should always be read from hardware.
      For this, a ``doReadParamname`` method on the device is needed.

    - *unit*: unit of the parameter for informational purposes; in there, the
      substring 'main' is replaced by the device unit when presented.

    - *fmtstr*: how to format the parameter in output.  If 'main', the fmtstr
      for the main device value is used instead (also works for tuples of
      values).

    - *category*: category of the parameter when returned by `.Device.info()`
      or ``None`` to ignore the parameter.  See `INFO_CATEGORIES` for the list
      of possible categories.

    - *preinit*: whether the parameter must be initialized before
      `.Device.preinit()` is called.

    - *prefercache*: whether on initialization, a value from the cache is
      preferred to a value from the config -- the default is true for
      settable parameters and false for non-settable parameters.

    - *internal*: true if the parameter should not be given in the config file
      because it is handled internally in the device implementation (default
      is False).

    - *userparam*: whether this parameter should be shown to the user
      (default is True for non *internal* parameters otherwise False).

    - *chatty*: whether changes of the parameter should produce a message
      (default is False).

    - *no_sim_restore*: whether the parameter should not be restored to its
      current value in a simulation copy (default is False).

    - *ext_desc*: extended description for the generated documentation
      (default is '').

      For long extended descriptions, this can also be set after the
      parameters block::

          parameters = {
              'param': Param(...),
              ...
          }

          parameters['param'].ext_desc = \"\"\"
          long description
          \"\"\"
    """

    _notset = object()

    # pylint: disable=redefined-builtin,too-many-arguments
    def __init__(self, description, type=float, default=_notset,
                 mandatory=False, settable=False, volatile=False,
                 unit=None, fmtstr='%r', category=None, preinit=False,
                 prefercache=None, userparam=None, internal=False,
                 chatty=False, no_sim_restore=False, ext_desc=''):
        self.type = fixup_conv(type)
        if default is self._notset:
            default = type()
        self.default = default
        self.mandatory = mandatory
        self.settable = settable
        self.volatile = volatile
        self.unit = unit
        self.fmtstr = fmtstr
        self.category = category
        self.description = description
        self.preinit = preinit
        self.prefercache = prefercache
        self.internal = internal
        self.chatty = chatty
        self.no_sim_restore = no_sim_restore
        self.ext_desc = ext_desc
        self.classname = None  # filled by DeviceMeta

        if internal and mandatory:
            raise ProgrammingError("Ambiguous parameter settings detected. "
                                   "'internal' and 'mandatory' must be used "
                                   "exclusively.")

        if userparam is None:  # implicit settings
            self.userparam = not self.internal
        else:
            self.userparam = userparam

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
                txt += "\n    * Unit: 'main' -> get unit from Device"
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
        if self.no_sim_restore:
            txt += '\n    * Will not be restored in simulation copy'
        return txt


class Override:
    """This class defines the overridden properties of a base class parameter.

    The `.Device.parameter_overrides` attribute contains a mapping of parameter
    names to instances of this class.

    Overriding parameters allows to share parameters with the base class, but
    still have slightly different behavior for the parameters.  For example,
    for a general `.Moveable` device the *unit* parameter is mandatory.
    However, for some subclasses this will not be necessary, since the unit can
    either be automatically determined from the device, or the value never has
    any unit.  Instead of redefining the *unit* parameter in subclasses, you
    only need to override its *mandatory* property in the subclass like this::

        parameter_overrides = {'unit': Override(mandatory=False)}

    The constructor takes all keywords that the `Param` constructor accepts.
    These properties of the parameter are then overridden compared to the base
    class.
    """

    def __init__(self, **kw):
        self._kw = kw

    def apply(self, paraminfo):
        newinfo = copy.copy(paraminfo)
        for attr, val in self._kw.items():
            setattr(newinfo, attr, val)
        return newinfo


class Attach:
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

    - *multiple*: either False, specifying that there shall be exactly one
      attached device (default), or True, allowing any number (1..N)
      attached devices, an integer requesting exactly that many devices
      or a nonempty list of integers, listing the allowed device counts.

    - *optional*: if True, the attached device does not need to be specified in
      the setup.  At runtime the device reference will be None.  Defaults to
      False.

    - *missingok*: if True, the device(s) mentioned in the setup can be missing
      from the session's configured devices.  The device reference will be None
      instead.  If a device is configured, but cannot be created due to an
      error, the error will be propagated.  Defaults to False.

    - *dontfix*: if True, the device(s) mentioned in the setup won't be fixed
      when this device is fixed. Defaults to False.

    Note: *optional* specifies that devices need not be configured, whereas
    *missingok* specifies that devices must be configured, but need not exist
    at runtime.  The two options can be combined.

    If multiple is a list containing more than one number and optional is true,
    the list of devices is filled with None's until it is at least as long
    as the max of multiple.

    Only description and class are mandatory parameters.
    """
    def __init__(self, description, devclass, optional=False, multiple=False,
                 missingok=False, dontfix=False):
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
            if not multiple:
                complain(multiple, 'list should be non-empty')
            for item in multiple:
                try:
                    if item != int(item):
                        complain(multiple, "list items should be int's")
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
        self.missingok = missingok
        self.dontfix = dontfix

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
            if self.multiple is True:
                return count > 0
            return count in multiple

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
            raise ConfigurationError(dev, 'device misses device %r in '
                                     'configuration' % aname)

        # Don't change it to more pythonic style since we want to check for
        # the boolean 'True' value
        if self.multiple is True:
            if check_count(self.multiple, self.optional, len(args)):
                return args
            raise ConfigurationError(dev, 'wrong number of devices (%d) for %r'
                                     ' in configuration (specified=%r)' %
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
            raise ConfigurationError(dev, 'not enough devices (%d<%d) for %r'
                                     ' in configuration (specified=%r)' %
                                     (len(args), mindevs, aname, args))
        if len(args) > maxdevs:
            raise ConfigurationError(dev, 'too many devices (%d>%d) for %r in '
                                          'configuration (specified=%r)' %
                                          (len(args), maxdevs, aname, args))

        if check_count(self.multiple, self.optional, len(args)):
            return args
        raise ConfigurationError(dev, 'wrong number of devices (%d) for %r in '
                                      'configuration (specified=%r)' %
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


class Value:
    """This class defines the properties of the "value" read from `.Readable`
    and `.Measurable` classes.  Their ``.valueInfo()`` method must return a
    tuple of instances of this class.

    * The *name* parameter is the name of the value.  By convention, if only
      one value is returned, this is the name of the device.  Otherwise, if the
      values are collected from subdevices, the value names should be the
      subdevice names.  In all other cases, they should be called
      "devname.valuename" where *devname* is the device name.

    * The *type* parameter can be one of:

      - ``'counter'`` -- some counter value
      - ``'monitor'`` -- some monitor value
      - ``'time'`` -- some timing value
      - ``'other'`` -- other numeric value
      - ``'error'`` -- standard error for previous value
      - ``'filename'`` -- filename of the last saved file
      - ``'info'`` -- non-numeric info value

    * The *errors* parameter can be one of:

      - ``'none'`` -- no errors known
      - ``'next'`` -- errors are in next value
      - ``'sqrt'`` -- counter-like value: errors are square root

    * The *unit* parameter is the unit of the value, or '' if it has no unit.
      This will generally be ``device.unit`` for Readables.

    * The *fmtstr* parameter selects how to format the value for display.  This
      will generally be ``device.fmtstr`` for Readables.
    """

    # pylint: disable=redefined-builtin
    def __init__(self, name, type='other', errors='none', unit='',
                 fmtstr='%.3f'):
        if type not in ('counter', 'monitor', 'time', 'other', 'error',
                        'filename', 'info'):
            raise ProgrammingError('invalid Value type parameter')
        if errors not in ('none', 'next', 'sqrt'):
            raise ProgrammingError('invalid Value errors parameter')
        self.name = name
        self.type = type
        self.errors = errors
        self.unit = unit
        self.fmtstr = fmtstr

    def __repr__(self):
        return 'value %r' % self.name

    def copy(self):
        return Value(self.name, self.type, self.errors, self.unit, self.fmtstr)


class ArrayDesc:
    """Defines the properties of an array detector result.

    An array type consists of these attributes:

    * name, a name for the array
    * shape, a tuple of lengths in 1 to N dimensions arranged as for C order
      arrays, i.e. (..., t, y, x), which is also the numpy shape
    * dtype, the data type of a single value, in numpy format
    * dimnames, a list of names for each dimension

    The class can try to determine if a given image-type can be converted
    to another.
    """

    def __init__(self, name, shape, dtype, dimnames=None):
        """Creates a datatype with given (numpy) shape and (numpy) data format.

        Also stores the 'names' of the used dimensions as a list called
        dimnames.  Defaults to 'X', 'Y' for 2D data and 'X', 'Y', 'Z' for 3D
        data.
        """
        self.name = name
        self.shape = shape
        self.dtype = np.dtype(dtype)
        if dimnames is None:
            dimnames = ['X', 'Y', 'Z', 'T', 'E', 'U', 'V', 'W'][:len(shape)]
        self.dimnames = dimnames

    def __repr__(self):
        return 'ArrayDesc(%r, %r, %r, %r)' % (self.name, self.shape,
                                              self.dtype, self.dimnames)

    def copy(self):
        return ArrayDesc(self.name, self.shape, self.dtype, self.dimnames)


# parameter conversion functions

_notset = object()


def convdoc(conv):
    if isinstance(conv, type):
        return conv.__name__
    return (conv.__doc__.splitlines() or [''])[0].strip()


def fixup_conv(conv):
    """Fix-up a single converter type.

    This changes `str` to `string`, a converter that decodes bytes instead of
    converting them using `repr`, and `bool` to `boolean`, which refuses to
    convert strings due to the trap of ``'False'`` being true.
    """
    if conv is str:
        return string
    elif conv is bool:
        return boolean
    return conv


def string(s=None):
    """a string"""
    if s is None:
        return ''
    if isinstance(s, bytes):
        # str(s) would result in the string "b'...'"
        return decodeAny(s)
    return str(s)


def boolean(v=None):
    """a boolean value"""
    if isinstance(v, str):
        raise ValueError('please use True or False without quotes, or 1/0)')
    return bool(v)


class listof:

    def __init__(self, conv):
        self.__doc__ = 'a list of %s' % convdoc(conv)
        if conv is str:
            conv = string
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        val = val if val is not None else []
        if not isinstance(val, (list, tuple, np.ndarray)):
            raise ValueError('value needs to be a list')
        return readonlylist(map(self.conv, val))


class nonemptylistof:

    def __init__(self, conv):
        self.__doc__ = 'a non-empty list of %s' % convdoc(conv)
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        if val is None:
            return readonlylist([self.conv()])
        if not isinstance(val, (list, tuple, np.ndarray)) or len(val) < 1:
            raise ValueError('value needs to be a nonempty list')
        return readonlylist(map(self.conv, val))


def nonemptystring(s=Ellipsis):
    """a non-empty string"""
    if s is Ellipsis:
        # used for setting the internal default if no default is given
        return None
    if not (s and isinstance(s, str)):
        raise ValueError('must be a non-empty string!')
    return s


class tupleof:

    def __init__(self, *types):
        if not types:
            raise ProgrammingError('tupleof() needs some types as arguments')
        self.__doc__ = 'a tuple of (' + ', '.join(map(convdoc, types)) + ')'
        self.types = [fixup_conv(typeconv) for typeconv in types]

    def __call__(self, val=None):
        if val is None:
            return tuple(type() for type in self.types)
        if not isinstance(val, (list, tuple, np.ndarray)) or \
           not len(self.types) == len(val):
            raise ValueError('value needs to be a %d-tuple' % len(self.types))
        return tuple(t(v) for (t, v) in zip(self.types, val))


def limits(val=None):
    """a tuple of lower and upper limit"""
    val = val if val is not None else (0, 0)
    if not isinstance(val, (list, tuple, np.ndarray)) or len(val) != 2:
        raise ValueError('value must be a list or tuple and have 2 elements')
    ll = float(val[0])
    ul = float(val[1])
    if ll > ul:
        raise ValueError('upper limit must be greater than lower limit')
    return (ll, ul)


class dictof:

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
        for k, v in val.items():
            ret[self.keyconv(k)] = self.valconv(v)
        return readonlydict(ret)


class dictwith:

    def __init__(self, **convs):
        self.__doc__ = 'a dict with the following keys: ' + \
            ', '.join('%s: %s' % (k, convdoc(c)) for k, c in convs.items())
        self.keys = set(convs)
        self.convs = {k: fixup_conv(conv) for (k, conv) in convs.items()}

    def __call__(self, val=None):
        if val is None:
            return {k: conv() for k, conv in self.convs.items()}
        if not isinstance(val, dict):
            raise ValueError('value needs to be a dict')
        vkeys = set(val)
        msgs = []
        if vkeys - self.keys:
            msgs.append('unknown keys: %s' % (vkeys - self.keys))
        if self.keys - vkeys:
            msgs.append('missing keys: %s' % (self.keys - vkeys))
        if msgs:
            raise ValueError('Key mismatch in dictionary: ' + ', '.join(msgs))
        ret = {}
        for k in self.keys:
            ret[k] = self.convs[k](val[k])
        return readonlydict(ret)


class intrange:

    def __init__(self, fr, to):
        if isinstance(fr, bool) or isinstance(to, bool):
            raise ValueError('intrange works with integer numbers! '
                             'A boolean was given!')
        fr = int(fr)
        to = int(to)
        if fr > to:
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


class floatrange:

    def __init__(self, fr, to=None):
        fr = float(fr)
        if to is not None:
            to = float(to)
            if fr > to:
                raise ValueError('floatrange must fulfill from <= to, given '
                                 'was [%f, %f]' % (fr, to))
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
                raise ValueError('value needs to fulfill %f <= x <= %f' %
                                 (self.fr, self.to))
        elif self.fr > val:
            raise ValueError('value needs to fulfill %f <= x' % self.fr)
        return val


class nonzero:
    """a nonzero number value"""

    def __init__(self, conv, default=None):
        self.__doc__ = 'Nonzero value of %s' % convdoc(conv)
        self.conv = fixup_conv(conv)
        # inital check for default value
        try:
            default_ = (default or conv()) or 1
            self.default = conv(default_)
        except ValueError as exc:
            raise ValueError(f'{default} is no good default value for {conv}, '
                              'please choose a valid nonzero value!') from exc

    def __call__(self, val=None):
        if val is None:
            return self.default
        if (val := self.conv(val)) == 0:
            raise ValueError('value needs to be != 0')
        return val


# in case the impl. of nonzero ever changes, divisor defaults to 1 explicitly
divisor = nonzero(float, 1)


class setof:

    def __init__(self, *vals):
        self.__doc__ = 'a (sub)set of ' + ', '.join(map(repr, vals))
        self.vals = frozenset(vals)

    def __call__(self, val=None):
        if val is None:
            return frozenset()
        val = frozenset(val)
        if val.difference(self.vals):
            raise ValueError('invalid value: %s, may only contain a (sub)set '
                             'of %s' % (val, ', '.join(map(repr, self.vals))))
        return val


class oneof:

    def __init__(self, *vals):
        self.__doc__ = 'one of ' + ', '.join(map(repr, vals))
        self.vals = vals

    def __call__(self, val=None):
        if val is None:
            if self.vals:
                return self.vals[0]
            return None
        if val not in self.vals:
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, self.vals))))
        return val


class oneofdict:

    def __init__(self, vals):
        self.__doc__ = 'one of ' + ', '.join(map(repr, vals.values()))
        self.vals = vals

    def __call__(self, val=None):
        if val is None:
            return None
        if val in self.vals:
            val = self.vals[val]
        elif val not in self.vals.values():
            raise ValueError('invalid value: %s, must be one of %s' %
                             (val, ', '.join(map(repr, self.vals.values()))))
        return val


class oneofdict_or:
    def __init__(self, named_vals, validator):
        self.conv = fixup_conv(validator)
        self.__doc__ = 'one of ' + ', '.join(map(repr, named_vals)) + \
            ', or ' + self.conv.__doc__
        self.named_vals = {k: self.conv(v) for (k, v) in named_vals.items()}

    def __call__(self, val=None):
        return self.conv(self.named_vals.get(val, val))


class none_or:

    def __init__(self, conv):
        self.__doc__ = 'None or %s' % convdoc(conv)
        self.conv = fixup_conv(conv)

    def __call__(self, val=None):
        if val is None:
            return None
        return self.conv(val)


nicosdev_re = re.compile(r'^[a-z_][a-z_0-9]*(\.[a-z_][a-z_0-9]*)?$', re.I)


def nicosdev(val=None):
    """a valid NICOS device name"""
    if not val:
        return ''
    val = string(val)
    if not nicosdev_re.match(val):
        raise ValueError('%r is not a valid NICOS device name' % val)
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
    val = string(val)
    if not val.startswith('tango://'):
        raise ValueError('%r should start with "tango://"' % val)
    if not tangodev_re.match(val):
        raise ValueError('%r is not a valid Tango device name' % val)
    return val


# Valid characters for PV-names are documented in the EPICS base manual:
#   http://www.aps.anl.gov/epics/base/R3-15/3-docs/AppDevGuide/node7.html
pvname_re = re.compile(r'^[a-z0-9_:\.\[\]<>;-]+$', re.IGNORECASE)


def pvname(val=None):
    """a valid EPICS PV-name"""
    if val in ('', None):
        return ''

    val = string(val)
    if not pvname_re.match(val):
        raise ValueError('%r is not a valid PV name' % val)
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
    val = string(val)
    parts = val.split('@')
    parts[-1] = parts[-1].encode('idna').decode('ascii')
    val = '@'.join(parts)
    if '>' in val and not val.strip().endswith('>'):
        raise ValueError('%r is not a valid email address' % val)
    if not mailaddress_re.match(
       val.strip().partition('<')[-1].rpartition('>')[0] or val):
        raise ValueError('%r is not a valid email address' % val)
    return val


def absolute_path(val=path.sep):
    """an absolute file path"""
    val = string(val)
    if path.isabs(val):
        return val
    raise ValueError('%r is not a valid absolute path (should start with %r)' %
                     (val, path.sep))


def relative_path(val=''):
    """a relative path, may not use ../../.. tricks"""
    val = path.normpath(string(val))
    if path.isabs(val):
        raise ValueError('%r is not a valid relative path (should NOT start '
                         'with %r)' % (val, path.sep))
    if val[:2] != '..':
        return val
    raise ValueError('%r is not a valid relative path (traverses outside)' %
                     val)


def expanded_path(val=''):
    """an absolute filepath which expands also '~' and $var constructs"""
    return path.expanduser(path.expandvars(val))


def subdir(val=''):
    """a relative subdir (a string NOT containing any path.sep)"""
    val = string(val)
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
    val = string(val)
    res = ipv4_re.match(val)
    if not res or res.group() != res.string:
        raise ValueError('%r is not a valid IPv4 address' % val)
    return val


class host:
    """Validator for a host[:port] value.

    Optionally, defaulthost and/or defaultport can be specified.
    """

    def __init__(self, defaulthost='', defaultport=None):
        self.__doc__ = 'a host[:port] value'
        self.defaulthost = defaulthost
        if defaultport is not None:
            self.defaultport = self._checkport(defaultport)
        else:
            self.defaultport = defaultport

    def _checkport(self, p):
        try:
            p = int(p)
            if not 0 < p < 65536:
                raise ValueError
        except ValueError:
            raise ValueError('The port is not a valid port number') from None
        return p

    def _addDefaults(self, host, port=None):
        host = host if host is not None else self.defaulthost
        port = port if port is not None else self.defaultport
        return (host + ':%d' % port) if port else host

    def __call__(self, val=''):
        if val is None:
            if self.defaulthost:
                return self._addDefaults(None)
            else:
                raise ValueError('A None host is not allowed '
                                 'without defaulthost')
        if not isinstance(val, (str, tuple, list)):
            raise ValueError('must be a string or tuple/list (host, port)!')
        if not val:
            return self._addDefaults('')

        try:
            host, port = parseHostPort(val, self.defaultport, True)
        except ValueError:
            raise ValueError(
                '%r is not in the form host_name[:port]' % val) from None
        if not host:
            raise ValueError('Empty hostname is not allowed')
        return self._addDefaults(host, port)


class secret:
    """Parameter type to lookup external secret sources.

    *externalkey*: the external key to look up
    *default*: (optional) default value if not resolved

    Calling `lookup` will resolve to the expected secret.

    Lookup is performed in this order and the first match returned:

    1. externalkey looked up in the nicos keystore
    2. NICOS_<upper(externalkey)> from the environment
    3. (optional) the given default
    """

    def __init__(self, externalkey='', default=None):
        if isinstance(externalkey, Secret):  # from using Secret() in setup
            self.externalkey = externalkey[0]
            self.default = externalkey[1].get('default')
        else:
            self.externalkey = externalkey
            self.default = default

    def lookup(self, error=None):
        """Look up the secret in the NICOS keystore.

        If *error* is given, raise a ConfigurationError if the secret cannot
        be found and no default is given.
        """
        if not self.externalkey:
            raise ConfigurationError('No external key given for this secret')
        try:
            from nicos.utils.credentials import keystore
            val = keystore.nicoskeystore.getCredential(self.externalkey)
        except ImportError:
            val = None

        if not val:
            env_name = f'NICOS_{self.externalkey.upper().replace("-", "_")}'
            val = os.environ.get(env_name)
        if not val:
            val = self.default
        if not val and error:
            raise ConfigurationError(error)
        return val

    def __repr__(self):
        return f'<secret {self.externalkey!r}>'
