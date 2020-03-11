#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.core.acquire import DevStatistics, acquire, read_environment
from nicos.core.constants import FINAL, INTERMEDIATE, INTERRUPTED, LIVE, \
    MAIN, MAINTENANCE, MASTER, POLLER, SIMULATION, SLAVE
from nicos.core.data import BaseDataset, DataSink, DataSinkHandler, \
    PointDataset, ScanDataset
from nicos.core.device import Device, DeviceAlias, DeviceMeta, Measurable, \
    Moveable, NoDevice, Readable, SubscanMeasurable, Waitable, requires
from nicos.core.errors import AccessError, CacheError, CacheLockError, \
    CommunicationError, ComputationError, ConfigurationError, HardwareError, \
    InvalidValueError, LimitError, ModeError, MoveError, NicosError, \
    NicosTimeoutError, PositionError, ProgrammingError, SPMError, UsageError
from nicos.core.mixins import AutoDevice, CanDisable, DeviceMixinBase, \
    HasCommunication, HasLimits, HasMapping, HasOffset, HasPrecision, \
    HasTimeout, HasWindowTimeout, IsController
from nicos.core.params import INFO_CATEGORIES, ArrayDesc, Attach, Override, \
    Param, Value, absolute_path, anytype, dictof, dictwith, floatrange, host, \
    intrange, limits, listof, mailaddress, nicosdev, none_or, nonemptylistof, \
    nonemptystring, oneof, oneofdict, oneofdict_or, pvname, relative_path, \
    setof, subdir, tacodev, tangodev, tupleof, vec3
from nicos.core.scan import Scan
from nicos.core.utils import ACCESS_LEVELS, ADMIN, GUEST, USER, User, \
    formatStatus, multiReset, multiStatus, multiStop, multiWait, system_user, \
    usermethod, waitForCompletion, watchdog_user
