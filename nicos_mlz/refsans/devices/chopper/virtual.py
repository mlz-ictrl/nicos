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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual chopper devices for testing."""

from nicos.core.params import Attach, Override, Param, intrange
from nicos.devices.generic.virtual import VirtualMotor

from nicos_mlz.refsans.devices.chopper.base import \
    ChopperDisc as ChopperDiscBase, ChopperDisc2 as ChopperDisc2Base, \
    ChopperDiscTranslation as ChopperDiscTranslationBase


class ChopperDisc(ChopperDiscBase, VirtualMotor):
    parameters = {
        'crc': Param('Counter-rotating mode',
                     type=int, default=1, settable=True),
        'slittype': Param('Slit type',
                          type=int, default=1, settable=True),
    }

    parameter_overrides = {
        'jitter': Override(default=2),
        'curvalue': Override(default=1200),
        'speed': Override(default=50),
    }

    def doReadCurrent(self):
        speed = self.read()
        if abs(speed) > self.jitter:
            return 2 + speed * 0.001
        return 0

    def doPoll(self, n, maxage):
        self._pollParam('current')


class ChopperDisc1(ChopperDisc):

    attached_devices = {
        'discs': Attach('slave choppers', ChopperDisc, multiple=5),
    }

    def doStart(self, target):
        for dev in self._attached_discs:
            dev.start(target)
        ChopperDisc.doStart(self, target)

    def _getWaiters(self):
        return []


class ChopperDisc2(ChopperDisc2Base, ChopperDisc):
    """Chopper disc 2 device."""
    parameter_overrides = {
        'pos': Override(type=intrange(0, 5), volatile=True, settable=True,
                        fmtstr='%d', unit=''),
    }


class ChopperDiscTranslation(ChopperDiscTranslationBase, VirtualMotor):
    """Position of chopper disc along the x axis.

    Since the chopper disc 2 can be translated, the chopper speed must be low
    enough (around 0, defined by its precision).

    The change of speed must be blocked if the translation device is not at
    a defined position.
    """

    parameter_overrides = {
        'speed': Override(default=0.1),
        'fmtstr': Override(default='%.0f'),
    }

    def doRead(self, maxage=0):
        try:
            val = VirtualMotor.doRead(self, maxage)
            if not self.isAtTarget(val):
                # This is because of cutting to int values. If the target is
                # lower than val the cut would give the wrong result.
                if self.target - val < 0:
                    val += 1.
            return self.valuetype(val)
        except ValueError:
            return self.target
