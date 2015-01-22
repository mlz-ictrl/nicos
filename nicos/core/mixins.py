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

"""Meta classes and Mixins for usage in NICOS."""

from time import time as currenttime

from nicos import session
from nicos.core.params import Param, Override, anytype, none_or, limits, dictof
from nicos.core.errors import ConfigurationError
from nicos.pycompat import add_metaclass


class DeviceMixinMeta(type):
    """
    This class provides the __instancecheck__ method for non-Device derived
    mixins.
    """
    def __instancecheck__(cls, inst):  # pylint: disable=C0203
        if inst.__class__ == DeviceAlias and inst._initialized:
            if isinstance(inst._obj, NoDevice):
                return issubclass(inst._cls, cls)
            return isinstance(inst._obj, cls)
        # does not work with Python 2.6!
        # return type.__instancecheck__(cls, inst)
        return issubclass(inst.__class__, cls)


@add_metaclass(DeviceMixinMeta)
class DeviceMixinBase(object):
    """
    Base class for all NICOS device mixin classes not derived from `Device`.

    This class sets the correct metaclass and is easier to use than setting the
    metaclass on each mixin class.  Mixins **must** derive from this class.
    """


class AutoDevice(DeviceMixinBase):
    """Abstract mixin for devices that are created automatically as dependent
    devices of other devices.
    """


class HasLimits(DeviceMixinBase):
    """
    This mixin can be inherited from device classes that are continuously
    moveable.  It automatically adds two parameters, absolute and user limits,
    and overrides :meth:`.isAllowed` to check if the given position is within the
    limits before moving.

    .. note:: In a base class list, ``HasLimits`` must come before ``Moveable``,
       e.g.::

          class MyDevice(HasLimits, Moveable): ...

    The `abslimits` parameter cannot be set after creation of the device and
    must be given in the setup configuration.

    The `userlimits` parameter gives the actual minimum and maximum values
    that the device can be moved to.  The user limits must lie within the
    absolute limits.

    **Important:** If the device is also an instance of `HasOffset`, it should
    be noted that the `abslimits` are in hardware units (disregarding the
    offset), while the `userlimits` are in logical units (taking the offset
    into account).

    The class also provides properties to read or set only one item of the
    limits tuple:

    .. attribute:: absmin
                   absmax

       Getter properties for the first/second value of `abslimits`.

    .. attribute:: usermin
                   usermax

       Getter and setter properties for the first/second value of `userlimits`.

    """

    parameters = {
        'userlimits': Param('User defined limits of device value', unit='main',
                            type=limits, settable=True, chatty=True),
        'abslimits':  Param('Absolute limits of device value', unit='main',
                            type=limits, mandatory=True),
    }

    @property
    def absmin(self):
        return self.abslimits[0]

    @property
    def absmax(self):
        return self.abslimits[1]

    def __getusermin(self):
        return self.userlimits[0]

    def __setusermin(self, value):
        self.userlimits = (value, self.userlimits[1])

    usermin = property(__getusermin, __setusermin)

    def __getusermax(self):
        return self.userlimits[1]

    def __setusermax(self, value):
        self.userlimits = (self.userlimits[0], value)

    usermax = property(__getusermax, __setusermax)

    del __getusermin, __setusermin, __getusermax, __setusermax

    def _checkLimits(self, limits):
        umin, umax = limits
        amin, amax = self.abslimits
        if isinstance(self, HasOffset):
            offset = getattr(self, '_new_offset', self.offset)
            umin += offset
            umax += offset
        else:
            offset = 0
        if umin > umax:
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) above the user '
                'maximum (%s, offset %s)' % (umin, offset, umax, offset))
        if umin < amin:
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) below the '
                'absolute minimum (%s)' % (umin, offset, amin))
        if umax > amax:
            raise ConfigurationError(
                self, 'user maximum (%s, offset %s) above the '
                'absolute maximum (%s)' % (umax, offset, amax))

    def doReadUserlimits(self):
        if 'userlimits' not in self._config:
            self.log.info('setting userlimits from abslimits, which are %s'
                          % (self.abslimits,))
            return self.abslimits
        cfglimits = self._config['userlimits']
        self._checkLimits(cfglimits)
        return cfglimits

    def doWriteUserlimits(self, value):
        self._checkLimits(value)
        if isinstance(self, HasOffset) and hasattr(self, '_new_offset'):
            # when changing the offset, the userlimits are adjusted so that the
            # value stays within them, but only after the new offset is applied
            return
        curval = self.read(0)
        if isinstance(self, HasPrecision):
            outoflimits = curval + self.precision < value[0] or \
                curval - self.precision > value[1]
        else:
            outoflimits = not (value[0] <= curval <= value[1])
        if outoflimits:
            self.log.warning('current device value (%s) not within new '
                             'userlimits (%s, %s)' %
                             ((self.format(curval, unit=True),) + value))

    def _adjustLimitsToOffset(self, value, diff):
        """Adjust the user limits to the given offset.

        Used by the HasOffset mixin class to adjust the offset. *value* is the
        offset value, *diff* the offset difference.
        """
        limits = self.userlimits
        self._new_offset = value
        self.userlimits = (limits[0] - diff, limits[1] - diff)
        del self._new_offset


class HasOffset(DeviceMixinBase):
    """
    Mixin class for Readable or Moveable devices that want to provide an
    'offset' parameter and that can be adjusted via adjust().

    This is *not* directly a feature of Moveable, because providing this
    transparently this would mean that `doRead()` returns the un-adjusted value
    while `read()` returns the adjusted value.  It would also mean that the
    un-adjusted value is stored in the cache, which is wrong for monitoring
    purposes.

    Instead, each class that provides an offset **must** inherit this mixin, and
    subtract ``self.offset`` in `doRead()`, while adding it in `doStart()`.

    The device position is ``hardware_position - offset``.
    """
    parameters = {
        'offset':  Param('Offset of device zero to hardware zero', unit='main',
                         settable=True, category='offsets', chatty=True),
    }

    def doWriteOffset(self, value):
        """Adapt the limits to the new offset."""
        old_offset = self.offset
        diff = value - old_offset
        if isinstance(self, HasLimits):
            self._adjustLimitsToOffset(value, diff)
        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value', self.read(0) - diff,
                            currenttime(), self.maxage)
        session.elog_event('offset', (str(self), old_offset, value))


class HasPrecision(DeviceMixinBase):
    """
    Mixin class for Readable and Moveable devices that want to provide a
    'precision' parameter.

    This is mainly useful for user info, and for high-level devices that have
    to work with limited-precision subordinate devices.
    """
    parameters = {
        'precision': Param('Precision of the device value', unit='main',
                           settable=True, category='precisions'),
    }

    def doIsAtTarget(self, pos):
        if self.target is None:
            return True  # avoid bootstrapping problems
        return abs(self.target - pos) <= self.precision


class HasMapping(DeviceMixinBase):
    """
    Mixin class for devices that use a finite mapping between user supplied
    input and internal representation.

    This is mainly useful for devices which can only yield certain values or go
    to positions from a predefined set, like switching devices.

    Abstract classes that use this mixin are implemented in
    `nicos.devices.abstract.MappedReadable` and `.MappedMoveable`.
    """
    parameters = {
        'mapping':  Param('Mapping of device values to raw (internal) values',
                          unit='', settable=False, mandatory=True,
                          type=dictof(str, anytype)),
        'fallback': Param('Readback value if the raw device value is not in the '
                          'mapping or None to disable', default=None,
                          unit='', type=anytype, settable=False),
    }

    # mapped values usually are string constants and have no unit
    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    def doIsAllowed(self, target):
        if target not in self.mapping:
            return False, 'unknown value: %r, must be one of %s' % \
                (target, ', '.join(map(repr, sorted(self.mapping))))
        return True, ''


class HasTimeout(DeviceMixinBase):
    """
    Mixin class for devices whose wait() should have a simple timeout.
    """
    parameters = {
        'timeout':  Param('Timeout of after start(), or None', unit='s',
                          type=none_or(float), settable=True, mandatory=True),
        '_started': Param('Timestamp of last doStart() call',
                          userparam=False, settable=True, unit='s'),
    }


from nicos.core.device import DeviceAlias, NoDevice
