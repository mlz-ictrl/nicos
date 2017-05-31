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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Common parts of the "classic" daemon protocol."""

import json
import struct

from nicos.protocols.daemon import DAEMON_COMMANDS, DAEMON_EVENTS, \
    Serializer as BaseSerializer
from nicos.pycompat import cPickle as pickle

# default port for the daemon

DEFAULT_PORT = 1301

# protocol version, increment this whenever making changes to command
# arguments or adding new commands

PROTO_VERSION = 17

# old versions with which the client is still compatible

COMPATIBLE_PROTO_VERSIONS = []

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
# frame format: STX + eventcode (2 bytes) + LENGTH + payload

READ_BUFSIZE = 4096


# command and event code numbers

_codefmt = struct.Struct('>H')

command2code, code2command = {}, {}
for _name, _number in DAEMON_COMMANDS.items():
    _enc = _codefmt.pack(_number)
    command2code[_name] = _enc
    code2command[_enc] = _name

event2code, code2event = {}, {}
for _name, (_, _number) in DAEMON_EVENTS.items():
    _enc = _codefmt.pack(_number)
    event2code[_name] = _enc
    code2event[_enc] = _name


class ClassicSerializer(BaseSerializer):

    name = 'classic'

    # serializing

    def serialize_cmd(self, cmdname, args):
        return pickle.dumps(args, 2)

    def serialize_ok_reply(self, payload):
        return pickle.dumps(payload, 2)

    def serialize_error_reply(self, reason):
        return pickle.dumps(reason, 2)

    def serialize_event(self, evtname, payload):
        return pickle.dumps(payload, 2)

    # deserializing

    def deserialize_cmd(self, data, cmdname=None):
        return cmdname, pickle.loads(data)

    def deserialize_reply(self, data, success=None):
        assert success is not None
        data = pickle.loads(data) if data else None
        return success, data

    def deserialize_event(self, data, evtname=None):
        return evtname, pickle.loads(data)


class JsonSerializer(BaseSerializer):

    name = 'json'

    def __init__(self):
        self.encoder = json.JSONEncoder(default=self._serialize_default)
        self.decoder = json.JSONDecoder(object_hook=self._object_hook)

    def _serialize_default(self, obj):
        return {'__pickle__': pickle.dumps(obj, 2).decode('latin1')}

    def _object_hook(self, obj):
        if '__pickle__' in obj:
            return pickle.loads(obj['__pickle__'].encode('latin1'))
        return obj

    # serializing

    def serialize_cmd(self, cmdname, args):
        return self.encoder.encode(args).encode()

    def serialize_ok_reply(self, payload):
        return self.encoder.encode(payload).encode()

    def serialize_error_reply(self, reason):
        return self.encoder.encode(reason).encode()

    def serialize_event(self, evtname, payload):
        return self.encoder.encode(payload).encode()

    # deserializing

    def deserialize_cmd(self, data, cmdname=None):
        return cmdname, self.decoder.decode(data.decode())

    def deserialize_reply(self, data, success=None):
        assert success is not None
        data = self.decoder.decode(data.decode()) if data else None
        return success, data

    def deserialize_event(self, data, evtname=None):
        return evtname, self.decoder.decode(data.decode())


SERIALIZERS = {
    ClassicSerializer.name: ClassicSerializer,
    JsonSerializer.name: JsonSerializer,
}
