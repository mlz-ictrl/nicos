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

from math import radians, tan


def xA(alpha, gamma, lsa, lsd, y, xp, nv):
    """Calculate position where the beam hits the analyzer crystal.

    :param alpha: the divergence angle of the neutron
    :param gamma: the tilt angle of the deflector
    :param lsa: the sample-analyzer distance
    :param lsd: the sample deflector distance
    :param y: the translation of the analyser crystal
    :param xp: the point at the sample where the neutron is scattered
    :param nv: neutron path: transmitted(0), reflected at the first deflector(1),
          reflected at the second deflector(2),
    """
    if nv == 0:
        return xp + (lsa - y) * tan(radians(alpha))
    return xp + lsd * tan(radians(alpha)) + \
        (lsa - lsd - y) * tan(radians(2 * gamma - alpha))
