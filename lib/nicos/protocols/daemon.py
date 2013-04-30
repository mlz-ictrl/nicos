#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon protocol helpers."""

import struct
import cPickle as pickle


# default port for the daemon

DEFAULT_PORT = 1301

# protocol version

PROTO_VERSION = 7

# message serialization/deserialization

# one-byte responses without length
ACK = '\x06'   # executed ok, no further information follows

# responses with length, encoded as a 32-bit integer
STX = '\x03'   # executed ok, reply follows
NAK = '\x15'   # error occurred, message follows
LENGTH = struct.Struct('>I')   # used to encode length

# argument separator in client commands
RS = '\x1e'

def serialize(data):
    """Serialize an object."""
    return pickle.dumps(data, 2)

unserialize = pickle.loads   # Unserialize an object.

# pyctl status constants

STATUS_IDLEEXC  = -2  # nothing started, last script raised exception
STATUS_IDLE     = -1  # nothing started
STATUS_RUNNING  = 0   # execution running
STATUS_INBREAK  = 1   # execution halted, in break function
STATUS_STOPPING = 2   # stop exception raised, waiting for propagation

# daemon event specification

# key: event name
# value: whether the event data is serialized

# IMPORTANT: add new events to the documentation too!

DAEMON_EVENTS = {
    # a new message arrived
    'message': True,
    # a new request arrived
    'request': True,
    # a request is now being processed
    'processing': True,
    # one or more requests have been blocked from execution
    'blocked': True,
    # the execution status changed
    'status': True,
    # the watched variables changed
    'watch': True,
    # the mode changed
    'mode': True,
    # a new cache value has arrived
    'cache': True,
    # a new dataset was created
    'dataset': True,
    # a new point was added to a dataset
    'datapoint': True,
    # a new fit curve was added to a dataset
    'datacurve': True,
    # new parameters for the data sent with the "livedata" event
    'liveparams': True,
    # live detector data to display
    'livedata': False,
    # a simulation finished with the given result
    'simresult': True,
    # request to display given help page
    'showhelp': True,
    # request to execute something on the client side
    'clientexec': True,
    # a watchdog notification has arrived
    'watchdog': True,
    # the remote-debugging status changed
    'debugging': True,
    # a plug-and-play/sample-environment event occurred
    'plugplay': True,
    # a setup was loaded or unloaded
    'setup': True,
    # a device was created or destroyed
    'device': True,
}
