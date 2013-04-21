#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS core utility functions."""

from time import sleep, time as currenttime

from nicos import session
from nicos.core import status
from nicos.core.errors import TimeoutError, MoveError, PositionError


# user access levels
GUEST = 0
USER  = 10
ADMIN = 20
ACCESS_LEVELS = {0: 'guest', 10: 'user', 20: 'admin'}


def multiStatus(devices, maxage=None):
    """Combine the status of multiple devices to form a single status value.

    This is typically called in the `doStatus` method of "superdevices" that
    control several attached devices.

    The resulting state value is the highest value of all devices' values
    (i.e. if all devices are `OK`, it will be `OK`, if one is `BUSY`, it will be
    `BUSY`, but if one is `ERROR`, it will be `ERROR`).

    The resulting state text is a combination of the status texts of all
    devices.
    """
    rettext = []
    retstate = status.OK
    for devname, dev in devices:
        if dev is None:
            continue
        state, text = dev.status(maxage)
        if '=' in text:
            rettext.append('%s=(%s)' % (devname, text))
        else:
            rettext.append('%s=%s' % (devname, text))
        if state > retstate:
            retstate = state
    return retstate, ', '.join(rettext)


def waitForStatus(device, delay=0.3, timeout=None,
                  busystates=(status.BUSY,),
                  errorstates=(status.ERROR, status.NOTREACHED)):
    """Wait for the *device* status to return exit the busy state.

    *delay* is the delay between status inquiries, and *busystates* gives the
    state values that are considered as "busy" states; by default only
    `status.BUSY`.
    """
    started = currenttime()
    while True:
        st = device.status(0)
        if st[0] in busystates:
            sleep(delay)
            if timeout is not None and currenttime() - started > timeout:
                raise TimeoutError(device, 'waiting timed out (timeout %.1f s)'
                                   % timeout)
        elif st[0] in errorstates:
            if st[0] == status.NOTREACHED:
                raise PositionError(device, st[1])
            else:
                raise MoveError(device, st[1])
        else:
            break
    return st


def formatStatus(st):
    const, message = st
    const = status.statuses.get(const, str(const))
    return const + (message and ': ' + message or '')


def getExecutingUser():
    """Returns a valid authenticated User object or a default User, if running
    in the console.
    """
    # ugly, but avoids an import loop
    from nicos.services.daemon.auth import system_user, User
    try:
        s = session.daemon_device.current_script()
        user = User(s.user, s.userlevel)
    except AttributeError:  # no daemon_device
        user = system_user
    return user


def checkUserLevel(user, level=0):
    return user.level >= level
