#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2014 by the NICOS contributors (see AUTHORS)
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
Position base class and factory function

The position handling uses quite a lot of chaining to
keep maintenance effort low.
"""

import numpy as np


def PositionFactory(ptype, **kwds):
    """ Position factory function.

        parameters:

            **ptype** -- 'k' for kappa type,
                        'e' for Euler,
                        'n' for euler with counter-clock-wise motors except phi,
                        'g' for goniometermatrix,
                        'b' for bisecting,
                        'c' for C-vector,

                        a suffix 'r' may be used to signal angles in radians

        ptype specific parameters::

            if ptype='k': omega, kappa, phi, theta
            if ptype='e': omega, chi, phi, theta
            if ptype='n': omega, chi, phi, theta
            if ptype='b': theta, phi, chi, psi
            if ptype='c': c, psi, signtheta
            if ptype='g': theta, matrix


        matrix= 3x3-matrix, c= 3-vector, dx in mm, angles in radians.

        Alternatively, a position object 'p' can be passed, and a copy
        will be returned.

        a
    """
    p = kwds.get('p', None)
    radians = False
    if len(ptype) > 1 and ptype[1] == 'r':
        ptype = ptype[0]
        radians = True
    if p:
        return p.__class__(p)
    elif ptype in typelist:
        return typelist[ptype](_rad=radians, **kwds)
    else:
        raise TypeError("unknown ptype specified in PositionFactory()")


class PositionBase(object):
    def __init__(self):
        pass

    def _r2d(self, val, _rad):
        if not _rad:
            if val:
                return np.deg2rad(val)
        else:
            return val

from nicos.laue.goniometer.euler import Euler
from nicos.laue.goniometer.kappa import Kappa
from nicos.laue.goniometer.neuler import NEuler
from nicos.laue.goniometer.cvector import CVector
from nicos.laue.goniometer.gmatrix import GMatrix
from nicos.laue.goniometer.bisect import Bisecting

typelist = {'k': Kappa,
            'e': Euler,
            'b': Bisecting,
            'c': CVector,
            'g': GMatrix,
            'n': NEuler,
            }


