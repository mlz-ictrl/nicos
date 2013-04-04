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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""NICOS "switcher" device."""

__version__ = "$Revision$"

from nicos.utils import lazy_property

from nicos.core import anytype, none_or, floatrange, listof, ConfigurationError, PositionError, \
     NicosError, Moveable, Param, Override, status

class MultiSwitcher(Moveable):
    """The switcher is a device that maps switch states onto discrete values of
    a set of (continuously) moveable device.

    This is useful if you have for example two motors that only every moves to
    certain discrete positions for selected 'configurations', e.g. a monochromator changer.
    Then you can control both using ::

        move(changer_switch, 'up')
        move(changer_switch, 'down')

    instead of moving the axis to positions hard to understand::

        move(changer1, 14.55, changer2, 8.15)
        move(changer1, 51.39, changer2, 3.14)

    and still have the underlying continuously moveable devices available for
    debugging purposes.
    """
    attached_devices = {
        'moveables': ([Moveable], 'The (continuous) devices which are controlled'),
    }

    parameters = {
        'states':    Param('List of state names.', type=listof(anytype),
                           mandatory=True),
        'values':    Param('List of values to move to', type=listof(listof(anytype)),
                           mandatory=True),
        'precision': Param('Used for evaluating position, use None to disable',
                           mandatory=True, type=none_or(floatrange(0., 360.))),
        'blockingmove': Param('Should we wait for the move to finish?',
                              mandatory=False, default=True, settable=True, type=bool),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

    hardware_access = False

    @lazy_property
    def devices(self):
        return self._adevs['moveables']

    def doInit(self, mode):
        states = self.states
        values = self.values
        if len(states) != len(values):
            raise ConfigurationError(self, 'Switcher states and values must be '
                                     'of equal length')
        for t in values:
            if len(t) != len(self.devices):
                raise ConfigurationError(self, 'Switcher state entries and moveable '
                                    'must be of equal length')
        self._switchlist = dict(zip(states, values))

    def doStart(self, target):
        if target not in self._switchlist:
            positions = ', '.join(repr(pos) for pos in self.states)
            raise NicosError(self, '%r is an invalid position for this device; '
                            'valid positions are %s' % (target, positions))
        for d,t in zip( self.devices, self._switchlist[target]):
            self.log.debug('moving %r to %r'%(d,t))
            d.start(t)
        for d in self.devices:
            self.log.debug('waiting for %r'%d)
            d.wait()

    def doStop(self):
        for d in self.devices:
            d.stop()

    def doRead(self, maxage=0):
        pos = []
        for d in self.devices:
            pos.append(d.read(maxage))
        hasprec = self.precision is not None
        for name, value in self._switchlist.iteritems():
            if hasprec:
                for d, p, v in zip(self.devices, pos, value):
                    if abs(p - v) > d.getattr(d, 'precision', self.precision):
                        break
                else: # if there was no break we end here...
                    return name
            else:
                if tuple(pos) == tuple(value):
                    return name
        raise PositionError(self, 'unknown position of %s' %
                            ', '.join(repr(d) for d in self.devices))

    def doStatus(self, maxage=0):
        # if the underlying device is moving or in error state,
        # reflect its status
        move_status = (0,'X')
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


