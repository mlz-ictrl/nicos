#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, HasLimits, HasTimeout, Readable, Moveable, \
    Param, Override, intrange, oneof, status, listof, tupleof

from nicos.toftof import calculations as calc


class BaseChopperController(HasTimeout, Readable):

    parameters = {
        'ch5_90deg_offset': Param('Whether chopper 5 is mounted the right way '
                                  '(= 0) or with 90deg offset (= 1)',
                                  type=intrange(0, 1), default=0,
                                  category='general',
                                  ),
        'phase_accuracy': Param('Required accuracy of the chopper phases',
                                settable=True, default=10, type=float,),
        'speed_accuracy': Param('Required accuracy of the chopper speeds',
                                settable=True, default=2, type=float,),
        'resolution': Param('Current energy resolution',
                            volatile=True, type=tupleof(float, float),),

        'wavelength': Param('Selected wavelength',
                            unit='AA', settable=True, type=float,
                            default=4.5),
        'speed': Param('Disk speed',
                       unit='rpm', userparam=False, type=int, default=6000),
        'ratio': Param('Frame-overlap ratio',
                       type=int, settable=True, default=1),
        'crc': Param('Counter-rotating mode',
                     type=int, settable=True, default=1),
        'slittype': Param('Slit type',
                          type=int, settable=True, default=1),
        'phases': Param('Current phases',
                        type=listof(float), userparam=False, default=[0] * 8),
        'changetime': Param('Time of last change',
                            userparam=False, type=float,),
    }

    parameter_overrides = {
        'timeout': Override(default=90),
    }

    def _readspeeds(self):
        return [0] * 8

    def _getparams(self):
        return (self.wavelength, self.speed, self.ratio,
                self.crc, self.slittype)

    def doRead(self, maxage=0):
        """Read average speed from all choppers."""
        speeds = self._readspeeds()
        speed = 0.0
        for ch in [1, 2, 3, 4, 6, 7]:
            speed += speeds[ch - 1]
        if self.ratio is not None:
            if self.ratio == 1:
                speed += speeds[5 - 1]
            elif self.ratio < 9:
                speed += speeds[5 - 1] * self.ratio / (self.ratio - 1.0)
            else:
                speed += speeds[5 - 1] * self.ratio / 7.0
            return speed / 7.0
        else:
            return speed / 6.0

    def doReadResolution(self):
        return calc.Eres1(self.wavelength, self.speed)


class SpeedReadout(Readable):
    """The current speed readout device of the chopper."""
    attached_devices = {
        'chopper': Attach('Chopper controller', BaseChopperController),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='rpm'),
    }

    def doRead(self, maxage=0):
        return [v / 279.618375
                for v in self._attached_chopper._readspeeds_actual()]

    def doStatus(self, maxage=0):
        return status.OK, 'no status info'


class PropertyChanger(Moveable):
    """This is essentially a ParamDevice

    and can be replace once Controller uses single setters
    (NICOS-style interface).
    """
    attached_devices = {
        'chopper': Attach('Chopper controller', BaseChopperController),
    }

    def doStatus(self, maxage=0):
        return status.OK, 'no status info'

    def doRead(self, maxage=0):
        return getattr(self._attached_chopper, self._prop)

    def doStart(self, target):
        self._attached_chopper._change(self._prop, target)

    def doReadTarget(self):
        return getattr(self._attached_chopper, self._prop)


class Wavelength(HasLimits, PropertyChanger):
    """The wave length parameter device of the chopper."""
    _prop = 'wavelength'
    parameter_overrides = {
        'unit': Override(mandatory=False, default='AA'),
    }
    valuetype = float


class Speed(HasLimits, PropertyChanger):
    """The speed parameter device of the chopper."""
    _prop = 'speed'
    parameter_overrides = {
        'unit': Override(mandatory=False, default='rpm'),
    }
    valuetype = float


class Ratio(PropertyChanger):
    """The ratio parameter device of the chopper."""
    _prop = 'ratio'
    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(*range(1, 11))


class CRC(PropertyChanger):
    """The crc (rotation direction of disc 5) parameter device of the
    chopper.
    """
    _prop = 'crc'
    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(0, 1)


class SlitType(PropertyChanger):
    """The slit type parameter device of the chopper."""
    _prop = 'slittype'
    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
        'fmtstr': Override(default='%d'),
    }
    valuetype = oneof(0, 1, 2)
