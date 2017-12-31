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
#   Tobias Unruh <tobias.unruh@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF safety system readout descriptions."""


bit_description = [
    "door of chopper shielded area is closed (switch 1)",                       # bit 1-0
    "door of chopper shielded area is closed (switch 2)",                       # bit 1-1
    "search procedure of chopper shielded area is active",                      # bit 1-2
    "search procedure of chopper shielded area is not active (not used)",       # bit 1-3
    "emergency stop not pressed (in chopper shielded area)",                    # bit 1-4
    "search button 1 pressed (chopper shielded area)",                          # bit 1-5
    "search button 2 pressed (chopper shielded area)",                          # bit 1-6
    "emergency stop not pressed (at sample chamber)",                           # bit 1-7
    "search button pressed (at sample chamber floor)",                          # bit 1-8
    "search button pressed (at sample chamber stage)",                          # bit 1-9
    "chopper speed 1 > 150 rpm",                                                # bit 1-10
    "chopper speed 2 > 150 rpm",                                                # bit 1-11
    "open shutter button pressed (control panel)",                              # bit 1-12
    "close shutter button pressed (control panel)",                             # bit 1-13
    "not used",                                                                 # bit 1-14
    "not used",                                                                 # bit 1-15

    "bypass of the switches of the sample chamber door active",                 # bit 2-0
    "bypass of the switches of the sample chamber door not active (not used)",  # bit 2-1
    "door of the sample chamber is opened (switch 1)",                          # bit 2-2
    "cover of the sample chamber is opened",                                    # bit 2-3
    "door of the sample chamber is opened (switch 2)",                          # bit 2-4
    "entry of experimental area \"floor\" is closed",                           # bit 2-5
    "entry of experimental area \"stage\" is closed",                           # bit 2-6
    "bypass of the whole safety system is active (not yet installed)",          # bit 2-7
    "bypass of the whole safety system is not active (not yet installed)",      # bit 2-8
    "shutter is opened (switch 1)",                                             # bit 2-9
    "shutter is closed (green light on)",                                       # bit 2-10
    "shutter is in error state (orange light on)",                              # bit 2-11
    "shutter is opened (red light on)",                                         # bit 2-12
    "warning light is flashing (in chopper shielded area, not yet installed)",  # bit 2-13
    "magnetic vent of shutter is powered to open shutter",                      # bit 2-14
    "not used",                                                                 # bit 2-15

    "shutter is opened (switch 2)",                                             # bit 3-0
    "shutter is closed (switch 1)",                                             # bit 3-1
    "shutter is closed (switch 2)",                                             # bit 3-2
    "emergency stop not pressed (control panel)",                               # bit 3-3
    "enable of shutter control (key switch, control panel)",                    # bit 3-4
    "disable of shutter control (key switch, control panel)",                   # bit 3-5
    "enable signal for instrument shutter (from NLA)",                          # bit 3-6
    "gamma detector alarm active",                                              # bit 3-7
    "gamma detector alarm inactive",                                            # bit 3-8
    "not used",                                                                 # bit 3-9
    "not used",                                                                 # bit 3-10
    "not used",                                                                 # bit 3-11
    "not used",                                                                 # bit 3-12
    "not used",                                                                 # bit 3-13
    "not used",                                                                 # bit 3-14
    "not used",                                                                 # bit 3-15
]
