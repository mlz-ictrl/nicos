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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
'''
Gmatrix

store position as goniometer matrix
'''
from nicos.devices.sxtal.goniometer.base import PositionBase, PositionFactory

import numpy as np
from nicos.devices.sxtal.goniometer.posutils import Xrot, Yrot, Zrot


class GMatrix(PositionBase):
    ptype = 'g'
    theta_clockwise = 1

    def __init__(self, p=None, matrix=None, theta=None, _rad=False):
        """ Constructor. Part of Position subclass protocol.
        """
        PositionBase.__init__(self)
        if p:
            self.theta = p.theta
            self.matrix = p.matrix
        else:
            if theta is not None and not _rad:
                theta = np.deg2rad(theta)
            self.theta = theta
            self.matrix = matrix

    def asE(self, zeromega=0):
        """ Conversion. Part of Position subclass protocol.
        """
        # The goniometermatrix from the eulerian angles=
        # Zrot(omega)*Xrot(chi)*Zrot(phi)
        # So, with a=cos(phi)
        #     b=sin(phi)
        #     c=cos(chi)
        #     d=sin(chi)
        #     e=cos(omega)
        #     f=sin(omega)
        # The goniometermatrix matrix[0..2][0..2] is:
        #   ( a -b  0 )   ( 1  0  0 )   ( e -f  0 )
        #   ( b  a  0 ) * ( 0  c -d ) * ( f  e  0 )
        #   ( 0  0  1 )   ( 0  d  c )   ( 0  0  1 )
        # or:
        #   ( a -b  0 )   ( e   -f  0 )
        #   ( b  a  0 ) * ( fc  ec -d )
        #   ( 0  0  1 )   ( fd  ed  c )
        # or:
        #   ( ae-bfc  -fa-bec   bd )
        #   ( be+afc  -fb+aec  -ad )
        #   (  fd        ed      c )
        # or:
        coschi = self.matrix[2, 2]
        # Assume chi positive.
        try:
            sinchi = np.sqrt(1 - coschi ** 2)
        except ValueError:
            sinchi = 0.0
        chi = np.arctan2(sinchi, coschi)
        if abs(sinchi) < 1.0e-10:
            # Choose omega to be 180 degrees (easily accessible)
            sinomega = 0.0
            if zeromega:
                cosomega = 1.0
            else:
                cosomega = -1.0
        else:
            sinomega = self.matrix[0, 2] / sinchi
            cosomega = self.matrix[1, 2] / sinchi
        omega = np.arctan2(sinomega, cosomega)
        if abs(sinchi) < 1.0e-10:
            # Since f==0 and e==-1, the solution is simple....
            sinphi = self.matrix[1, 0]
            cosphi = -self.matrix[0, 0]
        else:
            sinphi = self.matrix[2, 0] / sinchi
            cosphi = -self.matrix[2, 1] / sinchi
        phi = np.arctan2(sinphi, cosphi)
        return PositionFactory(ptype='er',
                               theta=self.theta,
                               omega=omega,
                               phi=phi,
                               chi=chi)

    def asC(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asC()

    def asK(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asK()

    def asB(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asB()

    def asG(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.With()

    def asN(self, _wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asN()

    def asL(self, wavelength=None):
        """ Conversion. Part of Position subclass protocol.
        """
        return self.asE().asL(wavelength)

    def Xrot(self, angle):
        """ Rotate 'angle' (clockwise) around the X axis.
        """
        return self.With(matrix=np.dot(Xrot(angle), self.matrix))

    def Yrot(self, angle):
        """ Rotate 'angle' (clockwise) around the Y axis.
        """
        return self.With(matrix=np.dot(Yrot(angle), self.matrix))

    def Zrot(self, angle):
        """ Rotate 'angle' (clockwise) around the Z axis.
        """
        return self.With(matrix=np.dot(Zrot(angle), self.matrix))

    def With(self, **kw):
        """ Make clone of this position with some angle(s) changed.
        """
        if not kw.get('_rad', False):
            if kw.get('theta', None):
                kw['theta'] = np.deg2rad(kw['theta'])
        return PositionFactory(ptype='gr',
                               theta=kw.get('theta', self.theta),
                               matrix=kw.get('matrix', self.matrix))

    def __repr__(self):
        """ Representation. Part of Position subclass protocol.
        """
        if self.theta is not None:
            theta = "%8.3f" % (np.rad2deg(self.theta))
        else:
            theta = "None"
        return "[Goniometermatrix: theta=%s matrix=%s]" % (theta, repr(self.matrix))
