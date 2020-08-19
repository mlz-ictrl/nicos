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
#   Matthias Pomm    <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Devices with an inclination."""

from __future__ import absolute_import, division, print_function

from nicos.core import Readable
from nicos.core.mixins import HasOffset
from nicos.core.params import Attach, Param
from nicos.devices.abstract import Motor


class SkewRead(Readable):
    """Device having two axes and an inclination.

    The position is the mid between the motor_1 and motor_2 device.
    """

    attached_devices = {
        'motor_1': Attach('moving motor, 1', Readable),
        'motor_2': Attach('moving motor, 2', Readable),
    }

    def _read_motors(self, maxage=0):
        return [d.read(maxage) for d in self._adevs.values()]

    def doRead(self, maxage=0):
        return sum(self._read_motors(maxage)) / 2.


class SkewMotor(HasOffset, SkewRead, Motor):
    """Device moving by using two axes and having a fixed inclination.

    Both axis have a fixed inclination given by the ``skew`` parameter.  The
    position of the devices is given for the middle between both axis.  The
    ``motor_1`` device has always the smaller position value than the
    ``motor_2`` device.

    pos(motor_1) + skew / 2 == pos == pos(motor_2) - skew / 2.
    """

    parameters = {
        'skew': Param('Skewness of hardware, difference between both motor_1 '
                      'and motor_2',
                      type=float, default=0., settable=True, unit='main'),
    }

    def doIsAtTarget(self, pos):
        if self.target is None:
            return True
        if not self._attached_motor_1.isAtTarget(pos - self.skew / 2.) or \
           not self._attached_motor_2.isAtTarget(pos + self.skew / 2.):
            return False
        m1, m2 = self._read_motors()
        self.log.debug('%.3f, %.3f, %.3f, %.3f', m1, m2, (m1 + self.skew / 2.),
                       (m2 - self.skew / 2.))
        return abs(m1 - m2 + self.skew) <= self.precision

    def doStart(self, target):
        self._attached_motor_1.move(target - self.skew / 2.)
        self._attached_motor_2.move(target + self.skew / 2.)
