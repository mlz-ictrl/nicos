# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#  Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos.core import Attach
from nicos.core.device import Moveable
from nicos.core.utils import multiStatus
from nicos_sinq.amor.devices.base_defs import Distances



class AmorDeflector(Moveable):
    """
    AMOR is operated through a number of logical devices.
    This class implements these devices as parameters which
    in turn are provided as ParamDevices.
    """

    attached_devices = {
        'distances': Attach('distance provider', Distances),
        'kad': Attach('initial beam inclination', Moveable),
        'lom': Attach('deflector omega', Moveable),
        'ltz': Attach('deflector height', Moveable),
        'd2z': Attach('slit 2 height', Moveable),
        'f_zoffset': Attach('focal point height shift', Moveable),
        's_zoffset': Attach('sample height shift to reach focal point', Moveable),
        'soz': Attach('sample height', Moveable),
        'nu': Attach('Detector tilt', Moveable),
        'det_zoffset': Attach('detector offset', Moveable),
        'ka0': Attach('Beam inclination after guide', Moveable),
    }

    _wait_for = []

    def _startDevices(self, target):
        for name, value in target.items():
            dev = self._adevs[name]
            dev.start(value)
            self._wait_for.append(dev)

    def _getWaiters(self):
        return self._wait_for

    def doStatus(self, maxage=0):
        return multiStatus(self._adevs)

    def doRead(self, maxage=0):
        sx = self._attached_distances.sample
        lx = self._attached_distances.deflector
        f_zoffset = self._attached_f_zoffset.read(maxage)
        ka0 = self._attached_ka0.read(maxage)

        kap = -np.rad2deg(np.arctan2(f_zoffset, -(lx-sx))) + ka0
        if kap < 1.1*ka0:
            self.log.warning('assuming deflector is not in the beam')
            kap = ka0
        return kap

    def doStart(self, target):
        ka0 = self._attached_ka0.read(0)
        kad = self._attached_kad.read(0)
        sx = self._attached_distances.sample
        lx = self._attached_distances.deflector
        d2x = self._attached_distances.diaphragm2
        s_zoffset = self._attached_s_zoffset.read(0)

        positions = {}
        if target > 1.1*ka0:
            # assuming deflector is in the beam
            szd = (sx-lx) * (np.tan(np.deg2rad(ka0)) - np.tan(np.deg2rad(target)))
            positions['lom'] = (target+ka0)/2 + kad
            positions['ltz'] = szd - (lx-sx) * np.tan(np.deg2rad(target + kad))
        else:
            self.log.warning("'kap' < %4.2f deg can not be chosen: returning to %4.2f deg", (1.1 * ka0), ka0)
            szd = 0.
            positions['lom'] = ka0
            positions['ltz'] = 70
            target = ka0
        positions['f_zoffset'] = szd
        positions['d2z'] = szd + (sx-d2x) * np.tan(np.deg2rad(target+kad))
        positions['soz'] = szd + s_zoffset
        angle = target + kad
        positions['nu'] = angle
        self._startDevices(positions)
