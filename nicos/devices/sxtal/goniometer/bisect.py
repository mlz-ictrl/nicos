#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Bisect

class for storing a bisecting position.
"""

from __future__ import print_function

from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory

import numpy as np
from nicos import session
from nicos.core import NicosError
from nicos.devices.sxtal.goniometer.posutils import normalangle, sign, Xrot, Yrot, Zrot


class Bisecting(PositionBase):
    ptype = 'b'

    def __init__(self, p=None, theta=None, phi=None, chi=None, psi=0, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """
        PositionBase.__init__(self)
        if p:
            self.theta = p.theta
            self.phi = p.phi
            self.chi = p.chi
            self.psi = p.psi
        else:
            self.theta = self._r2d(theta, _rad)
            self.omega = self._r2d(psi, _rad)
            self.chi = self._r2d(chi, _rad)
            self.phi = self._r2d(phi, _rad)
            self.psi = self._r2d( psi, _rad)

    def asC(self, wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        if wavelength is None:
            wavelength = session.instrument.wavelength or None
        if not wavelength:
            raise NicosError("Cannot perform conversion without knowing wavelength")
        if self.theta >= 0:
            signtheta = 1
        else:
            signtheta = -1
        d = 2 * np.sin(self.theta) / wavelength
        c = [-np.sin(self.phi) * np.cos(self.chi) * d,
             np.cos(self.phi) * np.cos(self.chi) * d,
             np.sin(self.chi) * d]
        return PositionFactory(ptype='cr', c=c, psi=self.psi, signtheta=signtheta)

    def asE(self):
        """ Conversion. Part of Position subclass protocol.
        """
        sinpsi = np.sin(self.psi)
        cospsi = np.cos(self.psi)
        signth = sign(np.sin(self.theta))
        sinchb = np.sin(self.chi)
        coschb = np.cos(self.chi)
        signcb = sign(coschb)
        sinche = signcb * sign(sinchb) * np.sqrt((cospsi * sinchb) ** 2 + sinpsi ** 2)
        cosche = signth * signcb * cospsi * coschb
        try:
            chi = np.arctan2(sinche, cosche)
        except ValueError:
            print("B-E Chi problem:", self)
            chi = 0.0
        if sinchb == 0 and sinpsi == 0:
            omega = self.theta - 90.0 * (signcb - 1.0)
            sinphe = -np.sin(omega - self.theta) * coschb
            cosphe = signth * signcb * np.cos(omega - self.theta) * cospsi
        else:
            signch = sign(np.sin(chi))
            sinome = signch * signcb * coschb * sinpsi
            cosome = signch * sinchb
            try:
                omega = np.arctan2(sinome, cosome) + self.theta
            except ValueError:
                print("Oops:", self)
                omega = 0.0
            sinphe = -signch * signcb * sinpsi
            cosphe = signch * signth * signcb * sinchb * cospsi
        try:
            phi = np.arctan2(sinphe, cosphe) + self.phi
        except ValueError:
            print("Oops:", self)
            phi = 0.0
        return PositionFactory(ptype='er',
                               theta=self.theta,
                               omega=normalangle(omega),
                               chi=normalangle(chi),
                               phi=normalangle(phi))

    def asG(self):
        """ Conversion. Part of Position subclass protocol.
        """
        if self.theta > 0:
            S = 0
        else:
            S = np.pi
        if np.cos(self.chi) > 0:
            C = 0
        else:
            C = np.pi
        return PositionFactory(
            ptype='gr',
            theta=self.theta,
            matrix=np.dot(Zrot(self.theta),
                          np.dot(Xrot(S),
                                 np.dot(Yrot(-self.psi),
                                        np.dot(Zrot(S + C),
                                               np.dot(Xrot(C),
                                                      np.dot(Xrot(self.chi),
                                                             Zrot(self.phi))))))))

    def asK(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asK()

    def asB(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asN(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asN()

    def asL(self):
        return self.asC().asL()

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            for var in ('theta', 'phi', 'chi', 'psi'):
                if kw.get(var, None) is not None:
                    kw[var] = np.deg2rad(kw[var])
        return PositionFactory(ptype='br',
                               theta=kw.get('theta', self.theta),
                               phi=kw.get('phi', self.phi),
                               chi=kw.get('chi', self.chi),
                               psi=kw.get('psi', self.psi))

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        s = "[Bisecting angles:"
        if self.theta is not None:
            s = s + " theta=%8.3f" % (np.rad2deg(self.theta))
        if self.phi is not None:
            s = s + " phi=%8.3f" % (np.rad2deg(self.phi))
        if self.chi is not None:
            s = s + " chi=%8.3f" % (np.rad2deg(self.chi))
        if self.psi is not None:
            s = s + " psi=%8.3f" % (np.rad2deg(self.psi))
        s = s + "]"
        return s
