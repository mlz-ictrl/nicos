#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

__version__ = "$Revision$"

from time import sleep

from nicos.core import status


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
        rettext.append('%s=%s' % (devname, text))
        if state > retstate:
            retstate = state
    return retstate, ', '.join(rettext)


def waitForStatus(device, delay=0.3, busystates=(status.BUSY,)):
    """Wait for the *device* status to return exit the busy state.

    *delay* is the delay between status inquiries, and *busystates* gives the
    state values that are considered as "busy" states; by default only
    `status.BUSY`.
    """
    # XXX add a timeout?
    # XXX what about error status?
    while True:
        st = device.status(0)
        if st[0] in busystates:
            sleep(delay)
            # XXX add a breakpoint here?
        else:
            break
    return st
