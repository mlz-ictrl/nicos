#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon protocol parts common to server and client."""

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
#   (not used in all protocols)

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

# possible states of ETA simulation

SIM_STATES = {
    'pending': 0x01,
    'running': 0x02,
    'success': 0x03,
    'failed':  0x04,
}


class ProtocolError(Exception):
    """Exception to be raised on protocol/serialization errors."""


class CloseConnection(Exception):
    """Exception to be raised to close the connection gracefully."""


class Server(object):
    """Represents a server, should create a transport for each client."""

    def __init__(self, daemon, address, serializer):
        self.daemon = daemon
        self.serializer = serializer

    def start(self, interval):
        """Start the server.

        This method should block (it is run in a thread) until the server is
        stopped by the main thread calling `stop()`.
        """
        raise NotImplementedError

    def stop(self):
        """Stop the server.

        This is called from the main thread upon receipt of a stop signal.
        """
        raise NotImplementedError

    def close(self):
        """Close the server.

        This is called from the main thread after the server thread is done.
        """
        raise NotImplementedError

    def emit(self, event, data, handler=None):
        """Emit an event.  If *handler* is given, only to this client.
        """
        raise NotImplementedError


class ServerTransport(object):
    """Represents the transport of data to one client, server side."""

    def close(self):
        """Close this client connection and clean up any resources."""
        raise NotImplementedError

    def get_version(self):
        """Return the server's protocol version as an integer.

        XXX: decide about versioning scheme (global/transport specific)
        """
        raise NotImplementedError

    def recv_command(self):
        """Blockingly wait for a new command from the client.

        Returns the deserialized command name and data as a tuple.
        """
        raise NotImplementedError

    def send_ok_reply(self, payload):
        """Send a "ok" type reply back to the client.

        *payload* is a piece of data to be serialized and sent along.
        """
        raise NotImplementedError

    def send_error_reply(self, reason):
        """Send an "error" type reply back to the client.

        *reason* is a string with an error description.
        """
        raise NotImplementedError

    def send_event(self, evtname, payload):
        """Send an event to the client.

        *evtname* is the event name, as defined in nicos.protocols.daemon.
        *payload* is the event data.  It is transport specific whether this
        data is already serialized.
        """
        raise NotImplementedError


class ClientTransport(object):
    """Represents the transport of data, client side."""

    def connect(self, conndata):
        """Establish the request-reply connection to the server.

        *conndata* is a ConnectionData object with connection information.

        XXX: change conndata to be less raw-socket specific.
        """
        raise NotImplementedError

    def connect_events(self, conndata):
        """Establish the event connection.

        This is a separate step because if authentication fails, the event
        connection is never opened.

        *conndata* is the ConnectionData object as for `connect()`.
        """
        raise NotImplementedError

    def disconnect(self):
        """Disconnect any established connections, including for events."""
        raise NotImplementedError

    def send_command(self, cmdname, args):
        """Send a command to the server.

        *cmdname* is the event name, as defined in nicos.protocols.daemon.
        *args* is a data object, in the format expected for this command,
        to be serialized.
        """
        raise NotImplementedError

    def recv_reply(self):
        """Blockingly receive a reply from the server.

        Returns a tuple of the success (ok/error) as a bool, and the extended
        data, if present, else None.
        """
        raise NotImplementedError

    def recv_event(self):
        """Blockingly receive an event from the server.

        Returns a tuple of the event name and the (deserialized if necessary)
        event data.
        """
        raise NotImplementedError


class Serializer(object):
    """Represents a serialization format for commands and events."""

    def serialize_cmd(self, cmdname, args):
        """Serialize arguments payload for the given command.

        The *cmdname* does not have to be used if command names are not part of
        the serialized data for this protocol.
        """
        raise NotImplementedError

    def serialize_ok_reply(self, payload):
        """Serialize payload for an "ok" type reply."""
        raise NotImplementedError

    def serialize_error_reply(self, reason):
        """Serialize payload for an "error" type reply.

        *reason* is always a string.
        """
        raise NotImplementedError

    def serialize_event(self, evtname, payload):
        """Serialize payload for the given event.

        The *evtname* does not have to be used if event names are not part of
        the serialized data for this protocol.
        """
        raise NotImplementedError

    def deserialize_cmd(self, data, cmdname=None):
        """Deserialize arguments payload for the command.

        If the command name is not part of the serialized data for this
        protocol, it must be provided in the *cmdname* argument.

        Returns a tuple of command name and deserialized arguments.
        """
        raise NotImplementedError

    def deserialize_reply(self, data, success=None):
        """Deserialize payload of a reply from the server.

        If the success (ok/error) state is not part of the serialized data for
        this protocol, it must be provided in the *success* argument.

        Returns a tuple of the success status (as a bool) and the payload.
        """
        raise NotImplementedError

    def deserialize_event(self, data, evtname=None):
        """Deserialize payload of an event from the server.

        If the event name is not part of the serialized data for this protocol,
        it must be provided in the *evtname* argument.

        Returns a tuple of the event name and deserialized payload.
        """
        raise NotImplementedError
