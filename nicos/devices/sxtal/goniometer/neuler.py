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

"""
NEuler

store eulerian coordinates with all angles except phi counterclockwise.

"""
from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory

import numpy as np
from nicos.core import NicosError
from nicos.devices.sxtal.goniometer.posutils import normalangle


class NEuler(PositionBase):
    """ Counter-clockwise rotating eulerian goniostat, phi clockwise!
    """
    ptype = 'n'
    theta_clockwise = 0
    phi_clockwise = 1
    omega_clockwise = 0

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
        return self.asE().asB()

    def asC(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asC()

    def asK(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asK()

    def asE(self):
        """ Conversion. Part of Position subclass protocol.
        """
        if self.omega is not None:
            om = np.deg2rad(180) - self.omega
        else:
            om = None
        if self.phi is not None:
            ph = normalangle(self.phi + np.deg2rad(90))
        else:
            ph = None
        if self.theta is not None:
            th = -self.theta
        else:
            th = None
        return PositionFactory(ptype='er',
                               theta=th,
                               chi=self.chi,
                               phi=ph,
                               omega=om)

    def asN(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asG(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asG()

    def asL(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asL()

    def Alternate(self):
        """ The alternate N-position that has the same orientation.
        """
        return PositionFactory(ptype='nr',
                               omega=normalangle(self.omega + np.pi),
                               theta=self.theta,
                               chi=-self.chi,
                               phi=normalangle(self.phi + np.pi))

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            for var in ('theta', 'phi', 'chi', 'omega'):
                if kw.get(var, None) is not None:
                    kw[var] = np.deg2rad(kw[var])
        return PositionFactory(ptype='nr',
                               theta=kw.get('theta', self.theta),
                               omega=kw.get('omega', self.omega),
                               chi=kw.get('chi', self.chi),
                               phi=kw.get('phi', self.phi))

    def towards(self, other, fraction):
        if not other.ptype == self.ptype:
            raise NicosError('cannot interpolate between different ptyped positions')
        f0 = 1.0 - fraction
        f1 = fraction
        return self.With(_rad=True,
            theta=self.theta * f0 + other.theta * f1,
            omega=self.omega * f0 + other.omega * f1,
            chi=self.chi * f0 + other.chi * f1,
            phi=self.phi * f0 + other.phi * f1)

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        s = "[Counterclockwise Eulerian angles:"
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
