# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Goetz Eckold <geckold@gwdg.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from math import degrees, tanh

from .gauss import gaussian

a0 = 1.
# all of the following parameters are just fit parameters to the reflectivy
# curve provided by the deflector vendor (SWISS NEUTRONICS)
xc = 0.  # critical angle
x0 = 1.05  # angle
b = 20.  # 1 / 0.05 with .05, where 0.05 is the 'm' value where the reflectivy
         # drops down rapidly
s = 0.3 / x0 / 3.5 * 4.5  # const from vendor of the deflector
dx = degrees(0.55 / 40)  # thickness of deflector wafers / deflector height


def rdefl(x, nv):
    """Calculate reflectivity curve of deflectors as function of grazing angle.

    :param x: effictive grazing angle of beam at deflector (in deg)
    :type x: ``float``
    :param nv: neutron spin: up(1), down(2)
    :type nv: ``1 or 2``

    :returns: reflectivity
    """
    ax = abs(x)

    if nv == 1:
        ret = (1. - tanh((ax - 0.15 * x0) * b)) / 2.
    else:
        ret = (1. - tanh((ax - x0) * b)) / 2.
        ret *= (1. + s * (x0 / 4.5 - ax))
    ret *= (1 - gaussian(a0, xc, dx, x))
    return ret


def ddefl(gamma, alpha, L, d, nv):
    """Calculate the propability of double reflection within deflector.

    :param gamma: the tilt angle of the deflector
    :param alpha: the divergence angle of the incident beam (w.r.t. optical axis)
    :param L: the length of the deflector
    :param d: the wafer thickness of the deflector
    :param nv: neutron spin: up(1), down(2)
    :type nv: ``1 or 2``
    """
    y = gamma - alpha if gamma > 0 else alpha - gamma
    div = degrees(d / L)
    if y <= div:
        return 0.
    rd = rdefl(y, nv)
    return max(0, (y / div - 1) * rd * rd)
