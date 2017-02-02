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

"""Definition of abstract base device classes."""

from nicos.core import ConfigurationError, DeviceMixinBase, HasLimits, \
    HasMapping, HasOffset, HasPrecision, InvalidValueError, ModeError, \
    Moveable, Override, Param, PositionError, ProgrammingError, Readable, \
    SLAVE, oneof, status, usermethod
from nicos.pycompat import iteritems


class Coder(HasPrecision, Readable):
    """Base class for all coders."""

    @usermethod
    def setPosition(self, pos):
        """Sets the current position of the controller to the target.

        This operation is forbidden in slave mode, and does the right thing
        virtually in simulation mode.

        .. method:: doSetPosition(pos)

           This is called to actually set the new position in the hardware.
        """
        if self._mode == SLAVE:
            raise ModeError(self, 'setting new position not possible in '
                            'slave mode')
        elif self._sim_active:
            self._sim_setValue(pos)
            return
        self.doSetPosition(pos)
        # update current value in cache
        self.read(0)

    def doSetPosition(self, pos):
        raise NotImplementedError('implement doSetPosition for concrete coders')


class Motor(HasLimits, Coder, Moveable):  # pylint: disable=W0223
    """Base class for all motors.

    This class inherits from Coder since a Motor can be used instead of a true
    encoder to supply the current position to an Axis.
    """

    parameters = {
        'speed': Param('The motor speed', unit='main/s', settable=True),
    }


class Axis(HasOffset, HasPrecision, HasLimits, Moveable):
    """Base class for all axes."""

    parameters = {
        'dragerror': Param('Maximum deviation of motor and coder when read out '
                           'during a positioning step', unit='main', default=1,
                           settable=True),
        'maxtries':  Param('Number of tries to reach the target', type=int,
                           default=3, settable=True),
        'loopdelay': Param('The sleep time when checking the movement',
                           unit='s', default=0.3, settable=True),
        'backlash':  Param('The backlash for the axis: if positive/negative, '
                           'always approach from positive/negative values',
                           unit='main', default=0, settable=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, settable=True),
    }


class CanReference(DeviceMixinBase):
    """Mixin class for axis devices to provide a reference drive function.

    This reference drive will be used by the `reference` user command.

    .. automethod:: reference

    .. method:: doReference(*args)

       This method is called by `reference` to do the reference drive.  It
       should initiate a reference drive, wait for its completion and set the
       device position to the "reference position".  It can return the new
       current position after referencing, or None.
    """

    @usermethod
    def reference(self, *args):
        """Do a reference drive of the axis."""
        if self._mode == SLAVE:
            raise ModeError(self, 'referencing not possible in slave mode')
        elif self._sim_active:
            return
        elif hasattr(self, 'fixed') and self.fixed:
            self.log.error('device fixed, not referencing: %s', self.fixed)
            return
        newpos = self.doReference(*args)
        if newpos is None:
            newpos = self.read(0)
        return newpos


# MappedReadable and MappedMoveable operate (via read/start) on a set of
# predefined values which are mapped via the mapping parameter onto
# device-specific (raw) values.

class MappedReadable(HasMapping, Readable):
    """Base class for all read-only value-mapped devices.

    (also called selector or multiplexer/mux).

    Subclasses need to define their attached devices and implement a
    `_readRaw()` method, returning (raw) device values.  Subclasses should also
    implement a `.doStatus()`.  Subclasses reimplementing `.doInit()` need to
    call this class' `.doInit()`.

    .. automethod:: _readRaw

    .. automethod:: _mapReadValue
    """

    # set this to true in derived classes to allow passing values out of mapping
    relax_mapping = False

    def doInit(self, mode):
        if self.fallback in self.mapping:
            raise ConfigurationError(self, 'Value of fallback parameter is '
                                     'not allowed to be in the mapping!')
        self._inverse_mapping = {}
        for k, v in iteritems(self.mapping):
            self._inverse_mapping[v] = k

    def doStatus(self, maxage=0):
        """May be derived in subclasses to yield the current status of the device.

        Shall never raise, but return status.NOTREACHED instead.
        """
        try:
            r = self.read(maxage)
            if r == self.fallback:
                return status.NOTREACHED, 'not one of the configured values'
            return status.OK, 'idle'
        except PositionError as e:
            return status.NOTREACHED, str(e)

    def doRead(self, maxage=0):
        return self._mapReadValue(self._readRaw(maxage))

    def _mapReadValue(self, value):
        """Hook for integration of mapping/switcher devices.

        This method is called with the value returned by `._readRaw()` and
        should map the raw value to a high-level value.  By default, it maps
        values according to the reverse of the `.mapping` parameter.
        """
        if value in self._inverse_mapping:
            return self._inverse_mapping[value]
        elif self.relax_mapping:
            if self.fallback is not None:
                return self.fallback
        else:
            raise PositionError(self, 'unknown unmapped position %r' % value)

    def _readRaw(self, maxage=0):
        """Reads the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_readRaw or doRead method!')


class MappedMoveable(MappedReadable, Moveable):
    """Base class for all moveable value-mapped devices

    Subclasses need to define their attached devices and implement `._readRaw()`
    and `._startRaw()`, operating on raw values.  Subclasses should also
    implement a `.doStatus()`.  Subclasses reimplementing `.doInit()` need to
    call this class' `.doInit()`.

    .. automethod:: _startRaw

    .. automethod:: _mapTargetValue
    """

    def doInit(self, mode):
        # be restrictive?
        if not self.relax_mapping:
            self.valuetype = oneof(*self.mapping)
        MappedReadable.doInit(self, mode)

    def doStart(self, target):
        return self._startRaw(self._mapTargetValue(target))

    def _mapTargetValue(self, target):
        """Hook for integration of mapping/switcher devices.

        This method is called to get a value to pass to `._startRaw()` and
        should map the high-level value to a raw value.  By default, it maps
        values according to the `.mapping` parameter.
        """
        if not self.relax_mapping:
            # be strict...
            if target not in self.mapping:
                positions = ', '.join(repr(pos) for pos in self.mapping)
                raise InvalidValueError(self, '%r is an invalid position for '
                                        'this device; valid positions are %s'
                                        % (target, positions))
        return self.mapping.get(target, target)

    def _startRaw(self, target):
        """Initiate movement to the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_startRaw or doStart method!')
