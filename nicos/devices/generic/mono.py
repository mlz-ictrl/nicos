#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2017-2018 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
"""
Base monochromator class
"""

from math import pi, sqrt

from nicos.core import ComputationError, Moveable, Override, \
    ProgrammingError, oneof, status, MASTER, SIMULATION

THZ2MEV = 4.1356675
ANG2MEV = 81.804165


def from_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return ANG2MEV * value ** 2 / (2 * pi) ** 2
        elif unit == 'THz':
            return ANG2MEV / THZ2MEV * value ** 2 / (2 * pi) ** 2
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError(
            'cannot convert %s A-1 to %s: %s' % (value, unit, err))


def to_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return 2.0 * pi * sqrt(value / ANG2MEV)
        elif unit == 'THz':
            return 2.0 * pi * sqrt(value * THZ2MEV / ANG2MEV)
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError(
            'cannot convert %s A-1 to %s: %s' % (value, unit, err))


class Monochromator(Moveable):
    """General monochromator device.

    It supports setting the `unit` parameter to different values.

    * "A-1" -- wavevector in inverse Angstrom
    * "A" -- wavelength in Angstrom
    * "meV" -- energy in meV
    * "THz" -- energy in THz

    """

    hardware_access = False

    parameters = {}

    parameter_overrides = {
        'unit':
            Override(
                default='A-1',
                type=oneof('A-1', 'A', 'meV', 'THz'),
                chatty=True),
        'fmtstr':
            Override(default='%.3f'), }

    def doInit(self, mode):
        if ('target' not in self._params or not self.target or
            self.target == 'unknown'):
            self._setROParam('target', from_k(to_k(0.73, 'A'), self.unit))

    def doStart(self, pos):
        self._sim_setValue(pos)

    def doIsAllowed(self, pos):
        return True, ''

    def doRead(self, maxage=0):
        return self.target

    def doStatus(self, maxage=0):
        return status.OK, ""

    def doReadPrecision(self):
        return 0

    def doWriteUnit(self, value):
        if self._cache:
            self._cache.invalidate(self, 'value')

    def doUpdateUnit(self, value):
        if 'unit' not in self._params:
            # this is the initial update
            return
        if self._mode not in (MASTER, SIMULATION):
            # change limits only from the master copy, or in simulation mode
            return
        if 'target' in self._params and self.target and self.target != 'unknown':
            # this should be still within the limits
            self._setROParam(
                'target', from_k(to_k(self.target, self.unit), value))
        self.read(0)
