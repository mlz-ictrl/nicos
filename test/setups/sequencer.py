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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

name = 'test_sequencer setup'

includes = ['stdsystem', 'multiswitch']

devices = dict(
    sm1 = device('devices.generic.VirtualMotor',
        abslimits = (0, 10),
        unit = 'V',
    ),
    sm2 = device('devices.generic.VirtualMotor',
        abslimits = (0, 10),
        unit = '',
    ),
    sm3 = device('devices.generic.VirtualMotor',
        abslimits = (0, 10),
        unit = '',
    ),
    ld = device('devices.generic.sequence.LockedDevice',
        device = 'sm1',
        lock = 'sm2',
        lockvalue = 10,
        unlockvalue = 0,
        keepfixed = True,
    ),
    ld2 = device('devices.generic.sequence.LockedDevice',
        device = 'sc1',
        lock = 'sm2',
        lockvalue = 10,
        unlockvalue = 0,
        keepfixed = True,
    ),
)
