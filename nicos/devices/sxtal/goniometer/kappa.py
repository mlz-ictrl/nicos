#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   pedersen
#
# *****************************************************************************
'''
Kappa

a class for storing kappa positions

All angle move clockwise for positive values.

to allow conversions, the kappa-angle alpha needs to be known
'''

from __future__ import print_function

from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory

import numpy as np
from nicos.core import NicosError
from nicos.devices.sxtal.goniometer.posutils import normalangle, Yrot, Zrot


class Kappa(PositionBase):
    ptype = 'k'
    theta_clockwise = 1
    phi_clockwise = 1
    omega_clockwise = 1

    def __init__(self, p=None, theta=None, omega=None, kappa=None, phi=None, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """
        PositionBase.__init__(self)
        self.alpha = np.deg2rad(60)  # TODO: get from experiment?
        if p:
            self.theta = p.theta
            self.omega = p.omega
            self.kappa = p.kappa
            self.phi = normalangle(p.phi)
        else:
            self.theta = self._r2d(theta, _rad)
            self.omega = self._r2d(omega, _rad)
            self.kappa = self._r2d(kappa, _rad)
            self.phi = self._r2d(phi, _rad)

    def Alternate(self):
        """ The alternate Kappa position that has the same orientation.
        """
        return self.asE().Alternate().asK()

    def NegateTheta(self):
        """ The same position with negative theta.

            Keep the same reflection active in the center of the detector.
        """
        return self.With(theta=-self.theta, omega=self.omega + np.rad2deg(180) - 2 * self.theta)

    def asG(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return PositionFactory(
            ptype='gr',
            theta=self.theta,
            matrix=np.dot(Zrot(self.omega),
                          np.dot(Yrot(-self.alpha),
                                 np.dot(Zrot(self.kappa),
                                        np.dot(Yrot(self.alpha), Zrot(self.phi))))))

    def asE(self):
        """ Conversion. Part of Position subclass protocol.
        """
        if self.kappa is None:
            print("DBG> Convert incomplete kappa to eulerian!")
            return PositionFactory(ptype='e',
                                   theta=self.theta)
        halfkappa = 0.5 * self.kappa
        # Modulo 360
        while halfkappa > np.pi / 2:
            halfkappa -= np.pi
        while halfkappa < -np.pi / 2:
            halfkappa += np.pi
        sinx = np.cos(self.alpha) * np.sin(halfkappa)
        cosx = np.cos(halfkappa)
        x = np.arctan2(sinx, cosx)
        omegae = self.omega + x
        phie = self.phi + x
        sinc = np.sin(self.alpha) * np.sin(halfkappa)
        chie = 2.0 * np.arcsin(sinc)
        return PositionFactory(ptype='er',
                               theta=self.theta,
                               omega=normalangle(omegae),
                               chi=normalangle(chie),
                               phi=normalangle(phie))

    def asB(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asB()

    def asC(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asB().asC()

    def asK(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asN(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asN()

    def asL(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asL()

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            for var in ('theta', 'phi', 'kappa', 'omega'):
                if kw.get(var, None) is not None:
                    kw[var] = np.deg2rad(kw[var])
        return PositionFactory(ptype='kr',
                               theta=kw.get('theta', self.theta),
                               omega=kw.get('omega', self.omega),
                               kappa=kw.get('kappa', self.kappa),
                               phi=kw.get('phi', self.phi))

    def towards(self, other, fraction):
        if not other.ptype == self.ptype:
            raise NicosError('cannot interpolate between different ptyped positions')
        f0 = 1.0 - fraction
        f1 = fraction
        kw = {}
        if self.theta is not None and other.theta is not None:
            kw['theta'] = self.theta * f0 + other.theta * f1
        if self.omega is not None and other.omega is not None:
            kw['omega'] = self.omega * f0 + other.omega * f1
        if self.phi is not None and other.phi is not None:
            kw['phi'] = self.phi * f0 + other.phi * f1
        if self.kappa is not None and other.kappa is not None:
            kw['kappa'] = self.kappa * f0 + other.kappa * f1
        return self.With(**kw)

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        s = "[Kappa angles:"
        if self.theta is not None:
            s = s + " theta=%8.3f" % (np.rad2deg(self.theta))
        if self.phi is not None:
            s = s + " phi=%8.3f" % (np.rad2deg(self.phi))
        if self.omega is not None:
            s = s + " omega=%8.3f" % (np.rad2deg(self.omega))
        if self.kappa is not None:
            s = s + " kappa=%8.3f" % (np.rad2deg(self.kappa))
        s = s + "]"
        return s
