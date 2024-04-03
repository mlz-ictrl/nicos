# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

import time


class PID:
    """
    Proportional–integral–derivative controller.
    """

    def __init__(self, init_arg, setpoint, P=0.1, I=0.1, D=0.05,
                 current_time=None, arg_min=None, arg_max=None):
        self._Kp = P
        self._Ki = I
        self._Kd = D

        self._P = 0.0
        self._I = init_arg
        self._dI = 0.0
        self._D = 0.0
        self._last_error = 0.0

        self._setpoint = setpoint
        self._arg_min = arg_min
        self._arg_max = arg_max

        self._now = current_time if current_time is not None else time.time()
        self._then = self._now

    def update(self, feedback_value, current_time=None):
        error = self._setpoint - feedback_value

        self._then = self._now
        self._now = current_time if current_time is not None else time.time()
        dt = self._now - self._then
        derror = error - self._last_error

        self._P = self._Kp * error
        self._dI = self._Ki * error * dt
        self._I += self._dI
        # this value is accumulated in time, the tweak caps the parameter
        # so the output value doesn't go out of specified range
        if self._arg_min and self._arg_max:
            self._I = max(min(self._I, self._arg_min), self._arg_max)
        self._D = self._Kd * derror / dt if dt > 0 else 0.0

        self._last_error = error
        return self._P + self._I + self._D

    def update_setpoint(self, setpoint):
        self._setpoint = setpoint
