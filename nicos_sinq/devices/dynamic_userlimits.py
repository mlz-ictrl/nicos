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

from nicos import session
from nicos.core import Param, limits, MASTER, POLLER, MAIN
from nicos.core.mixins import HasLimits, HasOffset


class DynamicUserlimits(HasLimits):
    '''
    Extension of `HasLimits` which automatically adjusts the `userlimits` if the
    `abslimits` change.

    This mixin is an enhanced version of `HasLimits` which provides the same
    basic functionality. On top of that, it automatically adapts the userlimits
    if the underlying absolute limits change. This is useful if the absolute
    limits of a device can change during runtime (e.g. if they are read out
    from the hardware) because this could lead to the userlimits being outside
    the absolute limits. Since NICOS assumes that the absolute limits are
    constant, this could lead to bugs.

    Two different operation modes are available which can be switched at runtime
    via the flag `userlim_follow_abslim`. If this flag is `True`, the userlimits
    maintain the same distance(s) to the absolute limits. If it is set to
    `False`, the user limits stay constant unless the absolute limits move
    inside the userlimits. If that happens, the user limits are shrunk
    accordingly. If the absolute limits expand again later, the user limits
    go back to their original values set by the user. Please see the extended
    description of the parameter `userlim_follow_abslim` for examples.

    If a device using this class also uses the mixin `HasOffset`, it is very
    important that the userlimits are not polled (or marked as
    `volatile = True`), because the poller does not know whether the device is
    in the process of setting a new offset. Reading the userlimits while the
    offset is being changed requires some special handling (see the places
    where `_setting_new_offset` is called). If the userlimits are polled
    because of a programming error, a warning is written in the poller log.

    Therefore, adjusting the userlimits happens inside the daemon (which is
    aware of offset changes) via a callback mechanism which reacts to changes
    of the absolute limits within the cache. Therefore, the absolute limits
    themselves can be polled normally (read from the poller process and
    then put into the cache).
    '''

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

    def doInit(self, mode):
        if mode == MASTER and session.sessiontype == MAIN:

            # At NICOS startup, the deltas are calculated based on the current
            # values for absolute limits and the cached user limits
            self.delta_limits = (self._absmin() - self.usermin,
                                 self._absmax() - self.usermax)

            # At NICOS startup, inputlimits equal cached userlimits
            self.inputlimits = self.userlimits

            # Add a callback in the daemon which adjusts the userlimits
            # automatically if the abslimits change.
            if self._cache:
                self._cache.addCallback(self, 'abslimits',
                                        self._callbackAbsoluteLimitsChanged)
                self._subscriptions.append(('abslimits',
                                            self._callbackAbsoluteLimitsChanged))

    def _offset(self):
        if isinstance(self, HasOffset):
            return self.offset
        return 0

    def _absmin(self):
        return self.absmin - self._offset()

    def _absmax(self):
        return self.absmax - self._offset()

    def _callbackAbsoluteLimitsChanged(self, key, value, time):
        # Calculate new offsets and put them into the cache, if we're not
        # currently changing the offset.
        if not self._setting_new_offset():
            self._cache.put(self, 'userlimits', self.doReadUserlimits())

    # This function is used to determine whether the device is in the process
    # setting a new offset. The HasOffset mixin temporarily creates an attribute
    # `_new_offset` at the start of its method `_adjustLimitsToOffset` and
    # deletes it again at the end.
    def _setting_new_offset(self):
        if isinstance(self, HasOffset):
            return hasattr(self, '_new_offset')
        return False

    def doReadUserlimits(self):
        # See description of parameter userlim_follow_abslim for an explanation
        # of the behaviour realized here.
        if self.userlim_follow_abslim:
            usermin_raw = self._absmin() - self.delta_limits[0]
            usermax_raw = self._absmax() - self.delta_limits[1]
        else:
            (usermin_raw, usermax_raw) = self.inputlimits

        # Make sure the user limits do not contradict each other
        usermin = min(usermin_raw, usermax_raw)
        usermax = max(usermax_raw, usermin_raw)

        # If the device is in the process of setting a new offset,
        # do not compare against the absolute limits
        if self._setting_new_offset():
            return (usermin, usermax)

        # The poller should never read the user limits, since they are handled
        # by the callback mechanism inside the daemon. In case a child class
        # is configured wrong, log a warning and return the raw limits.
        if session.sessiontype == POLLER:
            self.log.warning('user limits must not be polled (or marked as ' \
                             'volatile) when using mixin `DynamicUserlimits` ' \
                             'in a derived class. Returned user limits might ' \
                             'be outside absolute limits.')
            return (usermin, usermax)

        # Adjust the limits so that the user limits are always within the
        # absolute limits and that they do not contradict each other.
        usermax = min(usermax, self._absmax())
        usermin = max(usermin, self._absmin())
        usermax = max(usermax, self._absmin())
        usermin = min(usermin, self._absmax())
        return (usermin, usermax)

    def doWriteUserlimits(self, value):

        # Update the input limits unconditionally
        self.inputlimits = value

        # Do not check the limits and do not calculate the deltas if we are in
        # the process of setting a new offset
        if self._setting_new_offset():
            return

        # Check if the user limits are OK
        HasLimits.doWriteUserlimits(self, value)

        # Calculate the new deltas AFTER the new offset has been applied. This
        # is the case if _new_offset has been deleted.
        self.delta_limits = (
            self._absmin() - value[0], self._absmax() - value[1])
