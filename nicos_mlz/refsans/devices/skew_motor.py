#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm    <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Support Code 2 Motors: drive one, get one free: backguard left and right."""

from __future__ import absolute_import, division, print_function

from nicos.core import Moveable
from nicos.core.params import Attach, Param, floatrange
from nicos.devices.abstract import Motor


class SkewMotor(Motor):
    """Device moving by using two axes and having a fixed inclination.

    Both axis have a fixed inclination given by the ``skew`` parameter.  The
    position of the devices is given for the middle between both axis.  The
    ``motor_1`` device has always the smaller position value than the
    ``motor_2`` device.

    pos(motor_1) + skew / 2 == pos == pos(motor_2) - skew / 2.
    """

    attached_devices = {
        'motor_1': Attach('moving motor, 1', Moveable),
        'motor_2': Attach('moving motor, 2', Moveable),
    }

    parameters = {
        'skew': Param('Skewness of hardware, difference between both motors',
                      type=floatrange(0.), default=0.,
                      settable=True, unit='main'),
    }

    def _read_motors(self, maxage=0):
        return self._attached_motor_1.read(maxage), \
            self._attached_motor_2.read(maxage)

    def doRead(self, maxage=0):
        return sum(self._read_motors(maxage)) / 2.

    def doIsAtTarget(self, pos):
        if self.target is None:
            return True
        if not self._attached_motor_1.isAtTarget(pos - self.skew / 2.) or \
           not self._attached_motor_2.isAtTarget(pos + self.skew / 2.):
            return False
        m1, m2 = self._read_motors()
        self.log.debug('%.3f, %.3f, %.3f, %.3f', m1, m2, (m1 + self.skew / 2.),
                       (m2 - self.skew / 2.))
        return abs((m1 - m2 + self.skew)) <= self.precision

    def doStart(self, target):
        self._attached_motor_1.move(target - self.skew / 2.)
        self._attached_motor_2.move(target + self.skew / 2.)
