#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos.core import Attach, Moveable, Param, listof, tupleof

from nicos_ess.devices.epics.motor import EpicsMotor
from nicos_sinq.devices.epics.generic import WindowMoveable


class VSForbiddenMoveable(WindowMoveable):
    """
    Velocity selectors have forbidden regions in which they are
    not supposed to run for reason of excessive vibration. This class
    checks for this
    """

    parameters = {
        'forbidden_regions': Param('List of forbidden regions',
                                   type=listof(tupleof(float, float)),
                                   mandatory=True)
    }

    valuetype = float

    def doIsAllowed(self, value):
        for region in self.forbidden_regions:
            if region[0] < value < region[1]:
                return False, \
                       'Desired value value is within ' \
                       'forbidden region %f to %f' \
                       % (region[0], region[1])
        return True, ''


class VSTiltMotor(EpicsMotor):
    """
    The tilt motor for a velocity selector can only be moved when
    the selector is standing. This class ensures just that.
    """
    attached_devices = {
        'vs_rotation': Attach('Velcocity Selector Rotation',
                              Moveable),
    }

    parameters = {
        'limit': Param('Limit below which the rotation is considered standing',
                       type=float, mandatory=True)
    }

    def doIsAllowed(self, target):
        if self._attached_vs_rotation.read(0) > self.limit:
            return False, \
                   'Velocity Selector must be stopped before moving tilt'
        return True, ''

    def doStart(self, target):
        EpicsMotor.doStart(self, target)


class VSLambda(Moveable):
    """
    SINQ uses a different way to calculate the wavelength then
    implemented in NICOS. This has been copied from SICS.
    """

    attached_devices = {
        'seldev':  Attach('The selector speed device', Moveable),
        'tiltdev': Attach('The tilt angle motor, if present', Moveable,
                          optional=True),
    }

    def _calcCoefficients(self):
        tilt = self._attached_tiltdev.read(0)
        tsq = tilt*tilt
        tter = tilt*tsq
        tquat = tter*tilt

        A = 0.01223 + (0.000360495 * tilt) + (0.000313819 * tsq) + \
            (0.0000304937 * tter) + (0.000000931533 * tquat)

        B = 12721.11905 - (611.74127 * tilt) - (12.44417 * tsq) - \
            (0.12411 * tter) + (0.00583 * tquat)
        return A, B

    def doRead(self, maxage):
        spd = self._attached_seldev.read(maxage)
        if spd > 0:
            A, B = self._calcCoefficients()
            return A + B / spd
        return 0

    def doIsAllowed(self, value):
        if value == 0:
            return False, 'zero wavelength not allowed'
        A, B = self._calcCoefficients()
        speed = B/(value - A)
        allowed, why = self._attached_seldev.isAllowed(speed)
        if not allowed:
            why = 'requested %d rpm, %s' % (speed, why)
        return allowed, why

    def doStart(self, target):
        A, B = self._calcCoefficients()
        speed = B/(target - A)
        self.log.debug('moving selector to %d rpm', speed)
        self._attached_seldev.start(speed)
