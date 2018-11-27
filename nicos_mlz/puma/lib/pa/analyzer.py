# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from math import radians, sin

from .gauss import gaussian
from .xa import xA


def anaeff(theta0, theta, gamma, alpha, lsa, lsd, x, y, xp, eta, b, r, nv):
    """Calculate analyzer efficiency.

    :param theta0: the nominal analyzer angle (negativ!)
    :param theta: is the analyzer tilt angle
    :param eta: the mosaicity in deg
    :param gamma: the deflector tilt angle
    :param alpha: the divergence angle
    :param lsa: the nominal sample-analyzer distance
    :param lsd: the sample deflector diatance
    :param x: x coordinate for the analyzer center
    :param y: y coordinate for the analyzer center
    :param xp: the scattering position at the sample
    :param b: the width of an analyzer blade in cm
    :param r: the reflectivity
    :param nv: neutron type: 0 - transmitted, 1 - reflected at deflector
    """
    a = 1.
    xn = xA(alpha, gamma, lsa, lsd, y, xp, nv)
    dx = b * sin(radians(theta0))
    ang = theta - theta0
    if nv:
        ang = 2 * gamma - ang
    return gaussian(1, ang, eta, alpha) * gaussian(a, x, dx, xn)
