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
#    Jochen Stahn <jochen.stahn@psi.ch>
# *****************************************************************************

import numpy as np

from nicos.core import Attach, Override, Param, Waitable
from nicos.core.device import Moveable


class AmorQz(Waitable):
    """
    AMOR is operated through a number of logical devices.
    This class implements these devices as parameters which
    in turn are provided as ParamDevices.
    """
    parameters = {
        'ql': Param('minimal normal momentum transfer',
                    type=float, userparam=True, settable=True, volatile=True),
        'qh': Param('maximal normal momentum transfer',
                    type=float, userparam=True, settable=True, volatile=True),
    }

    attached_devices = {
        'div': Attach('div', Moveable),
        'kappa': Attach('kappa', Moveable),
        'kad': Attach('kad', Moveable),
        'sample_tilt': Attach('sample alignment tilt', Moveable),
        'mu': Attach('mu', Moveable),
        'nu': Attach('nu', Moveable),
        'det_nu': Attach('det_nu', Moveable),
    }

    # Note to Jochen:
    # A "Waitable" by default needs a unit. For our device however, this does not make sense; hence we remove the unit requirement
    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    _wait_for = []

    def _startDevices(self, target):
        # Reset the list before each start command to avoid infinite growth
        self._wait_for.clear()
        for name, value in target.items():
            dev = self._adevs[name]
            dev.start(value)
            self._wait_for.append(dev)

    def _getWaiters(self):
        return self._wait_for

    def doRead(self, maxage=0):
        pass

    def doReadQl(self):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu  = self._attached_mu.read(0)
        #nu  = self._attached_nu.read(0)
        #offset = nu - (2*mu + kappa + kad)
        #if abs(offset) > 0.1:
        #    self.log.warning(f"detector angle 'nu' is off by {offset:5.2f} deg")
        return 4*np.pi * np.sin( np.deg2rad(mu + kappa + kad - 0.5*div) ) / 11.5

    def doReadQh(self):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu  = self._attached_mu.read(0)
        #nu  = self._attached_nu.read(0)
        #offset = nu - (2*mu + kappa + kad)
        #if abs(offset) > 0.1:
        #    self.log.warning(f"detector angle 'nu' is off by {offset:5.2f} deg")
        return 4*np.pi * np.sin( np.deg2rad(mu + kappa + kad + 0.5*div) ) / 3.5

    def doWriteQl(self, target):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu = np.rad2deg(np.arcsin(target * 11.5 / (4*np.pi))) - kappa - kad + 0.5*div
        nu = 2*mu + kappa + kad
        if nu>self._attached_det_nu.absmax:
            self.log.warning('ql = %5.2f corresponds to nu = %5.2f, which exceeds the hardware limits', target, nu)
        else:
            self.log.info("moving 'mu' to %4.2f deg and 'nu' to %5.2f deg", mu, 2*mu+kappa+kad)
            positions = {}
            positions['mu'] = mu
            positions['nu'] = nu
            self._startDevices(positions)

    def doWriteQh(self, target):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu = np.rad2deg(np.arcsin(target * 3.5 / (4*np.pi))) - kappa - kad - 0.5*div
        nu = 2*mu + kappa + kad
        if nu>self._attached_det_nu.absmax:
            self.log.warning('qh = %5.2f corresponds to nu = %5.2f, which exceeds the hardware limits', target, nu)
        else:
            self.log.info("moving 'mu' to %4.2f deg and 'nu' to %5.2f deg", mu, 2*mu+kappa+kad)
            positions = {}
            positions['mu'] = mu
            positions['nu'] = nu
            self._startDevices(positions)
