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
#   Nikhil Biyani <Nikhil.Biyani@psi.ch>
#
# *****************************************************************************

"""Utilities for SINQ tests."""

from nicos.core.device import Readable

unit_correction = {
    'degree': 1.50,
    'mm': 40,
    'a': 1,  # Ampere
}


def unit_value(unitless_value, units):
    """
    Converts the provided unitless value to value with units
    """
    if units.lower() in unit_correction:
        return unitless_value * unit_correction[units.lower()]

    print('Units unknown: ' + units)
    return unitless_value


def is_at_target(device, target):
    """
    Checks if the device has reached it's target position
    """
    if not isinstance(device, Readable):
        return False

    precision = device.precision if device.precision > 0.0 else 0.001
    return abs(device.read(0) - target) < precision
