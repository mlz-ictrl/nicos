# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

devices = dict(
    motor1 = device('nicos_sinq.test.devices.test_sinqmotor.FakeSinqMotor',
        unit = 'mm',
        motorpv = 'IOC:m1',
        userlim_follow_abslim = True,
    ),
    jogmove1 = device('nicos.devices.generic.paramdev.ParamDevice',
        description = 'Jogmove param device of motor1',
        device = 'motor1',
        parameter = 'velocity_move',
    ),
    motor2 = device('nicos_sinq.test.devices.test_sinqmotor.FakeSinqMotor',
        unit = 'mm',
        motorpv = 'IOC:m1',
        userlim_follow_abslim = False,
    ),
    jogmove2 = device('nicos.devices.generic.paramdev.ParamDevice',
        description = 'Jogmove param device of motor2',
        device = 'motor2',
        parameter = 'velocity_move',
    ),
)
