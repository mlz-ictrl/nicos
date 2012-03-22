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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF focussing neutron guide device."""

__version__ = "$Revision$"

from time import sleep

from nicos.common import Slit

from nicos.core import oneof, Moveable, HasPrecision, Param, Value, Override, \
     AutoDevice, InvalidValueError


class FocussingNeutronGuide(Slit):
    """A rectangular focussing neutron guide consisting of four mirrors.

    The TOFTOF has a focussing neutron guide at which all four mirrors
    are bended by a small piezo motor to create a focussing cone at
    front of the guide.

    The guide can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '4blades' -- all four blades are controlled separately.  Values read from
      the slit are lists in the order ``[left, right, bottom, top]``; for
      ``move()`` the same list of coordinates has to be supplied.
    * 'centered' -- only width and height are controlled; the slit is centered
      at the zero value of the left-right and bottom-top coordinates.  Values
      read and written are in the form ``[width, height]``.(disabled at the 
      moment)
    * 'offcentered' -- the center and width/height are controlled.  Values read
      and written are in the form ``[centerx, centery, width, height]``.
      (disabled at the moment)

    Normally, the ``right`` and ``left`` as well as the ``bottom`` and ``top``
    devices need to share a common coordinate system, i.e. when ``right.read()
    == left.read()`` the slit is closed.  A different convention can be selected
    when setting `coordinates` to ``"opposite"``: in this case, the blades meet
    at coordinate 0, and both move in positive direction when they open.

    All instances have attributes controlling single dimensions that can be used
    as devices, for example in scans.  These attributes are:

    * `left`, `right`, `bottom`, `top` -- controlling the blades individually,
      independent of the opmode
    * `centerx`, `centery`, `width`, `height` -- controlling "logical"
      coordinates of the guide, independent of the opmode

    Example usage::

        >>> move(ng.centerx, 5)      # move slit center
        >>> scan(ng.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    attached_devices = {
        'right':  (HasPrecision, 'Right mirror'),
        'left':   (HasPrecision, 'Left mirror'),
        'bottom': (HasPrecision, 'Bottom mirror'),
        'top':    (HasPrecision, 'Top mirror'),
    }

    parameter_overrides = {
        'opmode': Override('Mode of operation for the slit',
                       type=oneof('4blades'), # , 'centered', 'offcentered'),
                       settable=True),
    }

    hardware_access = False

    def doInit(self):
        Slit.doInit(self)
