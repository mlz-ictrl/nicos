#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Custom TAS instrument class for MIRA."""

from nicos.devices.tas.spectro import TAS


class MIRA(TAS):

    def _getResolutionParameters(self):
        return [
            1,    # circular (0) or rectangular (1) source
            6.0,  # width of source / diameter (cm)
            12.0, # height of source / diameter (cm)
            1,    # no guide (0) or guide (1)
            7.2,  # horizontal guide divergence (min/AA)
            12.0, # vertical guide divergence (min/AA)

            0,    # cylindrical (0) or cuboid (1) sample
            2.0,  # sample width / diameter perp. to Q (cm)
            2.0,  # sample width / diameter along Q (cm)
            4.0,  # sample height (cm)

            1,    # circular (0) or rectangular (1) detector
            1.5,  # width / diameter of the detector (cm)
            8.0,  # height / diameter of the detector (cm)

            0.15, # thickness of monochromator (cm)
            11.7, # width of monochromator (cm)
            7.5,  # height of monochromator (cm)

            0.3,  # thickness of analyzer (cm)
            12.0, # width of analyzer (cm)
            8.0,  # height of analyzer (cm)

            10,   # distance source - monochromator (cm)
            200,  # distance monochromator - sample (cm)
            116,  # distance sample - analyzer (cm)
            35,   # distance analyzer - detector (cm)

            # automatically calculated from focmode and ki if they are zero
            0,    # horizontal curvature of monochromator (1/cm)
            0,    # vertical curvature of monochromator (1/cm)
            0,    # horizontal curvature of analyzer (1/cm)
            0,    # vertical curvature of analyzer (1/cm)

            30,   # distance monochromator - monitor (cm)
            6.0,  # width of monitor (cm)
            12.0, # height of monitor (cm)
        ]
