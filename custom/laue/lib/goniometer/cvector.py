#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2015 by the NICOS contributors (see AUTHORS)
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
cvector

store a position as realspace diffraction vector.

see the `Unitcell` class for conversion to reciprocal space

'''
from .base import PositionBase, PositionFactory

import numpy as np
from nicos import session
from nicos.core import NicosError
from .posutils import normalangle


class CVector(PositionBase):
    ptype = 'c'
    theta_clockwise = 1

    def __init__(self, p=None, c=None, psi=None, signtheta=1, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """

        PositionBase.__init__(self)
        self.wavelength = session.experiment.wavelength
        if p:
            self.c = (p.c[0], p.c[1], p.c[2])
            self.psi = p.psi
            self.signtheta = p.signtheta
        else:
            self.c = (c[0], c[1], c[2])
            if psi is None:
                self.psi = 0.0
            else:
                if not _rad:
                    psi = np.deg2rad(psi)
                self.psi = psi
            self.signtheta = signtheta

    def asB(self):
        if not self.wavelength:
            raise NicosError("Cannot perform conversion without knowing wavelength")
        cosx = np.sqrt(self.c[0] ** 2 + self.c[1] ** 2)
        chi = np.arctan2(self.c[2], cosx)
        if cosx < 1.0E-6:
            phi = 0.0
        else:
            try:
                phi = np.arctan2(-self.c[0], self.c[1])
            except ValueError:
                print "Oops: ", self
                phi = 0
        sinx = np.sqrt(cosx ** 2 + self.c[2] ** 2) * self.wavelength / 2.0
        if sinx >= 1.0:
            theta = self.signtheta * np.pi / 2.0
        else:
            theta = self.signtheta * np.arcsin(sinx)
        if self.signtheta < 0:
            phi = phi + np.deg2rad(180)
            chi = -chi
        return PositionFactory(ptype='br',
                               theta=normalangle(theta),
                               phi=normalangle(phi),
                               chi=normalangle(chi),
                               psi=self.psi)

    def asE(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asB().asE()

    def asK(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asK()

    def asC(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asG(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asG()

    def asN(self):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asN()

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            if kw.get('psi', None):
                kw['psi'] = np.deg2rad(kw['psi'])
        return PositionFactory(ptype='cr',
                               c=kw.get('c', self.c),
                               signtheta=kw.get('signtheta', self.signtheta),
                               psi=kw.get('psi', self.psi))

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        if self.psi is not None:
            psi = "%8.3f" % (np.rad2deg(self.psi))
        else:
            psi = "None"
        return "[C-vector: c=%s psi=%s]" % (repr(self.c), psi)
