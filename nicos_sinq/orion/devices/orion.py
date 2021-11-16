#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import numpy as np

from nicos_sinq.sxtal.instrument import EulerSXTal
from nicos_sinq.sxtal.singlexlib import rotatePsi, z1ToBisecting


class OrionSXTal(EulerSXTal):
    """
    This is a special version of the bisecting calculation for ORION.
    The need arises from the wish to use the same UB on ZEBRA as on
    ORION and MORPHEUS. Such that you can determine a UB on ORION and use
    it on ZEBRA. Problem is at ORION and MORPHEUS the crystal is sticking
    up but on ZEBRA it is hanging down. This class corrects for this.
    """
    def _orionChiPhi(self, chi, phi):
        chi = -1. * (chi + np.pi) + 2. * np.pi
        phi = phi + np.pi
        if phi > 1.99*np.pi:
            phi -= 2.*np.pi
        if phi < 0:
            phi += 2.*np.pi
        return chi, phi

    def _extractPos(self, pos):
        om, chi, phi = z1ToBisecting(self._attached_mono.read(0),
                                     pos)
        chi, phi = self._orionChiPhi(chi, phi)

        tth = 2. * om
        poslist = [
            ('ttheta', np.rad2deg(tth)),
            ('omega', np.rad2deg(om)),
            ('chi', np.rad2deg(chi)),
            ('phi', np.rad2deg(phi)),
        ]
        ok, _ = self._checkPosList(poslist)
        if not ok and self._attached_ttheta.isAllowed(np.rad2deg(tth)):
            for psi in range(0, 360, 10):
                ompsi, chipsi, phipsi = rotatePsi(om, chi, phi,
                                                  np.deg2rad(psi))
                chipsi, phipsi = self._orionChiPhi(chipsi, phipsi)
                psilist = [
                  ('ttheta', np.rad2deg(tth)),
                  ('omega', np.rad2deg(ompsi)),
                  ('chi', np.rad2deg(chipsi)),
                  ('phi', np.rad2deg(phipsi)),
                ]
                psiok, _ = self._checkPosList(psilist)
                if psiok:
                    poslist = psilist
                    break
        return poslist
