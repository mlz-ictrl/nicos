# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#  Mark Koennecke <make.koennecke@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos.core import Attach, Device, Param, oneof, tupleof
from nicos.core.device import Moveable, Waitable
from nicos.core.errors import LimitError, NicosError


class Distances(Device):
    """
    A parameter class for holding all the distances required for
    the angle calculations. This will eventually be replaced by
    a class which detects the distances using the laser distance
    measuring device. But Roman is not ready yet...
    """

    parameters = {
      'deflector': Param('distance to deflector', type=float,
                         userparam=True, settable=True,
                         category='instrument'),
      'diaphragm1': Param('distance to slit 1', type=float,
                          userparam=True, settable=True,
                          category='instrument'),
      'diaphragm2': Param('distance to slit 2', type=float,
                          userparam=True, settable=True,
                          category='instrument'),
      'diaphragm3': Param('distance to slit3', type=float,
                          userparam=True, settable=True,
                          category='instrument'),
      'diaphragm4': Param('distance to slit4', type=float,
                          userparam=True, settable=True,
                          category='instrument'),
      'sample': Param('distance to sample', type=float,
                      userparam=True, settable=True,
                      category='instrument'),
      'detector': Param('distance to detector', type=float,
                        userparam=True, settable=True,
                        category='instrument'),
      'chopper': Param('distance to chopper', type=float,
                       userparam=True, settable=True,
                       category='instrument'),
      'nxoffset': Param('offset for NeXus files',
                        type=tupleof(float, float, float),
                        userparam=True, category='instrument'),
    }

    def doReadNxoffset(self):
        return 0, 0, -self.sample


class AmorDirector(Waitable):
    """
    AMOR is operated through a number of logical devices.
    This class implements these devices as parameters which
    in turn are provided as ParamDevices.
    """
    parameters = {
        'ka0': Param('Divergence aperture: Beam inclination after guide',
                     type=float, userparam=True, settable=True,
                     default=0.245),
        'kad': Param('Divergence aperture: Beam center offset', type=float,
                     volatile=True, userparam=True, settable=True),
        'div': Param('Divergence aperture: Incident beam diviergence',
                     type=float, userparam=True, settable=True, volatile=True),
        'mu':  Param('Sample: Angle between horizon and sample surface',
                     type=float, userparam=True, settable=True, volatile=True),
        'mud': Param('Sample: rocking angle', type=float,
                     userparam=True, settable=True),
        'szd': Param('Sample: Vertical focal point offset', type=float,
                     userparam=True, settable=True),
        'zoffset': Param('sample offset to instrument horizon',
                         type=float, userparam=True,
                         settable=True, volatile=True),
        'kappa': Param('Sample: Angle between horizon and nominal beam center',
                       type=float, userparam=True, settable=True,
                       volatile=True),
        'nu':  Param('Detector: Angle horizon to sample-detector', type=float,
                     userparam=True, settable=True, volatile=True),
        'nud': Param('Detector: Detector position offset', type=float,
                     userparam=True, settable=True),
        'mode': Param('AMOR mode',
                      type=oneof('deflector', 'simple', 'universal'),
                      userparam=True, settable=True, default='universal'),
    }

    attached_devices = {
        'distances': Attach('distance provider', Distances),
        'lom': Attach('deflector omega', Moveable),
        'ltz': Attach('deflector height', Moveable),
        'd2z': Attach('slit 2 height', Moveable),
        'soz': Attach('sample height', Moveable),
        'som': Attach('sample omega', Moveable),
        'com': Attach('Detector tilt', Moveable),
        'coz': Attach('detector offset', Moveable),
        'd3z': Attach('slit3 height', Moveable),
        'd1t': Attach('slit 1 top', Moveable),
        'd1b': Attach('slit 1 bottom', Moveable),
        'd2t': Attach('slit2 top', Moveable),
        'd2b': Attach('slit2 bottom', Moveable),
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
        status, txt = Waitable.doStatus(self, maxage)
        if status not in self.busystates:
            # reset _wait_for such that we can start multiple parameter
            self._wait_for = []
        return status, txt

    def doReadKappa(self):
        value = self.szd
        diff = self._attached_distances.sample -\
            self._attached_distances.deflector
        if diff > 0:
            kappa = np.rad2deg(np.arctan(-value/(diff) +
                               np.tan(np.deg2rad(self.ka0))))
        else:
            kappa = np.tan(np.deg2rad(self.ka0))
        return max(kappa, self.ka0)

    def doReadMu(self):
        return self._attached_som.read(0) - self.mud

    def doReadNu(self, maxage=0):
        return self._attached_com.read(maxage) - self.nud

    def doReadDiv(self):
        d1t = self._attached_d1t.read(0)
        d1b = self._attached_d1b.read(0)
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        if abs(sx-d1x) > 0:
            return np.rad2deg(np.arctan((d1t+d1b)/(sx-d1x)))
        return np.rad2deg(np.arctan((d1t+d1b)))

    def doReadKad(self):
        d1t = self._attached_d1t.read(0)
        d1b = self._attached_d1b.read(0)
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        if abs(sx-d1x) > 0:
            return np.rad2deg(np.arctan(0.5*(d1t-d1b)/(sx-d1x)))
        return np.rad2deg(np.arctan(0.5*(d1t-d1b)))

    def doReadZoffset(self):
        soz = self._attached_soz.read(0)
        return soz - self.szd

    def doWriteKappa(self, target):
        positions = {}

        ka0 = self.ka0
        kad = self.kad
        diff_dist = self._attached_distances.sample -\
            self._attached_distances.deflector
        if abs(target - ka0) < 0.1:
            positions['lom'] = ka0
            positions['ltz'] = 70
            target = ka0
        else:
            positions['lom'] = (target+ka0)/2 + kad
            positions['ltz'] = diff_dist * np.tan(np.deg2rad(ka0+kad))
        local_zoffset = self.zoffset
        self.szd = (diff_dist)*(np.tan(np.deg2rad(ka0)) -
                                np.tan(np.deg2rad(target)))
        positions['d2z'] = self.szd + (self._attached_distances.sample -
                                       self._attached_distances.diaphragm2) *\
            np.tan(np.deg2rad(target+kad))
        positions['soz'] = self.szd + local_zoffset
        if self.mode != 'universal':
            self.nu = 2. * self.mu + target + kad
        self._startDevices(positions)

    def doWriteMu(self, target):
        positions = {}
        positions['som'] = target + self.mud
        if self.mode == 'simple':
            self.nu = 2*target + self.kappa + self.kad
        self._startDevices(positions)

    def doWriteNu(self, target):
        positions = {}
        positions['com'] = target + self.nud
        szd = self.szd
        positions['coz'] = szd
        diff = self._attached_distances.diaphragm3 -\
            self._attached_distances.sample
        positions['d3z'] = szd + diff*np.tan(np.deg2rad(target))
        self._startDevices(positions)

    def doWriteDiv(self, target):
        positions = {}
        d2offset = .2
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        d2x = self._attached_distances.diaphragm2
        kad = self.kad
        positions['d1t'] = (sx-d1x) * np.tan(np.deg2rad(target/2. + kad))
        positions['d1b'] = (sx-d1x) * np.tan(np.deg2rad(target/2. - kad))
        positions['d2t'] = (sx-d2x) * np.tan(np.deg2rad(d2offset + target/2.))
        positions['d2b'] = (sx-d2x) * np.tan(np.deg2rad(d2offset + target/2.))
        self._startDevices(positions)

    def doWriteKad(self, target):
        positions = {}
        kap = self.kappa
        ka0 = self.ka0
        sx = self._attached_distances.sample
        lx = self._attached_distances.deflector
        d1x = self._attached_distances.diaphragm1
        d2x = self._attached_distances.diaphragm2
        if kap > 1.1*self.ka0:  # assuming deflector is in the beam
            positions['lom'] = (kap-ka0)/2. + target
            positions['ltz'] = (sx-lx) * (np.tan(np.deg2rad(kap+target)) -
                                          np.tan(np.deg2rad(kap)))
            positions['d1t'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2.
                                                            + target))
            positions['d1b'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2.
                                                            - target))
        else:
            positions['d1t'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2
                                                            + target))
            positions['d1b'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2.
                                                            - target))
            positions['d2z'] = (sx-d2x) * np.tan(np.deg2rad(kap+target))\
                + self.szd
            self.nu = 2*self.mu+kap+target
        self._startDevices(positions)

    def doWriteMud(self, target):
        if self.mode == 'deflector':
            raise LimitError('mud cannot be changed in deflector mode')
        positions = {}
        positions['som'] = self.mu + target
        self._startDevices(positions)

    def doWriteNud(self, target):
        positions = {}
        positions['com'] = self.nu + target
        self._startDevices(positions)

    def doWriteMode(self, target):
        if target == 'deflector':
            if abs(self.mu) > .01:
                raise NicosError('mu is not zero, aborted')
            self.kappa = 1.
        elif target == 'simple':
            self.kappa = self.ka0
            self.nu = 2. * self.mu + self.kappa + self.kad

    def doWriteZoffset(self, target):
        positions = {}
        positions['soz'] = self.szd + target
        self._startDevices(positions)

    def doRead(self, maxage=0):
        pass
