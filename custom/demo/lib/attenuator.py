#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""An virtual Attentuator"""

from nicos.core import status
from nicos.core.device import Moveable

from nicos.core import Attach, Override, Param
from nicos.core.mixins import HasLimits


class Attenuator(HasLimits, Moveable):
    """Attentuator with 3 elements having a transmission of 1/2, 1/4, and 1/16
    """

    attached_devices = {
        'blades': Attach('The blade devices',
                         Moveable,
                         multiple=3),
    }

    parameters = {
        'base': Param('Attenuating base (transmission = 1 / base ** n)',
                      default=2, userparam=False, settable=False,),
    }

    parameter_overrides = {
        'unit': Override(default='%', mandatory=False,),
        'abslimits': Override(mandatory=False, default=(0, 100),
                              settable=False),
    }

    def _attenuation(self, exp):
        return 100. * (1.0 - 1.0 / self.base ** exp)

    def doRead(self, maxage=0):
        exp = 0
        i = 1
        for blade in self._attached_blades:
            if blade.read(maxage) == 'in':
                exp += i
            i *= 2
        return self._attenuation(exp)

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStart(self, value):
        for pos in range(8):
            if value <= self._attenuation(pos) or pos == 7:
                # Move first in all needed blades into the beam to reduce the
                # activation and/or save the detector and then move out the not
                # needed ones
                for (idx, blade) in enumerate(self._attached_blades):
                    if pos & (1 << idx):
                        blade.maw('in')
                for (idx, blade) in enumerate(self._attached_blades):
                    if not (pos & (1 << idx)):
                        blade.maw('out')
                break
