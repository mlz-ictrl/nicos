#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015 by the NICOS contributors (see AUTHORS)
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
#   bjoern.pedersen@frm2.tum.de
#
# *****************************************************************************

"""
Kappa goniometer module

main purposes:
 * handle dynamic limits
 * coord conversions
"""

from nicos.core import Attach
from nicos.core.device import Moveable
from nicos.core.mixins import IsController

from nicos.devices.sxtal.goniometer.base import PositionFactory, PositionBase


class KappaGon(IsController, Moveable):
    ''' Kappa goniometer base class'''

    attached_devices = {
        'ttheta': Attach('Two-theta device', Moveable),
        'omega': Attach('omega device', Moveable),
        'kappa': Attach('kappa device', Moveable),
        'phi': Attach('phi device', Moveable),
        'dx': Attach('detector movement device', Moveable),
    }


    def doRead(self, maxage=0):
        return PositionFactory('k',
                               ttheta=self._adevs['ttheta'].read(maxage),
                               omega=self._adevs['omega'].read(maxage),
                               kappa=self._adevs['kappa'].read(maxage),
                               phi=self._adevs['phi'].read(maxage),
                               )

    def doStart(self, pos):
        if isinstance(pos, PositionBase):
            target = pos.asK()
            self._adevs['ttheta'].start(target.theta * 2.)
            self._adevs['omega'].start(target.omega)
            self._adevs['kappa'].start(target.kappa)
            self._adevs['phi'].start(target.phi)
        else:
            raise ValueError('incorrect arguments for start, needs to be a PositionBase object')


    def isAdevTargetAllowed(self, adev, adevtarget):
        if adev == self._adevs['phi']:
            return True, 'Position allowed'  # phi can move freely
# for better visual indent
# pylint: disable=bad-indentation
        if adev == self._adevs['kappa']:
            if (-45 < self._adevs['omega'].target < 135 or
                135 < self._adevs['omega'].target < 255):
                    if -10 < adevtarget < 10:
                        return True, 'Position allowed'
                    else:
                        return False, ' -10 < kappa < 10 for  this omega position'

        if adev == self._adevs['omega']:
            if (self._adevs['ttheta'].target - adevtarget < 45):
                    return False, 'Omega too close to two-theta'
            else:
                    return True, 'Position OK'
        if adev == self._adevs['ttheta']:
            if (adevtarget - self._adevs['omega'].target < 45):
                    return False, 'Omega too close to two-theta'
            else:
                    return True, 'Position OK'
        return True, 'Position OK'
