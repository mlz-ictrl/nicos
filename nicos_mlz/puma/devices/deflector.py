#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Deflector device."""

from nicos.core.params import Override, Param, floatrange
from nicos.devices.generic import Axis


class Deflector(Axis):
    """Special axis to store additional parameters for the deflectors."""

    parameters = {
        'reflectivity': Param('Reflectivity of the material',
                              type=floatrange(0, 1), settable=False,
                              userparam=False, default=0.9),
        'length': Param('Length of the deflector blades',
                        type=floatrange(0, None), settable=False,
                        prefercache=False, default=40., unit='mm'),
        'thickness': Param('Thickness of the wafer',
                           type=floatrange(0, None), settable=False,
                           userparam=False, default=0.55, unit='mm'),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='deg'),
    }
