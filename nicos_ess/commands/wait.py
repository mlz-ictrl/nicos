#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import time

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core import SIMULATION


@usercommand
@helparglist('device, target, accuracy, time_stable, [timeout]')
def waitfor_stable(device, target, accuracy, time_stable, timeout=3600):
    """Wait for the device to be within a certain range of the target value
    for a defined continuous number of seconds.

    If the device takes too long to stabilise then the action will timeout.

    Example:

    >>> waitfor_stable(dev1, 10, 1, 30, 600)

    will wait until the device position is between 9 and 11 for a continous
    period of 30 seconds, but will exit after 10 minutes if
    stability is not reached.

    .. note::

       The default timeout is an hour (3600 s).
    """
    if session.mode == SIMULATION:
        session.clock.tick(time_stable)
        return
    dev = session.getDevice(device)
    start_time = int(time.monotonic())
    in_range = False
    start_in_range = None

    while True:
        curr_pos = dev.read()
        curr_time = int(time.monotonic())

        if curr_time > start_time + timeout:
            session.log.warning(
                'stablilisation timed out - %s might not be '
                'stable', device)
            break

        if abs(target - curr_pos) <= accuracy:
            if not in_range:
                in_range = True
                start_in_range = curr_time
                session.log.warning(
                    '%s is within range, waiting %s seconds '
                    'for it to stabilise', device, time_stable)
        else:
            if in_range:
                session.log.warning('%s is no longer in range', device)
            in_range = False

        if in_range and curr_time > start_in_range + time_stable:
            session.log.warning('%s is considered stable', device)
            break

        session.delay(dev._long_loop_delay)
