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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS "switcher" devices."""

from nicos.utils import lazy_property
from nicos.core import anytype, dictof, none_or, floatrange, listof, \
     PositionError, ConfigurationError, Moveable, Readable, Param, \
     Override, status, InvalidValueError, multiStatus
from nicos.core.params import Attach
from nicos.devices.abstract import MappedReadable, MappedMoveable
from nicos.pycompat import iteritems


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
        'moveable': (Moveable, 'The continuous device which is controlled'),
    }

    parameters = {
        'precision':    Param('Precision for comparison', mandatory=True),
        'blockingmove': Param('Should we wait for the move to finish?',
                              type=bool, default=True, settable=True),
    }

    parameter_overrides = {
        'fallback':  Override(userparam=False, type=none_or(str), mandatory=False),
    }

    hardware_access = False

    def _startRaw(self, target):
        """Initiate movement of the moveable to the translated raw value."""
        self._adevs['moveable'].start(target)
        if self.blockingmove:
            self._adevs['moveable'].wait()

    def _readRaw(self, maxage=0):
        """Return raw position value of the moveable."""
        return self._adevs['moveable'].read(maxage)

    def _mapReadValue(self, pos):
        """Override default inverse mapping to allow a deviation <= precision"""
        prec = self.precision
        for name, value in iteritems(self.mapping):
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        if self.relax_mapping:
            return self._adevs['moveable'].format(pos, True)
        raise PositionError(self, 'unknown position of %s: %s' %
                            (self._adevs['moveable'],
                             self._adevs['moveable'].format(pos, True))
                            )

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._adevs['moveable'].status(maxage)
        if move_status[0] != status.OK:
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            r = self.read(maxage)
            if r not in self.mapping:
                if self.fallback:
                    return (status.UNKNOWN, 'unconfigured position of %s, using '
                                            'fallback' % self._adevs['moveable'])
                return (status.NOTREACHED, 'unconfigured position of %s or still'
                                           ' moving' % self._adevs['moveable'])
        except PositionError as e:
            return status.NOTREACHED, str(e)
        return status.OK, ''


class ReadonlySwitcher(MappedReadable):
    """Same as the `Switcher`, but for read-only underlying devices."""

    attached_devices = {
        'readable': (Readable, 'The continuous device which is read'),
    }

    parameters = {
        'precision': Param('Precision for comparison', type=float, default=0),
    }

    parameter_overrides = {
        'fallback':  Override(userparam=False, type=none_or(str), mandatory=False),
    }

    hardware_access = False

    def _readRaw(self, maxage=0):
        return self._adevs['readable'].read(maxage)

    def _mapReadValue(self, pos):
        prec = self.precision
        for name, value in iteritems(self.mapping):
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['readable'])

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._adevs['readable'].status(maxage)
        if move_status[0] != status.OK:
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            if self.read(maxage) == self.fallback:
                return status.NOTREACHED, 'unconfigured position of %s or '\
                                       'still moving' % self._adevs['moveable']
        except PositionError as e:
            return status.NOTREACHED, str(e)
        return status.OK, ''


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
                           'position, or None to disable.', mandatory=True,
                           type=none_or(listof(floatrange(0., 360.)))),
        'blockingmove': Param('Should we wait for the move to finish?',
                              mandatory=False, default=True, settable=True,
                              type=bool),
    }

    parameter_overrides = {
        'mapping':   Override(description='Mapping of state names to N values '
                              'to move the moveables to',
                              type=dictof(anytype, listof(anytype))),
        'fallback':  Override(userparam=False, type=none_or(anytype),
                              mandatory=False),
    }

    hardware_access = False

    @lazy_property
    def devices(self):
        return self._adevs['moveables'] + self._adevs['readables']

    def doInit(self, mode):
        MappedMoveable.doInit(self, mode)
        for t in self.mapping.values():
            if len(t) != len(self.devices):
                raise ConfigurationError(self, 'Switcher state entries and '
                                       'moveables list must be of equal length')
        if self.precision:
            if len(self.precision) not in [1, len(self.devices)]:
                raise ConfigurationError(self, 'The precision list must either'
                                         'contain only one element or have the '
                                         'same amount of elements as the '
                                         'moveables list')

    def _startRaw(self, target):
        """target is the raw value, i.e. a list of positions"""
        moveables = self._adevs['moveables']
        if not isinstance(target, (tuple, list)) or \
            len(target) < len(moveables):
            raise InvalidValueError(self, 'doStart needs a tuple of %d positions'
                                    ' for this device!' % len(moveables))
        # only check and move the moveables, which are first in self.devices
        for d, t in zip(moveables, target):
            if not d.isAllowed(t):
                raise InvalidValueError(self, 'target value %r not accepted by '
                                        'device %s' % (t, d.name))
        for d, t in zip(moveables, target):
            self.log.debug('moving %r to %r' % (d, t))
            d.start(t)
        if self.blockingmove:
            for d in self.devices:
                self.log.debug('waiting for %r'%d)
                d.wait()

    def _readRaw(self, maxage=0):
        return tuple(d.read(maxage) for d in self.devices)

    def _mapReadValue(self, pos):
        """maps a tuple to one of the configured values"""
        hasprec = bool(self.precision)
        if hasprec:
            precisions = self.precision
            if len(precisions) == 1:
                precisions = [precisions[0]] * len(self.devices)
        for name, values in iteritems(self.mapping):
            if hasprec:
                for p, v, prec in zip(pos, values, precisions):
                    if prec:
                        if abs(p - v) > prec:
                            break
                    elif p != v:
                        break
                else: # if there was no break we end here...
                    return name
            else:
                if tuple(pos) == tuple(values):
                    return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s : %s' % (
                            ', '.join(repr(p) for p in pos),
                            ', '.join(str(d) for d in self.devices)))

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = multiStatus(self.devices, maxage)
        if move_status[0] != status.OK:
            return move_status
        return MappedReadable.doStatus(self, maxage)
