#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from nicos.core import status
from nicos.core.constants import MASTER, SLAVE, SIMULATION, MAINTENANCE, \
    MAIN, POLLER, LIVE, INTERMEDIATE, INTERRUPTED, FINAL
from nicos.core.errors import NicosError, ProgrammingError, \
    ConfigurationError, UsageError, InvalidValueError, ModeError, \
    PositionError, MoveError, LimitError, CommunicationError, \
    HardwareError, TimeoutError, ComputationError, \
    CacheLockError, AccessError, CacheError, SPMError
from nicos.core.mixins import DeviceMixinBase, AutoDevice, HasLimits, \
    HasOffset, HasPrecision, HasMapping, HasTimeout, HasWindowTimeout, \
    HasCommunication
from nicos.core.device import DeviceMeta, Device, Readable, Waitable, \
    Moveable, Measurable, SubscanMeasurable, DeviceAlias, NoDevice, \
    usermethod, requires
from nicos.core.params import Attach, Param, Override, Value, ArrayDesc, \
    INFO_CATEGORIES, listof, nonemptylistof, tupleof, dictof, setof, tacodev, \
    tangodev, anytype, vec3, intrange, floatrange, oneof, oneofdict, none_or, \
    nicosdev, relative_path, absolute_path, subdir, mailaddress, limits, \
    dictwith, host
from nicos.core.data import BaseDataset, PointDataset, ScanDataset, DataSink, \
    DataSinkHandler
from nicos.core.acquire import acquire, read_environment, DevStatistics
from nicos.core.scan import Scan
from nicos.core.utils import formatStatus, multiStatus, waitForStatus, \
    multiWait, multiStop, multiReset, GUEST, USER, ADMIN, ACCESS_LEVELS, \
    User, system_user, watchdog_user

# XXX(dataapi): to be removed
from nicos.core.image import ImageSink
