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

"""Definition of abstract base device classes."""

from nicos.core import SLAVE, Attach, ConfigurationError, DeviceMixinBase, \
    HasLimits, HasMapping, HasOffset, HasPrecision, InvalidValueError, \
    ModeError, Moveable, Override, Param, PositionError, ProgrammingError, \
    Readable, oneof, status, usermethod
from nicos.utils import num_sort


class Coder(HasPrecision, Readable):
    """Base class for all coders."""

    @usermethod
    def setPosition(self, pos):
        """Set the current position of the controller to the target.

        This operation is forbidden in slave mode, and does the right thing
        virtually in simulation mode.

        .. method:: doSetPosition(pos)

           This is called to actually set the new position in the hardware.
        """
        if self._mode == SLAVE:
            raise ModeError(self, 'setting new position not possible in '
                            'slave mode')
        elif self._sim_intercept:
            self._sim_setValue(pos)
            return
        self.doSetPosition(pos)
        # update current value in cache
        self.read(0)

    def doSetPosition(self, pos):
        raise NotImplementedError('implement doSetPosition for concrete coders')


class Motor(HasLimits, Coder, Moveable):
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

    .. method:: doReference()

       This method is called by `reference` to do the reference drive.  It
       should initiate a reference drive, wait for its completion and set the
       device position to the "reference position".  It can return the new
       current position after referencing, or None.
    """

    @usermethod
    def reference(self):
        """Do a reference drive of the axis."""
        if self._mode == SLAVE:
            raise ModeError(self, 'referencing not possible in slave mode')
        elif self._sim_intercept:
            return
        elif hasattr(self, 'fixed') and self.fixed:
            self.log.error('device fixed, not referencing: %s', self.fixed)
            return
        newpos = self.doReference()
        if newpos is None:
            newpos = self.read(0)
        return newpos

    def doReference(self):
        raise NotImplementedError('implement doReference for concrete devices')


class TransformedReadable(Readable):
    """Base class for all read-only value-transformed devices.

    Subclasses need to define their attached devices and implement a
    :meth:`._readRaw()` method, returning (raw) device
    values.
    The transformation should be done in the :meth:`._mapReadValue()`
    function that is required to be implemented.

    .. automethod:: _readRaw

    .. automethod:: _mapReadValue
    """

    def doRead(self, maxage=0):
        return self._mapReadValue(self._readRaw(maxage))

    def _mapReadValue(self, value):
        """Hook for integration of transformed devices.

        This method is called with the value returned by :meth:`._readRaw()` and
        should map the raw value to the transformed value.
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_readMapValue method!')

    def _readRaw(self, maxage=0):
        """Read the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_readRaw or doRead method!')


class TransformedMoveable(TransformedReadable, Moveable):
    """Base class for all moveable value-transformed devices

    Subclasses need to define their attached devices and implement
    :meth:`._readRaw() <TransformedReadable._readRaw()>`
    and :meth:`._startRaw()`, operating on raw values.
    The :meth:`._mapTargetValue()` is needed and should do the
    equivalent of the inverse
    :meth:`._mapReadValue() <TransformedReadable._mapReadValue()>`
    function (or whatever is appropriate for the device).

    .. automethod:: _startRaw

    .. automethod:: _mapTargetValue
    """

    def doStart(self, target):
        return self._startRaw(self._mapTargetValue(target))

    def _mapTargetValue(self, target):
        """Hook for integration of transformed devices.

        This method is called to get a value to pass to :meth:`.startRaw()` and
        should map the target value to a raw value.
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_mapTargetValue method!')

    def _startRaw(self, target):
        """Initiate movement to the unmapped/raw value from the device.

        Must be implemented in derived classes!
        """
        raise ProgrammingError(self, 'Somebody please implement a proper '
                               '_startRaw or doStart method!')


class Magnet(HasLimits, TransformedMoveable):
    """Base class for electromagnets."""

    attached_devices = {
        'currentsource': Attach('Powersupply driving the magnetic field',
                                Moveable)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='T'),
        'abslimits': Override(mandatory=False, volatile=True),
    }

    hardware_access = False

    def doReadAbslimits(self):
        limits = self._attached_currentsource.abslimits
        return self._mapReadValue(limits[0]), self._mapReadValue(limits[1])

    def _readRaw(self, maxage=0):
        return self._attached_currentsource.read(maxage)

    def _startRaw(self, target):
        self._attached_currentsource.start(target)

# MappedReadable and MappedMoveable operate (via read/start) on a set of
# predefined values which are mapped via the mapping parameter onto
# device-specific (raw) values.


class MappedReadable(HasMapping, TransformedReadable):
    """Base class for all read-only (discrete) value-mapped devices.

    (also called selector or multiplexer/mux).

    Subclasses need to define their attached devices and implement a
    :meth:`._readRaw() <MappedReadable._readRaw()>` method, returning (raw) device values.
    Subclasses should also implement a :meth:`.doStatus()`.
    Subclasses reimplementing :meth:`.doInit()` need to
    call this class' :meth:`.doInit() <MappedReadable.doInit()>`.

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
        for k, v in self.mapping.items():
            self._inverse_mapping[v] = k

    def doStatus(self, maxage=0):
        """May be derived in subclasses to yield the current status of the device.

        Shall never raise, but return status.NOTREACHED instead.
        """
        try:
            r = self.read(maxage)
            if r == self.fallback:
                return status.NOTREACHED, 'not at configured position: %r, ' \
                    'used dev at pos: %r' % (r, self._readRaw(maxage))
            return status.OK, 'idle'
        except PositionError as e:
            return status.NOTREACHED, str(e)

    def _mapReadValue(self, value):
        """Hook for integration of mapping/switcher devices.

        This method is called with the value returned by `._readRaw()` and
        should map the raw value to a high-level value.  By default, it maps
        values according to the reverse of the
        `nicos.core.mixins.HasMapping.mapping` parameter.
        """
        if value in self._inverse_mapping:
            return self._inverse_mapping[value]
        elif self.relax_mapping:
            if self.fallback is not None:
                return self.fallback
        else:
            raise PositionError(self, 'unknown unmapped position %r' % value)


class MappedMoveable(MappedReadable, TransformedMoveable):
    """Base class for all moveable (discrete) value-mapped devices

    Subclasses need to define their attached devices and implement
    :meth:`.readRaw() <MappedReadable._readRaw()>`
    and :meth:`.startRaw() <MappedMoveable._startRaw()>`, operating on raw values.
    Subclasses should also implement a :meth:`.doStatus()`.
    Subclasses reimplementing :meth:`.doInit()` need to    call this class'
    :meth:`.doInit() <MappedMoveable.doInit()>`.

    .. automethod:: _startRaw

    .. automethod:: _mapTargetValue
    """

    def doInit(self, mode):
        # be restrictive?
        if not self.relax_mapping:
            self.valuetype = oneof(*self.mapping)
        MappedReadable.doInit(self, mode)

    def _mapTargetValue(self, target):
        """Hook for integration of mapping/switcher devices.

        This method is called to get a value to pass to `._startRaw()` and
        should map the high-level value to a raw value.  By default, it maps
        values according to the
        `nicos.core.mixins.HasMapping.mapping` parameter.
        """
        if not self.relax_mapping:
            # be strict...
            if target not in self.mapping:
                positions = ', '.join(repr(pos) for pos in self.mapping)
                raise InvalidValueError(self, '%r is an invalid position for '
                                        'this device; valid positions are %s'
                                        % (target, positions))
        return self.mapping.get(target, target)
