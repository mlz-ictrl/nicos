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
#   Oleg Sobolev <oleg.sobolev@frm2.tum.de>
#
# *****************************************************************************

"""Magazin for monochanger. Modified Switcher class."""

from nicos.core import listof, anytype, ConfigurationError, PositionError, \
     NicosError, Moveable, Param, Override, oneof


class Lift(Moveable):

    attached_devices = {
        'moveable': (Moveable, 'The continuous device which is controlled'),
    }

    parameters = {
        'states':    Param('List of state names.', type=listof(str),
                           mandatory=True),
        'values':    Param('List of values to move to', type=listof(anytype),
                           mandatory=True),
        'sw_values': Param('List of values to move to', type=listof(anytype),
                           mandatory=True),
        'precision': Param('Precision for comparison', mandatory=True),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False),
    }

#    hardware_access = False

    def doInit(self, mode):
        states = self.states
        values = self.values
        sw_values = self.sw_values
        if (len(states) != len(values)) and (len(states) != len(sw_values)):
            raise ConfigurationError(self, 'Switcher states and values must be '
                                     'of equal length')
        self._switchlist = dict(zip(states, values))
        self._swlist = dict(zip(states, sw_values))
        self.valuetype = oneof(*self._switchlist)

    def doStart(self, target):
        # shouldn't happen...
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
            if abs(pos - value) <= prec:
                if self._readSwitch() ==  self._swlist[name]:
                    return name
        raise PositionError(self, 'unknown position of %s' %
                            self._adevs['moveable'])

    def doStatus(self, maxage=0):
        return self._adevs['moveable'].status(maxage)


    def _readSwitch(self):
        try:
            temp = self._adevs['moveable'].motor._adevs['bus'].get(self._adevs['moveable'].motor.addr,134)
            if temp & 64:
                return 'high'
            elif temp & 32:
                return 'low'
            elif temp & 128:
                return 'ref'
            else:
                return 0
        except Exception:
            raise NicosError(self, 'cannot evaluate status byte of stepper')
