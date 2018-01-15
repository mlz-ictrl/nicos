#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from nicos.pycompat import cPickle as pickle


# default port for the daemon

DEFAULT_PORT = 1301

# protocol version, increment this whenever making changes to command
# arguments or adding new commands

PROTO_VERSION = 19

# old versions with which the client is still compatible
# 18 -> 19: Add support for multiple images in 'liveparams' event
#           (using lists for shapes and filenames) and send one 'livedata'
#           event for each array

COMPATIBLE_PROTO_VERSIONS = [18]

# message serialization/deserialization

# to encode payload lengths as network-order 32-bit unsigned int
LENGTH = struct.Struct('>I')

# command frame (client -> daemon)
# frame format: ENQ + commandcode (3 bytes) + LENGTH + payload
ENQ = b'\x05'

# one-byte response without length
# frame format: ACK
ACK = b'\x06'   # executed ok, no further information follows

# error response with payload
# frame format: NAK + LENGTH + payload
NAK = b'\x15'   # error occurred, message follows

# response with payload
# frame format: STX + LENGTH + payload
STX = b'\x03'   # executed ok, reply follows

# also for events
# frame format: STX + eventcode (3 bytes) + LENGTH + payload


# to serialize/unserialize payload data:

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

# break/stop level constants

BREAK_AFTER_LINE = 1  # break after current command in script
BREAK_AFTER_STEP = 2  # break after scan step (or any breakpoint with level 2)
BREAK_NOW = 3         # break "now" (i.e. also while counting)
BREAK_IMMEDIATE = 5   # immediate stop

# daemon command specification

# tuples of
# - command name
# - command code (integer < 65535, will be converted to 2 bytes)

DAEMON_COMMANDS = {
    # script control commands
    'start':          0x01,
    'simulate':       0x02,
    'queue':          0x03,
    'unqueue':        0x04,
    'update':         0x05,
    # script flow commands
    'break':          0x11,
    'continue':       0x12,
    'stop':           0x13,
    'emergency':      0x14,
    'finish':         0x15,
    # async execution commands
    'exec':           0x21,
    'eval':           0x22,
    # watch variable commands
    'watch':          0x31,
    'unwatch':        0x32,
    # enquiries
    'getversion':     0x41,
    'getstatus':      0x42,
    'getmessages':    0x43,
    'getscript':      0x44,
    'gethistory':     0x45,
    'getcachekeys':   0x46,
    'gettrace':       0x47,
    'getdataset':     0x48,
    # miscellaneous commands
    'complete':       0x51,
    'transfer':       0x52,
    'debug':          0x53,
    'debuginput':     0x54,
    # connection related commands
    'eventmask':      0x61,
    'unlock':         0x62,
    'quit':           0x63,
    'authenticate':   0x64,  # only used during handshake
    'eventunmask':    0x65,
    'rearrange':      0x66,
}

ACTIVE_COMMANDS = set((
    'start', 'queue', 'unqueue', 'rearrange', 'update',
    'break', 'continue', 'stop', 'finish', 'exec',  # 'emergency' is allowed
))

_codefmt = struct.Struct('>H')

command2code, code2command = {}, {}
for _name, _number in DAEMON_COMMANDS.items():
    _enc = _codefmt.pack(_number)
    command2code[_name] = _enc
    code2command[_enc] = _name

# daemon event specification

# key: event name
# value: - whether the event data is serialized or raw bytes
#        - event code (integer < 65535, will be converted to 2 bytes)

# IMPORTANT: add new events to the documentation too!

DAEMON_EVENTS = {
    # a new message arrived
    'message':     (True, 0x1001),
    # a new request arrived
    'request':     (True, 0x1002),
    # a request is now being processed
    'processing':  (True, 0x1003),
    # one or more requests have been blocked from execution
    'blocked':     (True, 0x1004),
    # the execution status changed
    'status':      (True, 0x1005),
    # the watched variables changed
    'watch':       (True, 0x1006),
    # the mode changed
    'mode':        (True, 0x1007),
    # a new cache value has arrived
    'cache':       (True, 0x1008),
    # a new dataset was created
    'dataset':     (True, 0x1009),
    # a new point was added to a dataset
    'datapoint':   (True, 0x100A),
    # a new fit curve was added to a dataset
    'datacurve':   (True, 0x100B),
    # new parameters for the data sent with the "livedata" event
    'liveparams':  (True, 0x100C),
    # live detector data to display
    'livedata':    (False, 0x100D),
    # a simulation finished with the given result
    'simresult':   (True, 0x100E),
    # request to display given help page
    'showhelp':    (True, 0x100F),
    # request to execute something on the client side
    'clientexec':  (True, 0x1010),
    # a watchdog notification has arrived
    'watchdog':    (True, 0x1011),
    # the remote-debugging status changed
    'debugging':   (True, 0x1012),
    # a plug-and-play/sample-environment event occurred
    'plugplay':    (True, 0x1013),
    # a setup was loaded or unloaded
    'setup':       (True, 0x1014),
    # a device was created or destroyed
    'device':      (True, 0x1015),
    # the experiment has changed
    'experiment':  (True, 0x1016),
    # the user is prompted to continue
    'prompt':      (True, 0x1017),
    # queued script has been updated
    'updated':     (True, 0x1018),
    # order of queued scripts changed
    'rearranged':  (True, 0x1019),
    # estimated finishing time for the currently running script
    'eta':         (True, 0x101A),
    # message sent out while simulating
    'simmessage':  (True, 0x101B),
}

event2code, code2event = {}, {}
for _name, (_, _number) in DAEMON_EVENTS.items():
    _enc = _codefmt.pack(_number)
    event2code[_name] = _enc
    code2event[_enc] = _name


# possible states of ETA simulation

SIM_STATES = {
    'pending': 0x01,
    'running': 0x02,
    'success': 0x03,
    'failed': 0x04,
}
