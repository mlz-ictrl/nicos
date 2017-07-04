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
Lifting

class for storing position using omega and lifting counter

'''

import numpy as np

from nicos import session
from nicos.core import NicosError
from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory


class Lifting(PositionBase):
    ptype = 'l'
    theta_clockwise = 1
    phi_clockwise = 1
    omega_clockwise = 1

    def __init__(self, p=None, gamma=None, omega=None, nu=None, signtheta=1,
                  psi=None, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """
        PositionBase.__init__(self)
        if p:
            self.gamma = p.gamma
            self.omega = p.omega
            self.nu = p.nu
            self.signtheta = p.signtheta
            self.psi = p.psi
        else:
            self.gamma = self._r2d(gamma, _rad)
            self.omega = self._r2d(omega, _rad)
            self.nu = self._r2d(nu, _rad)
            self.signtheta = signtheta
            self.psi = self._r2d(psi, _rad)

    def asB(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asB()

    def asC(self, wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        if wavelength is None:
            wavelength = session.instrument.wavelength or None
        if not wavelength:
            raise NicosError("Cannot perform conversion without knowing wavelength")
        cz = np.sin(self.nu) / wavelength
        theta = 0.5 * np.arccos(np.cos(self.gamma) * np.cos(self.nu))
        cabs2 = (2.0 / wavelength * np.sin(theta))**2
        cxy = np.sqrt(cabs2 - cz**2)
        delta = self.signtheta * np.arcsin(cabs2 / cxy * wavelength / 2.0)
        phi = -np.pi/2 + delta - self.omega
        cx = np.cos(phi) * cxy
        cy = np.sin(phi) * cxy
        return PositionFactory(ptype='cr', c=(cx, cy, cz),
                               signtheta=self.signtheta, psi=self.psi)

    def asK(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asK()

    def asE(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asE()

    def asG(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asG()

    def asN(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asC().asN()

    def asL(self, wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            for var in ('gamma', 'omega', 'nu', 'psi'):
                if kw.get(var, None) is not None:
                    kw[var] = np.deg2rad(kw[var])
        return PositionFactory(ptype='lr',
                               gamma=kw.get('gamma', self.gamma),
                               omega=kw.get('omega', self.omega),
                               nu=kw.get('nu', self.nu),
                               signtheta=kw.get('signtheta', self.signtheta),
                               psi=kw.get('psi', self.psi)
                               )

    def towards(self, other, fraction):
        if not other.ptype == self.ptype:
            raise NicosError('cannot interpolate between different typed positions')
        f0 = 1.0 - fraction
        f1 = fraction
        return self.With(gamma=self.gamma * f0 + other.gamma * f1,
                         omega=self.omega * f0 + other.omega * f1,
                         nu=self.nu * f0 + other.nu * f1)

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        s = "[Lifting:"
        if self.gamma is not None:
            s = s + " gamma=%8.3f" % (np.rad2deg(self.gamma))
        if self.omega is not None:
            s = s + " omega=%8.3f" % (np.rad2deg(self.omega))
        if self.nu is not None:
            s = s + " nu=%8.3f" % (np.rad2deg(self.nu))
        if self.psi is not None:
            s = s + " psi=%8.3f" % (np.rad2deg(self.psi))
        s = s + "]"
        return s
