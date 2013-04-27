#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""NICOS "switcher" device."""

from nicos.core import anytype, dictof, PositionError, NicosError, Moveable, \
     Readable, Param, Override, status, oneof


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
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
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
            self.read(maxage)
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
