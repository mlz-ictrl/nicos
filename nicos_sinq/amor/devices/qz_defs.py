# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Override, Param, Waitable, LimitError
from nicos.core.device import Moveable
from nicos.core.mixins import HasLimits


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
        'det_nu': Attach('det_nu', HasLimits),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    hardware_access = False
    _wait_for = []

    def _startDevices(self, target):
        # Reset the list before each start command to avoid infinite growth
        self._wait_for.clear()
        for name, value in target.items():
            dev = self._adevs[name]
            dev.start(value)
            self._wait_for.append(dev)

    def _getWaiters(self):
        if self._wait_for:
            return self._wait_for
        return Waitable._getWaiters(self)

    def doRead(self, maxage=0):
        pass

    def doReadQl(self):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu  = self._attached_mu.read(0)
        return 4*np.pi * np.sin( np.deg2rad(mu + kappa + kad - 0.5*div) ) / 11.5

    def doReadQh(self):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu  = self._attached_mu.read(0)
        return 4*np.pi * np.sin( np.deg2rad(mu + kappa + kad + 0.5*div) ) / 3.5

    def doWriteQl(self, target):
        kappa = self._attached_kappa.read(0)
        kad = self._attached_kad.read(0)
        div = self._attached_div.read(0)
        mu = np.rad2deg(np.arcsin(target * 11.5 / (4*np.pi))) - kappa - kad + 0.5*div
        nu = 2*mu + kappa + kad
        allowed, msg = self._attached_det_nu.isAllowed(nu)
        if not allowed:
            raise LimitError(self, 'ql = %5.2f corresponds to nu = %5.2f deg, '
                             'which exceeds the limits: %s' % (target, nu, msg))

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
        allowed, msg = self._attached_det_nu.isAllowed(nu)
        if not allowed:
            raise LimitError(self, 'qh = %5.2f corresponds to nu = %5.2f deg, '
                             'which exceeds the limits: %s' % (target, nu, msg))

        self.log.info("moving 'mu' to %4.2f deg and 'nu' to %5.2f deg", mu, 2*mu+kappa+kad)
        positions = {}
        positions['mu'] = mu
        positions['nu'] = nu
        self._startDevices(positions)
