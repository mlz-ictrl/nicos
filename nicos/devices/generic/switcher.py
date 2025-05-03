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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS "switcher" devices."""

from nicos.core import ConfigurationError, InvalidValueError, Moveable, \
    Override, Param, PositionError, Readable, anytype, dictof, floatrange, \
    listof, multiReset, multiStatus, multiStop, multiWait, none_or, status
from nicos.core.constants import SIMULATION
from nicos.core.params import Attach
from nicos.devices.abstract import MappedMoveable, MappedReadable
from nicos.utils import lazy_property


class Switcher(MappedMoveable):
    """The switcher is a device that maps switch states onto discrete values of
    a continuously moveable device.

    This is useful if you have for example a motor that only every moves to
    certain discrete positions, e.g. a monochromator changer.  Then you can
    control it using ::

        move(changer_switch, 'up')
        move(changer_switch, 'down')

    instead of moving the axis to positions hard to understand::

        move(changer, 14.55)
        move(changer, 51.3)

    and still have the underlying continuously moveable device available for
    debugging purposes.
    """

    attached_devices = {
        'moveable': Attach('The continuous device which is controlled',
                           Moveable),
    }

    parameters = {
        'precision':    Param('Precision for comparison', mandatory=True),
        'blockingmove': Param('Should we wait for the move to finish?',
                              type=bool, default=True, settable=True),
    }

    parameter_overrides = {
        'fallback': Override(userparam=False, type=none_or(str),
                             mandatory=False),
    }

    hardware_access = False

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        self._attached_moveable.start(target)
        if self.blockingmove:
            self._attached_moveable.wait()

    def _readRaw(self, maxage=0):
        """Return raw position value of the moveable."""
        return self._attached_moveable.read(maxage)

    def _mapReadValue(self, value):
        """Override default inverse mapping to allow a
        deviation <= precision.
        """
        prec = self.precision
        for name, pos in self.mapping.items():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        if self.relax_mapping:
            return self._attached_moveable.format(value, True)
        raise PositionError(self, 'unknown position of %s: %s' %
                            (self._attached_moveable,
                             self._attached_moveable.format(value, True))
                            )

    def doIsAllowed(self, target):
        # Forward the move request to the underlying device
        return self._attached_moveable.isAllowed(self._mapTargetValue(target))

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        (move_status, move_msg) = self._attached_moveable.status(maxage)
        if move_status == status.BUSY:
            return move_status, f'moving to {self.format(self.target)}'
        elif move_status not in (status.OK, status.WARN):
            return (move_status, move_msg)

        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            r = self.read(maxage)
            if r not in self.mapping:
                if self.fallback:
                    return (status.UNKNOWN, 'unconfigured position of %s, '
                            'using fallback' % self._attached_moveable)
                return (status.NOTREACHED, 'unconfigured position of %s or '
                        'still moving' % self._attached_moveable)
        except PositionError as e:
            return status.NOTREACHED, str(e)
        return status.OK, ''

    def doReset(self):
        self._attached_moveable.reset()

    def doStop(self):
        self._attached_moveable.stop()

class ReadonlySwitcher(MappedReadable):
    """Same as the `Switcher`, but for read-only underlying devices."""

    attached_devices = {
        'readable': Attach('The continuous device which is read', Readable),
    }

    parameters = {
        'precision': Param('Precision for comparison', type=floatrange(0),
                           default=0),
    }

    parameter_overrides = {
        'fallback': Override(userparam=False, type=none_or(str),
                             mandatory=False),
    }

    hardware_access = False

    def _readRaw(self, maxage=0):
        return self._attached_readable.read(maxage)

    def _mapReadValue(self, value):
        prec = self.precision
        for name, pos in self.mapping.items():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s' %
                            self._attached_readable)

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._attached_readable.status(maxage)
        if move_status[0] not in (status.OK, status.WARN):
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            if self.read(maxage) == self.fallback:
                return status.NOTREACHED, 'unconfigured position of %s or '\
                    'still moving' % self._attached_readable
        except PositionError as e:
            return status.NOTREACHED, str(e)
        return status.OK, ''

    def doReset(self):
        self._attached_readable.reset()


class MultiSwitcher(MappedMoveable):
    """The multi-switcher generalizes the `Switcher` so that for a state change
    multiple underlying moveable devices can be controlled.

    This is useful if you have for example two motors that only ever move to
    certain discrete positions for selected 'configurations', e.g. a
    monochromator changer.  Then you can control both using ::

        move(changer_switch, 'up')
        move(changer_switch, 'down')

    instead of moving the axis to positions hard to understand or remember::

        move(changer1, 14.55, changer2, 8.15)
        move(changer1, 51.39, changer2, 3.14)

    and still have the underlying continuously moveable devices available for
    debugging purposes.

    """
    attached_devices = {
        'moveables': Attach('The N (continuous) devices which are'
                            ' controlled', Moveable, multiple=True),
        'readables': Attach('0 to N (continuous) devices which are'
                            ' used for read back only', Readable,
                            optional=True, multiple=True),
    }

    parameters = {
        'precision': Param('List of allowed deviations (1 or N) from target '
                           'position, or None to disable', mandatory=True,
                           type=none_or(listof(none_or(floatrange(0))))),
        'blockingmove': Param('Should we wait for the move to finish?',
                              mandatory=False, default=True, settable=True,
                              type=bool),
    }

    parameter_overrides = {
        'mapping': Override(description='Mapping of state names to N values '
                            'to move the moveables to',
                            type=dictof(anytype, listof(anytype))),
        'fallback': Override(userparam=False, type=none_or(anytype),
                             mandatory=False),
    }

    hardware_access = False

    @lazy_property
    def devices(self):
        return self._attached_moveables + self._attached_readables

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)
        for k, t in self.mapping.items():
            if len(t) != len(self.devices):
                raise ConfigurationError(self, 'Switcher state entry for key '
                                         '%r has different length than '
                                         'moveables list' % k)
        if self.precision:
            if len(self.precision) not in [1, len(self.devices)]:
                raise ConfigurationError(self, 'The precision list must either'
                                         ' contain only one element or have '
                                         'the same amount of elements as the '
                                         'moveables list')

    def _startRaw(self, target):
        """target is the raw value, i.e. a list of positions"""
        moveables = self._attached_moveables
        if not isinstance(target, (tuple, list)) or \
                len(target) < len(moveables):
            raise InvalidValueError(self, 'doStart needs a tuple of %d '
                                    'positions for this device!' %
                                    len(moveables))
        # only check and move the moveables, which are first in self.devices
        for d, t in zip(moveables, target):
            if not d.isAllowed(t):
                raise InvalidValueError(self, 'target value %r not accepted '
                                        'by device %s' % (t, d.name))
        for d, t in zip(moveables, target):
            self.log.debug('moving %r to %r', d, t)
            d.start(t)
        if self.blockingmove:
            multiWait(moveables)

    def _readRaw(self, maxage=0):
        if self._mode == SIMULATION and self.target is not None:
            # In simulation mode the values of the readables are assumed to be
            # given in the mapping table for the current target
            return tuple(d.read(maxage) for d in self._attached_moveables) + \
                   tuple(self.mapping[self.target][len(self._attached_moveables):])
        return tuple(d.read(maxage) for d in self.devices)

    def _mapReadValue(self, value):
        """maps a tuple to one of the configured values"""
        hasprec = bool(self.precision)
        if hasprec:
            precisions = self.precision
            if len(precisions) == 1:
                precisions = [precisions[0]] * len(self.devices)
        for name, values in self.mapping.items():
            if hasprec:
                for p, v, prec in zip(value, values, precisions):
                    if prec:
                        if abs(p - v) > prec:
                            break
                    elif p != v:
                        break
                else:  # if there was no break we end here...
                    return name
            else:
                if tuple(value) == tuple(values):
                    return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s: %s' % (
            ', '.join(str(d) for d in self.devices),
            ', '.join(d.format(p) for (p, d) in zip(value, self.devices))))

    def doStatus(self, maxage=0):
        # if the underlying devices are moving or in error state,
        # reflect their status
        move_status = multiStatus(self.devices, maxage)
        if move_status[0] not in (status.OK, status.WARN):
            return move_status
        return MappedReadable.doStatus(self, maxage)

    def doReset(self):
        multiReset(self._adevs)

    def doStop(self):
        multiStop(self._adevs)
