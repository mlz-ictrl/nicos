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

"""NICOS core APIs and classes."""

__version__ = "$Revision$"

from nicos.core import status
from nicos.core.errors import NicosError, ProgrammingError, \
     ConfigurationError, UsageError, InvalidValueError, ModeError, \
     PositionError, MoveError, LimitError, CommunicationError, \
     HardwareError, TimeoutError, ComputationError, FixedError, \
     CacheLockError, AccessError
from nicos.core.device import Device, AutoDevice, Readable, Moveable, \
     HasLimits, HasOffset, HasPrecision, Measurable, usermethod, \
     requires
from nicos.core.params import Param, Override, Value, INFO_CATEGORIES, \
     listof, nonemptylistof, tupleof, dictof, tacodev, anytype, \
     vec3, intrange, floatrange, oneof, oneofdict, none_or, \
     control_path_relative
from nicos.core.utils import multiStatus, waitForStatus, GUEST, USER, ADMIN, \
     ACCESS_LEVELS
