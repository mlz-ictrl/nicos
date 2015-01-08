# -*- coding: utf-8 -*-
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************


# local library
from nicos.devices.generic.slit import Slit


__author__ = "Christian Felder <c.felder@fz-juelich.de>"


class PosOpeningSlit(Slit):
    """A rectangular slit consisting of four blades.

    Use a coordinate system which is centered and closed at zero.
    Driving in positive direction means opening the slits for each axes.

    """

    def _isAllowedSlitOpening(self, positions):
        ok, why = True, ''
        if positions[1] + positions[0] < 0:
            ok, why = False, 'horizontal slit opening is negative'
        elif positions[3] + positions[2] < 0:
            ok, why = False, 'vertical slit opening is negative'
        return ok, why
