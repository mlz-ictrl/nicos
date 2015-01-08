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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

import time

from nicos.utils import lazy_property
from nicos.devices.generic import Switcher
from nicos.core import anytype, dictof, none_or, floatrange, listof, oneof, \
     NicosError, ConfigurationError, Readable, Override, \
     Param, status, tupleof
from nicos.core.utils import formatStatus
from nicos.pycompat import iteritems


class SenseSwitch(Switcher):
    """The SenseSwitcher is a device that maps switch states onto discrete values of
    a set continuously moveable device. For readout of the current position an additional
    set of readable devices is also used.

    This is useful if you have for example a digital output to initiate a certain action
    and a digital input to see if it succeeded,
    and still have the underlying continuously moveable device available for
    debugging purposes.
    """

    attached_devices = {
        'readable': (Readable, 'The sensing device which is checked'),
    }

    parameters = {
        'timeout': Param('Max. allowed time to reach the requested position',
                         type=float, default=13, settable=True, mandatory=False,
                         unit='s'),
    }

    parameter_overrides = {
        'precision':  Override(type=none_or(listof(floatrange(0., 360.))),
                               default=None),
        'mapping':    Override(type=dictof(anytype, tupleof(anytype, anytype))),
    }
    hardware_access = False

    _starttime = None

    @lazy_property
    def devices(self):
        return [self._adevs['moveable'], self._adevs['readable']]

    def doInit(self, mode):
        for t in self.mapping.values():
            if len(t) != 2:
                raise ConfigurationError(self, 'All mapping state entries '
                                       'must have a length of 2')
        if self.precision:
            if len(self.precision) not in [1, 2]:
                raise ConfigurationError(self, 'The precision list must '
                                       'contain exactly only or two elements')
        self.valuetype = oneof(*self.mapping)

    def doStart(self, target):
        if target not in self.mapping:
            positions = ', '.join(repr(pos) for pos in self.mapping)
            raise NicosError(self, '%r is an invalid position for this device; '
                             'valid positions are %s' % (target, positions))
        target = self.mapping[target]
        self._adevs['moveable'].start(target[0])
        self._starttime = time.time()
        if self.blockingmove:
            self.wait()

    def _read(self):
        pos = [d.read(0) for d in self.devices]  # or doRead ???
        self.log.debug('_read: %s' % (', '.join(
                        ['%r is at %s' % (d, d.format(p))
                            for d, p in zip(self.devices, pos)])))
        hasprec = bool(self.precision)
        if hasprec:
            precisions = self.precision
            if len(precisions) == 1:
                precisions = [precisions[0]] * len(self.devices)
        for name, values in iteritems(self.mapping):
            if hasprec:
                for d, p, v, prec in zip(self.devices, pos, values, precisions):
                    if prec:
                        if abs(p - v) > prec:
                            break
                    elif p != v:
                        break
                else: # if there was no break we end here...
                    self.log.debug('_read we are at position %r' % name)
                    return name
            else:
                if tuple(pos) == tuple(values):
                    self.log.debug('_read we are at position %r' % name)
                    return name
        self.log.debug('_read we are at an unknown position!!!')
        return '<unknown>'

    def doRead(self, maxage=0):
        return self._read()
#        res = self._read()
#        if res != '<unknown>':
#            return res
#        raise PositionError(self, 'unknown position of %s' %
#                            ', '.join(str(d) for d in self.devices))

    def doStatus(self, maxage=0):
        '''determine status of this device'''
        # check if an underlying device is busy or in error
        self.log.debug('doStatus: checking underlying devices')
        for d in self.devices:
            st = d.status(0) # maybe doStatus ???
            if st[0] != status.OK:
                self.log.debug('doStatus: dev %r is at %s' % (d, formatStatus(st)))
                return st

        # devices are not busy, check if we are at an known position (yet)
        self.log.debug('doStatus: Devices are all idle, checking Position')
        pos = self._read()
        if self.target is not None:
            # somebody issued an start/move command already
            if self._starttime  is None:
                # poller needs its own copy of _starttime or the logic of the
                # following lines fail.
                self._starttime = time.time()
            if self.target == pos:
                # we are at the target -> good!
                self._starttime = None
                return status.OK, 'idle at %r' % pos
            elif self._starttime + self.timeout < time.time():
                # we are not there, but within out timeout -> busy
                self.log.debug('moving, will timeout in %.2fs' %
                            (self.timeout - time.time() + self._starttime))
                return status.BUSY, 'Moving'
            else:
                # we are neither at out target nor within our timeout -> Error!
                return status.ERROR, 'Target not reached within timeout!'
        else:
            # no target (yet)
            if pos != '<unknown>':
                # we know that position!
                return status.OK, 'idle at %r' % pos
            # signal in invalid position, but handle this (not yet) as a hard
            # error, allowing further moves
            return status.NOTREACHED, 'Unknown position'
