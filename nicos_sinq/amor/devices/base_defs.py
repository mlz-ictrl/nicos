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
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos.core import Attach, Device, Override, Param, Waitable, tupleof
from nicos.core.device import Moveable


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

class AmorBase(Waitable):
    """
    AMOR is operated through a number of logical devices.
    This class implements these devices as parameters which
    in turn are provided as ParamDevices.
    """
    parameters = {
        'div': Param('Divergence aperture: Incident beam divergence',
                     type=float, userparam=True, settable=True, volatile=True),
        'ka0': Param('Divergence aperture: Beam inclination after guide',
                     type=float, userparam=True, settable=True),
        'kad': Param('Divergence aperture: Beam center offset', type=float,
                     volatile=True, userparam=True, settable=True),
        'fzoffset': Param('vertical focal point offset',
                          type=float, userparam=True, settable=True, volatile=True),
        'szoffset': Param("sample alignment offset realised by 'soz'",
                          type=float, userparam=True, settable=True, volatile=True),
        'sampletilt': Param('sample alignment tilt angle', type=float,
                            userparam=True, settable=True, volatile=True),
        'mu': Param('Sample: Angle between horizon and sample surface',
                    type=float, userparam=True, settable=True, volatile=True),
        'nu': Param('Detector: Angle horizon to sample-detector',
                    type=float, userparam=True, settable=True, volatile=True),
        'alphai': Param('mean incident angle on sample surface',
                        type=float, userparam=True, settable=True, volatile=True),
        'alphaf': Param('mean final angle (detector position)',
                        type=float, userparam=True, settable=True, volatile=True),
    }

    attached_devices = {
        'distances': Attach('distance provider', Distances),
        'd1b': Attach('slit 1 bottom', Moveable),
        'd1t': Attach('slit 1 top', Moveable),
        'd2z': Attach('slit 2 height', Moveable),
        'd2b': Attach('slit2 bottom', Moveable),
        'd2t': Attach('slit2 top', Moveable),
        'd3b': Attach('slit3 bottom', Moveable),
        'd3t': Attach('slit3 top', Moveable),
        'soz': Attach('sample height', Moveable),
        'f_zoffset_target': Attach('Manual moveable holding the target for f_zoffset', Moveable),
        's_zoffset_target': Attach('Manual moveable holding the target for s_zoffset', Moveable),
        'som': Attach('sample omega', Device),
        'sample_tilt_target': Attach('Manual moveable holding the target for sample_tilt', Moveable),
        'd3z': Attach('slit3 height', Moveable),
        'det_zoffset': Attach('Detector tilt', Moveable),
        'det_nu': Attach('detector offset', Moveable),
        'kappa': Attach('beam inclination', Moveable),
    }

    # A "Waitable" by default needs a unit. Here this does not make sense.
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

    def doRead(self, maxage = 0):
        return 0

    def doReadDiv(self, maxage = 0):
        d1t = self._attached_d1t.read(0)
        d1b = self._attached_d1b.read(0)
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        return np.rad2deg(np.arctan((d1t+d1b)/np.abs(d1x-sx)))

    def doWriteDiv(self, target):
        d2offset = .2
        limit = 1.8
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        d2x = self._attached_distances.diaphragm2
        kad = self.kad
        # check for possible divergences
        if target + 2*np.abs(self.kad) < limit:
            positions = {}
            positions['d1t'] = (sx-d1x) * np.tan(np.deg2rad(target/2. + kad))
            positions['d1b'] = (sx-d1x) * np.tan(np.deg2rad(target/2. - kad))
            if self._attached_d2t.connected:
                positions['d2t'] = (sx-d2x) * np.tan(np.deg2rad(d2offset + target/2.))
                positions['d2b'] = (sx-d2x) * np.tan(np.deg2rad(d2offset + target/2.))
            self._startDevices(positions)
        else:
            self.log.warning("divergence exceeds diaphragm limits. (div + 2|kad| < %f)", limit)

    def doReadAlphai(self, maxage=0):
        return self.mu + self._attached_kappa.read(0) + self.kad

    def doReadAlphaf(self, maxage=0):
        return self.nu - self.mu

    def doReadKad(self, maxage = 0):
        d1t = self._attached_d1t.read(0)
        d1b = self._attached_d1b.read(0)
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        return np.rad2deg(np.arctan(0.5*(d1t-d1b)/np.abs(d1x-sx)))

    def doWriteKad(self, target):
        limit = 1.8
        ka0 = self.ka0
        sx = self._attached_distances.sample
        d1x = self._attached_distances.diaphragm1
        d2x = self._attached_distances.diaphragm2
        fzoffset = self.fzoffset
        if self.div + 2*np.abs(target) < limit :
            positions = {}
            positions['d1t'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2. + target))
            positions['d1b'] = (sx-d1x) * np.tan(np.deg2rad(self.div/2. - target))
            #if self._attached_d2z.connected:
            positions['d2z'] = (sx-d2x) * np.tan(np.deg2rad(target+ka0)) + fzoffset
            self._startDevices(positions)
        else:
            self.log.warning("'kad' exceeds diaphragm limits. (div + 2|kad| < %f)", limit)

    def doReadFzoffset(self, maxage=0):
        target = self._attached_f_zoffset_target.read(maxage)
        if target is None:
            self.log.warning('No cached value for fzoffset found, using 0.0')
            return 0.0
        return target

    def doWriteFzoffset(self, target):
        self._attached_f_zoffset_target.maw(target)
        szoffset = self.szoffset
        positions = {}
        positions['soz'] = szoffset + target
        self._startDevices(positions)

    def doReadSzoffset(self, maxage=0):
        target = self._attached_s_zoffset_target.read(maxage)
        if target is None:
            self.log.warning('No cached value for szoffset found, using 0.0')
            return 0.0
        return target

    def doWriteSzoffset(self, target):
        self._attached_s_zoffset_target.maw(target)
        fzoffset = self.fzoffset
        positions = {}
        positions['soz'] = target + fzoffset
        self._startDevices(positions)

    def doReadSampletilt(self, maxage=0):
        target = self._attached_sample_tilt_target.read(maxage)
        if not target:
            self.log.warning('No cached value for sampletilt found, using 0.0')
            return 0.0
        return target

    def doWriteSampletilt(self, target):
        positions = {}
        positions['som'] = target + self.mu
        self._startDevices(positions)
        self._attached_sample_tilt_target.maw(target)

    def doReadMu(self, maxage=0):
        return self._attached_som.read(maxage) - self.sampletilt

    def doWriteMu(self, target):
        positions = {}
        positions['som'] = target + self.sampletilt
        self._startDevices(positions)

    def doReadNu(self, maxage=0):
        #if self._attached_d3z.connected:
            #sx = self._attached_distances.sample
            #d3x = self._attached_distances.diaphragm3
            #fzoffset = self.fzoffset
            #angle = self._attached_det_nu.read(maxage)
            #d3z_pos = fzoffset + (d3x-sx) * np.tan(np.deg2rad(angle))
            #offset = d3z_pos - self._attached_d3z.read(maxage)
            #if abs( offset ) > 0.1:
            #    self.log.warning(f'diaphragm D3 is off position by {offset:5.2f} mm')
        #return det_nu
        # TODO: is nud still necessary?
        # return self._attached_det_nu.read(maxage) - self.nud
        return self._attached_det_nu.read(maxage)

    def doWriteNu(self, target):
        d3offset = 0.2
        sx = self._attached_distances.sample
        d3x = self._attached_distances.diaphragm3
        div = self.div
        fzoffset = self.fzoffset
        angle = target
        positions = {}
        #positions['det_nu'] = angle + self.nud
        positions['det_nu'] = angle
        positions['det_zoffset'] = fzoffset
        if self._attached_d3z.connected:
            positions['d3z'] = fzoffset + (d3x-sx) * np.tan(np.deg2rad(angle))
            if self._attached_d3t.enabled:
                positions['d3t'] = np.tan(np.deg2rad(div/2 + d3offset)) * \
                    (d3x-sx) + np.tan(np.deg2rad(np.abs(target) + div/2)) * 15.
            if self._attached_d3b.enabled:
                positions['d3t'] = np.tan(np.deg2rad(div/2 + d3offset)) * \
                    (d3x-sx) + np.tan(np.deg2rad(np.abs(target) + div/2)) * 15.
        self._startDevices(positions)
