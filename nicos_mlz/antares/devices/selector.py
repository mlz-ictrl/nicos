#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""Selector tilt motor for ANTARES with interlock."""

from __future__ import absolute_import, division, print_function

from nicos.core import Attach, HasLimits, Moveable, MoveError, Param
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod


class SelectorTilt(HasLimits, BaseSequencer):
    """Before the selector is allowed to tilt, the speed has to be reduced
    to a certain value.
    """

    attached_devices = {
        'selector': Attach('The selector speed', Moveable),
        'motor': Attach('The tilt motor', Moveable),
    }

    parameters = {
        'maxtiltspeed': Param('Maximum safe speed for tilting the selector',
                              mandatory=True, type=int, unit='rpm'),
    }

    def _generateSequence(self, target):
        seq = []
        if self._attached_selector.read(0) > self.maxtiltspeed:
            seq.insert(0, SeqDev(self._attached_selector, self.maxtiltspeed,
                                 stoppable=True))
        seq.append(SeqMethod(self, '_check_speed'))
        seq.append(SeqMethod(self._attached_motor, 'release'))
        seq.append(SeqDev(self._attached_motor, target, stoppable=True))
        seq.append(SeqMethod(self._attached_motor, 'fix',
                             'only move this using %s' % self))
        return seq

    def _check_speed(self):
        if self._attached_selector.read(0) > self.maxtiltspeed + 50:
            raise MoveError(self, 'selector not in safe speed range')

    def doRead(self, maxage=0):
        return self._attached_motor.read(maxage)

    def doIsAllowed(self, target):
        return self._attached_motor.isAllowed(target)

    def _getWaiters(self):
        return [self._attached_motor]
