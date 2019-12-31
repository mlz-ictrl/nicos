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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Refsans specific devices for 'alphaf'."""

from __future__ import absolute_import, division, print_function

from math import atan2, cos, degrees, radians, sin, tan

import numpy as np

from nicos.core import Moveable, Readable
from nicos.core.mixins import HasLimits
from nicos.core.params import Attach, Override, Param, floatrange, tupleof


class TubeAngle(HasLimits, Moveable):
    """Angle of the tube controlled by the yoke."""

    attached_devices = {
        'yoke': Attach('Yoke device', Moveable),
    }

    parameters = {
        'yokepos': Param('Position of yoke from pivot point',
                         type=floatrange(0, 20000), unit='mm', default=11000),
    }

    parameter_overrides = {
        'abslimits': Override(mandatory=False, volatile=True),
        'unit': Override(mandatory=False, default='deg'),
    }

    def doRead(self, maxage=0):
        return degrees(atan2(self._attached_yoke.read(maxage), self.yokepos))

    def doStart(self, target):
        self._attached_yoke.move(tan(radians(target)) * self.yokepos)

    def doReadAbslimits(self):
        yokelimits = self._attached_yoke.userlimits
        return (degrees(atan2(yokelimits[0], self.yokepos)),
                degrees(atan2(yokelimits[1], self.yokepos)))


class DetAngle(HasLimits, Moveable):
    """Angle of the outgoing (centered) beam to detector."""

    attached_devices = {
        'tubeangle': Attach('Angle of the tube to the ground', Moveable),
        'tubepos': Attach('Position of detector inside tube', Readable),
        'pivot': Attach('Position of the pivot point', Readable),
        'theta': Attach('Tilt angle of the sample', Readable, optional=True),
    }

    parameters = {
        'pivot1pos': Param('Distance of the pivot point 1 from wall',
                           type=floatrange(0), mandatory=False, default=290,
                           unit='mm'),
        'b2pos': Param('Distance of B2 aperture from wall',
                       type=floatrange(0), mandatory=False, default=165,
                       unit='mm'),
        'b3pos': Param('Distance of B3 aperture from wall',
                       type=floatrange(0), mandatory=False, default=285,
                       unit='mm'),
        'samplepos': Param('Distance of sample from B3',
                           type=floatrange(0), mandatory=False, default=50,
                           unit='mm'),
        'detheight': Param('Height of the detector',
                           type=floatrange(0), mandatory=False, default=533.715,
                           unit='mm'),
        # calculated from the beamheight - pivot.height - (256 - 160) * 2.093 mm
        # Beam height at 0 deg is in pixel 160 counted from top pixel (256)
        # times pixel size (2.093 mm)
        'detoffset': Param('Offset from virtual tube base to lower edge of '
                           'detector',
                           type=floatrange(0), mandatory=False,
                           default=619.772, unit='mm'),
        'beamheight': Param('Height of beam above ground level',
                            type=floatrange(0), mandatory=False,
                            default=1193.7, unit='mm'),
        'range': Param('range of angles between upper and lower detector edge',
                       type=tupleof(float, float), volatile=True,
                       unit='deg, deg', internal=True, preinit=False),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='deg'),
        'abslimits': Override(mandatory=False, volatile=True),
    }

    def doPreinit(self, mode):
        # center of the detector in respect to the tube base line
        self._detcenter = self.detheight / 2 + self.detoffset
        self._yoffset = self.beamheight - self._attached_pivot.height

    def doInit(self, mode):
        self._func = np.vectorize(self._alpha)

    def doRead(self, maxage=0):
        self._update(maxage)
        beta = self._attached_tubeangle.read(maxage)
        self.log.debug('Tube angle: %.3f', beta)
        alphaf = self._alpha(beta)
        if self._attached_theta:
            alphaf -= self._attached_theta.read(maxage)
        return alphaf

    def _update(self, maxage=0):
        pivot = self._attached_pivot
        # Calculate the distance between sample and pivot point
        self._xoffset = self.pivot1pos + pivot.grid * (
            pivot.read(maxage) - 1) - (self.samplepos + self.b3pos)
        self.log.debug('Sample pivot distance : %.1f', self._xoffset)
        self._tpos = self._attached_tubepos.read(maxage)

    def _alpha(self, beta):
        beta = radians(beta)
        # calculate the detector center position in respect to sample
        x = self._xoffset + self._tpos * cos(beta) - self._detcenter * sin(beta)

        # calculate the height of the detector center in respect to the ground
        y = self._tpos * sin(beta) + self._detcenter * cos(beta) - self._yoffset
        return degrees(atan2(y, x))

    def doStart(self, target):
        self._update(0)
        x = np.arange(self.absmin, self.absmax + 0.01, 0.01)
        y = self._func(x)
        if self._attached_theta:
            target += self._attached_theta.read(0)
        val = np.interp(target, y, x)
        self.log.debug('new beta: %f', val)
        self._attached_tubeangle.start(val)

    def doReadAbslimits(self):
        return self._attached_tubeangle.abslimits

    def doReadRange(self):
        alpha = self.doRead(0)
        opening = degrees(atan2(self.detheight, self._tpos)) / 2.
        return (alpha - opening, alpha + opening)
