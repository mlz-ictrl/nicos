# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Param, limits
from nicos.core.constants import MASTER
from nicos.core.mixins import HasLimits
from nicos.core.params import Override


class DynamicUserlimits(HasLimits):

    parameters = {
        'userlim_follow_abslim': Param('Set userlimit behavior in case of '
                                       'changing absolute limits',
                                       default=False, settable=True, type=bool,
                                       userparam=True),
        'inputlimits': Param('Limits given from the user', unit='main',
                             type=limits, settable=True, userparam=False,
                             category='limits', fmtstr='main',
                             mandatory=False),
        'delta_limits': Param('Internal parameter = abslimits - userlimits',
                              type=limits, mandatory=False, settable=True,
                              userparam=False, default=(0.0, 0.0), internal=True),
    }

    parameters['userlim_follow_abslim'].ext_desc = """
    This flag controls the user limits behavior in case the absolute limits
    change over time. In the examples below, some tables are given where
    the absolute limits of the device are changed from within the hardware
    over time (the absolute limits of this device type are not user-settable),
    but read directly from the hardware.

    `userlim_follow_abslim = True`:
    User limits maintain a constant distance / delta to the absolut limits. The
    delta is calculated anew for each manual input of the user limit.

    ```
    Time (s)             |       0 |       1 |       2 |      3 |        4 |
    Absolute limits (mm) | [0, 10] | [2, 13] | [0, 10] | [3, 7] | [-8, -1] |
    User limits     (mm) | [1,  8] | [3, 11] | [1,  8] | [4, 5] | [-7, -3] |
    ```
    In this example, the user limits [1, 8] were given at t = 0 seconds. The
    delta to the low absolute limit is 1, the delta to the high absolute limit
    is 2. These deltas are maintained over time until new user limits (and
    therefore deltas) are given.

    `userlim_follow_abslim = False`:
    User limits shrink if they would be outside the absolute limits and re-
    expand to the original manual input again if possible.

    ```
    Time (s)             |       0 |       1 |       2 |      3 |        4 |
    Absolute limits (mm) | [0, 10] | [2, 13] | [0, 10] | [3, 7] | [-8, -1] |
    User limits     (mm) | [1,  8] | [2,  8] | [1,  8] | [3, 7] | [-1, -1] |
    ```
    In this example, the user limits are left at the given values [1, 8] if
    possible, but shrunken in order to fit within the absolute limits, if
    necessary.

    In case the absolute limits do not change over time, this flag does not
    change the behaviour of the userlimits at all.
    """

    parameter_overrides = {
        'userlimits': Override(volatile=True),
    }

    def doInit(self, mode):
        if mode == MASTER:
            # At NICOS startup, the deltas are calculated based on the current
            # values for absolute limits and the cached user limits
            self.delta_limits = (self.absmin - self.usermin, self.absmax - self.usermax)

            # At NICOS startup, inputlimits equal cached userlimits
            self.inputlimits = self.userlimits

    def _user_limits(self):
        # See description of parameter userlim_follow_abslim for an explanation
        # of the behaviour realized here
        if self.userlim_follow_abslim:
            (usermin, usermax) = HasLimits.doReadUserlimits(self)
            usermax = self.absmax - self.delta_limits[1]
            usermin = self.absmin - self.delta_limits[0]
            return (usermin, usermax)
        return self.inputlimits

    def doReadUserlimits(self):
        (usermin, usermax) = self._user_limits()

        # Adjust the limits so that the user limits are always within the
        # absolute limits and that they do not contradict each other.
        usermax = min(usermax, self.absmax)
        usermin = max(usermin, self.absmin)
        usermax = max(usermax, self.absmin)
        usermin = min(usermin, self.absmax)
        usermin = min(usermin, usermax)
        usermax = max(usermin, usermax)

        return (usermin, usermax)

    def doWriteUserlimits(self, value):

        # Check if the given limits are legal
        HasLimits.doWriteUserlimits(self, value)

        # Store the newly given limits
        self.inputlimits = value
        self.delta_limits = (self.absmin - value[0], self.absmax - value[1])
