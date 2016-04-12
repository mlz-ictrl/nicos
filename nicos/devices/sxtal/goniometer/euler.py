#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
Euler

class for stroing clockwise eulerian angles

'''

from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory

import numpy as np
from nicos import session
from nicos.core import NicosError
from nicos.devices.sxtal.goniometer.posutils import normalangle, Xrot, Zrot


class Euler(PositionBase):
    ptype = 'e'
    theta_clockwise = 1
    phi_clockwise = 1
    omega_clockwise = 1

    def __init__(self, p=None, theta=None, omega=None, chi=None, phi=None, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """
        PositionBase.__init__(self)
        if p:
            self.theta = p.theta
            self.omega = p.omega
            self.chi = p.chi
            self.phi = p.phi
        else:
            self.theta = self._r2d(theta, _rad)
            self.omega = self._r2d(omega, _rad)
            self.chi = self._r2d(chi, _rad)
            self.phi = self._r2d(phi, _rad)

    def asB(self):
        """ Conversion. Part of Position subclass protocol.
        """
        sineps = np.sin(self.omega - self.theta)
        coseps = np.cos(self.omega - self.theta)
        if coseps < 0:
            signcb = -1.0
        else:
            signcb = 1.0
        coschi = np.cos(self.chi)
        sinchi = np.sin(self.chi)
        if self.theta < 0:
            signth = -1.0
        else:
            signth = 1.0
        sinchib = coseps * sinchi
        coschib = signcb * np.sqrt(coschi ** 2 + (sinchi * sineps) ** 2)
        chib = np.arctan2(sinchib, coschib)
        if sineps == 0 and coschi == 0:
            phib = 0
            sinpsi = -signcb * np.sin(self.phi) * sinchi
            cospsi = signth * signcb * np.cos(self.phi) * coseps
        else:
            sinphi = -signcb * sineps
            cosphi = signcb * coseps * coschi
            phib = self.phi - np.arctan2(sinphi, cosphi)
            sinpsi = sinchi * sineps
            cospsi = signth * coschi
        psi = np.arctan2(sinpsi, cospsi)
        return PositionFactory(ptype='br',
            theta=self.theta,
            phi=normalangle(phib),
            chi=normalangle(chib),
            psi=normalangle(psi))

    def asC(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asB().asC()

    def asK(self):
        """ Conversion. Part of Position subclass protocol.
        """
        if not hasattr(self, 'alpha'):
            self.alpha = np.deg2rad(60)  # TODO: get from experiment?
            self.kappamax = np.rad2deg(180)

        si = np.sin(0.5 * self.chi)
        co = np.sin(self.alpha) ** 2 - si ** 2
        con3 = np.cos(self.kappamax / 2.0) ** 2 * np.sin(self.alpha) ** 2
        if con3 > co:
            session.log.warn("Chi can not be reached on this hardware")
            kappa = np.deg2rad(180.0)
            omega = np.deg2rad(90.0)
            # raise error("Chi high")
            co = con3
            co = np.sqrt(co)
            kappa = 2.0 * np.arctan2(si, co)
            si = si * np.cos(self.alpha)
            omega = np.arctan2(si, co)
        else:
            co = np.sqrt(co)
            kappa = 2.0 * np.arctan2(si, co)
            si = si * np.cos(self.alpha)
            omega = np.arctan2(si, co)
        phi = self.phi - omega
        omega = -omega + self.omega
        return PositionFactory(ptype='kr',
            theta=self.theta,
            omega=normalangle(omega),
            kappa=normalangle(kappa),
            phi=normalangle(phi))

    def asE(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asG(self):
        """ Conversion. Part of Position subclass protocol.
        """
        # print >> sys.stderr, self
        return PositionFactory(
            ptype='gr',
            theta=self.theta,
            matrix=np.dot(Zrot(self.omega),
                          np.dot(Xrot(self.chi), Zrot(self.phi))))

    def asN(self):
        """ Conversion. Part of Position subclass protocol.
        """
        if self.phi is not None:
            ph = normalangle(self.phi - np.deg2rad(90))
        else:
            ph = None
        if self.omega is not None:
            om = np.deg2rad(180) - self.omega
        else:
            om = None
        if self.theta is not None:
            th = -self.theta
        else:
            th = None
        return PositionFactory(ptype='nr',
                               theta=th,
                               chi=self.chi,
                               phi=ph,
                               omega=om)

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            for var in ('theta', 'phi', 'chi', 'omega'):
                if kw.get(var, None) is not None:
                    kw[var] = np.deg2rad(kw[var])
        return PositionFactory(ptype='er',
                               theta=kw.get('theta', self.theta),
                               omega=kw.get('omega', self.omega),
                               chi=kw.get('chi', self.chi),
                               phi=kw.get('phi', self.phi))

    def towards(self, other, fraction):
        if not other.ptype == self.ptype:
            raise NicosError('cannot interpolate between different typed positions')
        f0 = 1.0 - fraction
        f1 = fraction
        return self.With(theta=self.theta * f0 + other.theta * f1,
                         omega=self.omega * f0 + other.omega * f1,
                         chi=self.chi * f0 + other.chi * f1,
                         phi=self.phi * f0 + other.phi * f1)

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        s = "[Eulerian angles:"
        if self.theta is not None:
            s = s + " theta=%8.3f" % (np.rad2deg(self.theta))
        if self.phi is not None:
            s = s + " phi=%8.3f" % (np.rad2deg(self.phi))
        if self.omega is not None:
            s = s + " omega=%8.3f" % (np.rad2deg(self.omega))
        if self.chi is not None:
            s = s + " chi=%8.3f" % (np.rad2deg(self.chi))
        s = s + "]"
        return s
