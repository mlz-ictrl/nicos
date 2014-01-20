#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
from nicos.core import anytype, dictof, none_or, floatrange, listof, oneof, \
     PositionError, NicosError, ConfigurationError, Moveable, Readable, Param, \
     Override, status, multiStop


class Switcher(Moveable):
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
        'mapping':      Param('Map of state names to values',
                              type=dictof(str, anytype), mandatory=True),
        'precision':    Param('Precision for comparison', mandatory=True),
        'blockingmove': Param('Should we wait for the move to finish?',
                              type=bool, default=True, settable=True),
        'fallback' :    Param('Default value if value not in mapping',
                              default=None, mandatory=False, settable=False,
                              userparam=False, type=none_or(str)),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        if self.fallback in self.mapping:
            raise ConfigurationError('Value of default Parameter is not allowed to be in mapping!')
        self.valuetype = oneof(*self.mapping)

    def doStart(self, target):
        if target not in self.mapping:
            positions = ', '.join(repr(pos) for pos in self.mapping)
            raise NicosError(self, '%r is an invalid position for this device; '
                             'valid positions are %s' % (target, positions))
        target = self.mapping[target]
        self._adevs['moveable'].start(target)
        if self.blockingmove:
            self._adevs['moveable'].wait()

    def doWait(self):
        self._adevs['moveable'].wait()

    def doStop(self):
        self._adevs['moveable'].stop()

    def doRead(self, maxage=0):
        pos = self._adevs['moveable'].read(maxage)
        prec = self.precision
        for name, value in self.mapping.iteritems():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        if self.fallback is not None:
            return self.fallback
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['moveable'])

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = self._adevs['moveable'].status(maxage)
        if move_status[0] != status.OK:
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            if self.read(maxage) == self.fallback:
                return status.NOTREACHED, 'unconfigured position of %s or '\
                                       'still moving' % self._adevs['moveable']
        except PositionError, e:
            return status.NOTREACHED, str(e)
        return status.OK, ''


class ReadonlySwitcher(Readable):
    """Same as the `Switcher`, but for read-only underlying devices."""

    attached_devices = {
        'readable': (Readable, 'The continuous device which is read'),
    }

    parameters = {
        'mapping':   Param('Map of state names to values',
                           type=dictof(str, anytype), mandatory=True),
        'precision': Param('Precision for comparison', type=float, default=0),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        pass

    def doRead(self, maxage=0):
        pos = self._adevs['readable'].read(maxage)
        prec = self.precision
        for name, value in self.mapping.iteritems():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            elif pos == value:
                return name
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['readable'])

    def doStatus(self, maxage=0):
        return self._adevs['readable'].status(maxage)


class MultiSwitcher(Moveable):
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
        'moveables': ([Moveable], 'The N (continuous) devices which are'
                                  ' controlled'),
    }

    parameters = {
        'mapping':   Param('Mapping of state names to N values to move the moveables to',
                           type=dictof(anytype, listof(anytype)),
                           mandatory=True),
        'precision': Param('List of allowed deviations (1 or N) from target '
                           'position, or None to disable.', mandatory=True,
                           type=none_or(listof(floatrange(0., 360.)))),
        'blockingmove': Param('Should we wait for the move to finish?',
                              mandatory=False, default=True, settable=True,
                              type=bool),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    @lazy_property
    def devices(self):
        return self._adevs['moveables']

    def doInit(self, mode):
        for t in self.mapping.itervalues():
            if len(t) != len(self.devices):
                raise ConfigurationError(self, 'Switcher state entries and '
                                       'moveables list must be of equal length')
        if self.precision:
            if len(self.precision) not in [1, len(self.devices)]:
                raise ConfigurationError(self, 'The precision list must either'
                                       'contain only one element or have the same amount'
                                       'of elements as the moveables list')
        self.valuetype = oneof(*self.mapping)

    def doStart(self, target):
        if target not in self.mapping:
            positions = ', '.join(repr(pos) for pos in self.mapping)
            raise NicosError(self, '%r is an invalid position for this device; '
                             'valid positions are %s' % (target, positions))
        for d,t in zip(self.devices, self.mapping[target]):
            self.log.debug('moving %r to %r' % (d, t))
            d.start(t)
        if self.blockingmove:
            for d in self.devices:
                self.log.debug('waiting for %r'%d)
                d.wait()

    def doStop(self):
        multiStop(self.devices)

    def doRead(self, maxage=0):
        pos = [d.read(maxage) for d in self.devices]
        hasprec = bool(self.precision)
        if hasprec:
            precisions = self.precision
            if len(precisions) == 1:
                precisions = [precisions[0]] * len(self.devices)
        for name, values in self.mapping.iteritems():
            if hasprec:
                for d, p, v, prec in zip(self.devices, pos, values, precisions):
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
        raise PositionError(self, 'unknown position of %s' %
                            ', '.join(str(d) for d in self.devices))

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = (0, 'X')
        for d in self.devices:
            s = d.status(maxage)
            if move_status[0] < s[0]:
                move_status = s
        if move_status[0] != status.OK:
            return move_status
        # otherwise, we have to check if we are at a known position,
        # and otherwise return an error status
        try:
            self.read(maxage)
        except PositionError, e:
            return status.NOTREACHED, str(e)
        return status.OK, ''
