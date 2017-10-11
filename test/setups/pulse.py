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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

name = 'test_pulse setup'

devices = dict(
    sw = device('test.test_simple.test_pulse.PulseSwitch',
        states = ['up', 'down'],
    ),
    # well configured
    pulse1 = device('nicos.devices.generic.Pulse',
        onvalue = 'up',
        offvalue = 'down',
        ontime = 0.01,
        moveable = 'sw',
    ),
    # onvalue wrong
    pulse2 = device('nicos.devices.generic.Pulse',
        onvalue = 'UP',
        offvalue = 'down',
        ontime = 0.01,
        moveable = 'sw',
    ),
    # offvalue wrong
    pulse3 = device('nicos.devices.generic.Pulse',
        onvalue = 'up',
        offvalue = 'DOWN',
        ontime = 0.01,
        moveable = 'sw',
    ),
)
