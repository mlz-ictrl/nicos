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
#   Alexander Söderqvist <alexander.soederqvist@psi.ch>
#
# *****************************************************************************
"""
Wrap miscellaneous epics methods to hide underlying library.
"""
from nicos.devices.epics.base import DEFAULT_EPICS_PROTOCOL


def epics_get(name, timeout=3.0):
    """
    Wrap epics getters
    """
    if DEFAULT_EPICS_PROTOCOL == 'pva':
        from nicos.devices.epics.wrapper.p4p import pvget
        return pvget(name, timeout)
    else:
        from nicos.devices.epics.wrapper.caproto import caget
        return caget(name, timeout)


def epics_put(name, value, wait=False, timeout=3.0):
    """
    Wrap epics putters
    """
    if DEFAULT_EPICS_PROTOCOL == 'pva':
        from nicos.devices.epics.wrapper.p4p import pvput
        return pvput(name, value, wait, timeout)
    else:
        from nicos.devices.epics.wrapper.caproto import caput
        return caput(name, value, wait, timeout)
