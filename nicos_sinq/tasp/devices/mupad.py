# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import numpy as np

from nicos.core import Moveable, Readable
from nicos.core.params import Attach, Override, Param, listof, oneof, tupleof
from nicos.devices.abstract import TransformedMoveable
from nicos.devices.generic.mono import Monochromator, to_k


class Mupad(Moveable):
    """
    Device for the PSI mupad.
    """

    hardware_access = False

    parameters = {
        'w1': Param('Weight 1', type=float, default=10.3,
                    settable=True, userparam=True),
        'w2': Param('Weight 2', type=float, default=10.3,
                    settable=True, userparam=True),
        'w3': Param('Weight 3', type=float, default=10.3,
                    settable=True, userparam=True),
        'w4': Param('Weight 4', type=float, default=10.3,
                    settable=True, userparam=True),
        'p1': Param('Phase shift 1', type=float, default=0,
                    settable=True, userparam=True),
        'p2': Param('Phase shift 2', type=float, default=0,
                    settable=True, userparam=True),
        'p3': Param('Phase shift 3', type=float, default=0,
                    settable=True, userparam=True),
        'p4': Param('Phase shift 4', type=float, default=0,
                    settable=True, userparam=True),
        'last_currents': Param('last known currents', type=listof(float),
                               settable=True, internal=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'i1': Attach('Magnet 1', Moveable),
        'i2': Attach('Magnet 1', Moveable),
        'i3': Attach('Magnet 1', Moveable),
        'i4': Attach('Magnet 1', Moveable),
        'mono': Attach('Monochromator', Monochromator),
        'ana': Attach('Analyser', Monochromator),
        'a4': Attach('A4', Readable),
    }

    valuetype = tupleof(float, float, float, float, float, float)

    def calc_q_vector(self):
        ki = np.array([to_k(self._attached_mono.read(0), 'meV'), 0, 0])
        kfabs = to_k(self._attached_ana.read(0), 'meV')
        a4 = np.radians(self._attached_a4.read(0))
        kf = np.array([kfabs*np.cos(a4), kfabs*np.sin(a4), 0])
        q = ki - kf
        if np.sqrt(float(q.dot(q))) < 0.001:
            q = ki
        return q

    def angle(self, v1, v2):
        uv1 = v1/np.linalg.norm(v1)
        uv2 = v2/np.linalg.norm(v2)
        dp = np.dot(uv1, uv2)
        return np.arccos(dp)

    def calc_chi_phi_incoming(self, target):
        ki = np.array([to_k(self._attached_mono.read(), 'meV'), 0, 0])
        pi = np.array(target[0:3])
        q = self.calc_q_vector()
        angle_kiq = self.angle(ki, q)

        angle_kiq_cross = np.cross(ki, q)
        if angle_kiq_cross[2] < 0:
            angle_kiq = angle_kiq * -1.

        theta = self.angle(pi, np.array([0, 0, 1.]))

        piv = np.array([target[0], target[1], 0])
        if np.sqrt(piv.dot(piv)) > .01:
            phi = self.angle(piv, np.array([1., 0, 0]))
        else:
            phi = 0

        phicross = np.cross(np.array([1., 0, 0]), piv)
        if phicross[2] < 0:
            phi = phi * -1

        if np.abs(theta) < .01 or np.abs(theta - np.pi) < .01:
            phi = 0
        else:
            phi = angle_kiq + phi

        # now make corrections to these angles in order to
        # use as less current as possible in coils
        if phi > np.pi / 2:
            theta = -1.0 * theta
            phi = -1.0 * (np.pi - phi)
        elif phi < -1 * np.pi / 2:
            theta = -1.0 * theta
            phi = -1.0 * (-1 * np.pi - phi)

        return np.degrees(theta), np.degrees(phi)

    def calc_chi_phi_outgoing(self, target):
        pf = np.array(target[3:])
        a4 = np.radians(self._attached_a4.read(0))
        kfv = to_k(self._attached_ana.read(0), 'meV')
        kf = np.array([kfv*np.cos(a4), kfv*np.sin(a4), 0])
        q = self.calc_q_vector()
        angle_kfq = self.angle(kf, q)

        # Calculate sign
        kfcross = np.cross(kf, q)
        if kfcross[2] < 0:
            angle_kfq *= -1

        theta = self.angle(pf, np.array([0., 0., 1.]))
        pfp = np.array([pf[0], pf[1], 0.])
        if np.sqrt(pfp.dot(pfp)) != 0:
            phi = self.angle(pfp, np.array([1., 0., 0.]))
        else:
            phi = 0
        pfpcross = np.cross(np.array([1., 0., 0.]), pfp)
        if pfpcross[2] < 0:
            phi *= -1

        if np.abs(theta) < .01 or np.abs(theta - np.pi) < .01:
            phi = 0
        else:
            phi = -1. * (angle_kfq + phi)
        theta *= -1.

        # Corrections to reduce current in coils
        if phi > np.pi / 2:
            theta = -1.0 * theta
            phi = -1.0 * (np.pi - phi)
        elif phi < -1 * np.pi / 2:
            theta = -1.0 * theta
            phi = -1.0 * (-1 * np.pi - phi)

        return np.degrees(theta), np.degrees(phi)

    def calc_currents(self, target):
        # import pdb; pdb.set_trace()
        chi, phi = self.calc_chi_phi_incoming(target)
        ki = to_k(self._attached_mono.read(0), 'meV')
        i1 = (ki/self.w1)*np.radians(chi) - self.p1
        i2 = (ki/self.w2)*np.radians(phi) - self.p2
        chi, phi = self.calc_chi_phi_outgoing(target)
        kf = to_k(self._attached_ana.read(0), 'meV')
        i3 = (kf/self.w3)*np.radians(phi) - self.p3
        i4 = (kf/self.w4)*np.radians(chi) - self.p4
        return [i1, i2, i3, i4]

    def _getWaiters(self):
        return [
            self._attached_i1,
            self._attached_i2,
            self._attached_i3,
            self._attached_i4,
        ]

    def doStart(self, target):
        currents = self.calc_currents(target)
        magnets = self._getWaiters()
        for mag, cur in zip(magnets, currents):
            mag.start(cur)
        self.last_currents = currents

    def doRead(self, maxage=0):
        # There is no documented way to calculate the values back
        # from the currents. The only thing we can do is to compare the
        # currents we last set with the ones at which the magnets are now
        # and either complain bitterly or return the last target.
        for mag, cur in zip(self._getWaiters(), self.last_currents):
            if not mag.isAtTarget(target=cur):
                self.log.warning('Magnet current mismatch: should %f, is %f',
                                 cur, mag.read(maxage))
                return (-99, ) * 6
        return self.target


class MuSwitch(TransformedMoveable):
    """
    Translates between the x, y ,z syntax and mupad
    """

    hardware_access = False

    valuetype = tupleof(oneof('X', '-X', 'Y', '-Y', 'Z', '-Z'),
                        oneof('X', '-X', 'Y', '-Y', 'Z', '-Z'))

    attached_devices = {
        'mupad': Attach('Actual mupad device',
                        Mupad)
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    mapping = {
        'X': [1., 0, 0],
        '-X': [-1., 0, 0],
        'Y': [0, 1., 0],
        '-Y': [0, -1, 0],
        'Z': [0, 0, 1.],
        '-Z': [0, 0, -1.],
        'N': [-99, -99, -99]
    }

    def _mapTargetValue(self, target):
        return tuple(self.mapping[target[0]] + self.mapping[target[1]])

    def _startRaw(self, target):
        return self._attached_mupad.start(target)

    def doStatus(self, maxage=0):
        return self._attached_mupad.status(maxage)

    def _readRaw(self, maxage=0):
        return self._attached_mupad.read(maxage)

    def _findVector(self, v):
        for key, val in self.mapping.items():
            if val == v:
                return key

    def _mapReadValue(self, value):
        v1 = self._findVector(list(value[:3]))
        v2 = self._findVector(list(value[3:]))
        return v1, v2


class MuNumSwitch(MuSwitch):

    valuetype = tupleof(oneof(1, 2, 3, -1, -2, -3),
                        oneof(1, 2, 3, -1, -2, -3))

    mapping = {
        1: [1., 0, 0],
        -1: [-1., 0, 0],
        2: [0, 1., 0],
        -2: [0, -1, 0],
        3: [0, 0, 1.],
        -3: [0, 0, -1.],
        -9: [-99, -99, -99]
    }
