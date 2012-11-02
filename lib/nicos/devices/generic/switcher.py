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

"""NICOS "switcher" device."""

__version__ = "$Revision$"

from nicos.core import listof, anytype, ConfigurationError, PositionError, \
     NicosError, Moveable, Readable, Param, Override


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
        'states':    Param('List of state names.', type=listof(str),
                           mandatory=True),
        'values':    Param('List of values to move to', type=listof(anytype),
                           mandatory=True),
        'precision': Param('Precision for comparison', mandatory=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        states = self.states
        values = self.values
        if len(states) != len(values):
            raise ConfigurationError(self, 'Switcher states and values must be '
                                     'of equal length')
        self._switchlist = dict(zip(states, values))

    def doStart(self, target):
        if target not in self._switchlist:
            positions = ', '.join(repr(pos) for pos in self.states)
            raise NicosError(self, '%r is an invalid position for this device; '
                            'valid positions are %s' % (target, positions))
        target = self._switchlist[target]
        self._adevs['moveable'].start(target)
        self._adevs['moveable'].wait()

    def doRead(self, maxage=0):
        pos = self._adevs['moveable'].read(maxage)
        prec = self.precision
        for name, value in self._switchlist.iteritems():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            else:
                if pos == value:
                    return name
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['moveable'])

    def doStatus(self, maxage=0):
        return self._adevs['moveable'].status(maxage)


class ReadonlySwitcher(Readable):
    """Same as the `Switcher`, but for read-only underlying devices."""

    attached_devices = {
        'readable': (Readable, 'The continuous device which is read'),
    }

    parameters = {
        'states':    Param('List of state names.', type=listof(str),
                           mandatory=True),
        'values':    Param('List of values to move to', type=listof(anytype),
                           mandatory=True),
        'precision': Param('Precision for comparison', type=float, default=0),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    def doInit(self, mode):
        states = self.states
        values = self.values
        if len(states) != len(values):
            raise ConfigurationError(self, 'Switcher states and values must be '
                                     'of equal length')
        self._switchlist = dict(zip(states, values))

    def doRead(self, maxage=0):
        pos = self._adevs['readable'].read(maxage)
        prec = self.precision
        for name, value in self._switchlist.iteritems():
            if prec:
                if abs(pos - value) <= prec:
                    return name
            else:
                if pos == value:
                    return name
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['readable'])

    def doStatus(self, maxage=0):
        return self._adevs['readable'].status(maxage)
