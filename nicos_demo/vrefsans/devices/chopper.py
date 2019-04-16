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
#   Jens Krüger <jens.krueger@frm2.tum.de
#
# *****************************************************************************

"""Virtual chopper devices for testing."""

from __future__ import absolute_import, division, print_function

from nicos.core import status
from nicos.core.device import Moveable
from nicos.core.mixins import IsController
from nicos.core.params import Attach, Override, Param, floatrange, intrange, \
    limits, oneof
from nicos.devices.abstract import CanReference
from nicos.devices.generic.virtual import VirtualMotor


class ChopperDisc(VirtualMotor):
    parameters = {
        'phase': Param('Phase of chopper',
                       type=floatrange(0, 360), settable=True, userparam=True,
                       unit='deg',
                       ),
        # 'phase': Param('Phase in respect to the first disc',
        #                type=floatrange(-180, 180), default=0, settable=True,
        #                ),
        'current': Param('motor current',
                         settable=False, userparam=True, volatile=True,
                         fmtstr='%.3f', unit='A',
                         ),
        'mode': Param('Internal mode',
                      type=int, settable=False, userparam=True,
                      # volatile=True,
                      ),
        'chopper': Param('chopper number inside controller',
                         type=intrange(1, 6), settable=False, userparam=True,
                         default=2,
                         ),
        'reference': Param('reference to Disc one',
                           type=floatrange(-360, 360), settable=False,
                           userparam=True,
                           ),
        'gear': Param('Chopper ratio',
                      type=intrange(-6, 6), settable=False, userparam=True,
                      default=0,
                      ),
        # 'gear': Param('Gear',
        #               type=float, default=1, settable=True,
        #               ),
        'edge': Param('Chopper edge of neutron window',
                      type=oneof('open', 'close'), settable=False,
                      userparam=True,
                      ),
        'crc': Param('Counter-rotating mode',
                     type=int, default=1, settable=True,
                     ),
        'slittype': Param('Slit type',
                          type=int, default=1, settable=True,
                          ),
    }

    parameter_overrides = {
        'unit': Override(default='rpm', mandatory=False,),
        'abslimits': Override(default=(0, 6000), mandatory=False),
        'precision': Override(default=2),
        'jitter': Override(default=2),
        'curvalue': Override(default=1200),
        'speed': Override(default=50),
        'fmtstr': Override(default='%.f'),
    }

    def doReadCurrent(self):
        speed = self.read()
        if abs(speed) > self.jitter:
            return 2 + speed * 0.001
        return 0

    def doPoll(self, n, maxage):
        self._pollParam('current')

    def _isStopped(self):
        return abs(self.read(0)) <= self.precision


class ChopperDisc2(IsController, ChopperDisc):
    """Chopper disc 2 device.

    Since the chopper disc 2 can be translated, the chopper speed must be low
    enough (around 0, defined by its precision).

    The change of speed must be blocked if the translation device is not at
    a defined position.
    """

    attached_devices = {
        'translation': Attach('Chopper translation device', Moveable),
    }

    def isAdevTargetAllowed(self, dev, target):
        if self._isStopped():
            return True, ''
        return False, 'Disc speed is too high, %.0f!' % self.read(0)

    def doIsAllowed(self, target):
        state = self._attached_translation.status()
        if state[0] == status.OK:
            return True, ''
        return False, 'translation is: %s' % state[1]


class ChopperDisc2Pos(CanReference, VirtualMotor):
    """Position of chopper disc 2 along the x axis."""

    valuetype = intrange(1, 5)

    parameter_overrides = {
        'unit': Override(default='', mandatory=False),
        'abslimits': Override(mandatory=False, default=limits((1, 5))),
        'fmtstr': Override(default='%d'),
        'speed': Override(default=0.1),
    }

    def doRead(self, maxage=0):
        try:
            return self.valuetype(VirtualMotor.doRead(self, maxage))
        except ValueError:
            return self.target

    def doReference(self, *args):
        self.move(1)
