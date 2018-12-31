#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import

from nicos.core import Device
from nicos.core.errors import ProgrammingError


class CacheEntrySerializer(Device):
    """Base class to serialize and de-serialize the entries for cache

    Following methods must be implemented in the derived classes:
    * encode(key, entry, **params)
    where `entry` represents the instance to be serialized and the `key`
    is the NICOS key for which this entry is written.

    * decode(encoded) : returns tuple of (key, entry)
    The decode method should return a key and entry tuple decoded from
    the message.
    """

    def encode(self, key, entry, **params):
        raise ProgrammingError('Encoder not implemented')

    def decode(self, encoded):
        raise ProgrammingError('Decoder not implemented')
