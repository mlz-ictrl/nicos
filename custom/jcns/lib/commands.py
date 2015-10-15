#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Module for JCNS specific user commands."""

from nicos.core import HasOffset, Readable
from nicos.core.spm import spmsyntax, Dev, Bare, Multi, AnyDev, DevParam
from nicos.commands import usercommand, helparglist, parallel_safe
from nicos.commands.device import adjust as _adjust, reset as _reset, \
    set as _set


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(Readable)))
@parallel_safe
def init(*devlist):
    """Initialize (reset) the given device(s).

    This can restore communication with the device, re-set a positioning fault
    or make a reference drive (only for devices where this cannot lead to
    crashes, such as slits).

    Examples:

    >>> init(ss1)        # reset a single device
    >>> init(ss1, ss2)   # reset multiple devices
    """
    _reset(*devlist)


@usercommand
@spmsyntax(Dev(HasOffset), Bare)
def recalibrate(dev, value):
    """Adjust the offset of the device to the given value.

    Example:

    >>> recalibrate(om, 100)   # om's current value is now 100
    """
    _adjust(dev, value)


@usercommand
@spmsyntax(AnyDev, DevParam, Bare)
@parallel_safe
def configure(dev, parameter, value):
    """Set a the parameter of the device to a new value.

    Example:

    >>> configure(phi, 'speed', 50)
    """
    _set(dev, parameter, value)
