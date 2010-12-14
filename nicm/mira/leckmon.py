#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Toni leakage monitor class
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Toni leakage monitor class."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from nicm.device import Readable, Param
from nicm.errors import CommunicationError
from nicm.taco.base import TacoDevice


class Monitor(TacoDevice, Readable):

    taco_class = StringIO

    parameters = {
        'addr':  Param('Bus address of monitor', type=int, mandatory=True),
    }

    def _crc(self, str):
        crc = ord(str[0])
        for i in str[1:]:
            crc ^= ord(i)
        return crc

    def _communicate(self, msg):
        out = '%02X00%s' % (self.addr, msg)
        out = '\x02%s%02X\x03' % (out, self._crc(out))
        ret = self._taco_guard(self._dev.communicate, out)
        if not ret.startswith('\x0200%02x>' % self.addr):
            raise CommunicationError('got garbage from device')
        if '%02X' % self._crc(ret[1:-2]) != ret[-2:]:
            raise CommunicationError('invalid checksum in answer')
        return ret[6:-2]

    def doRead(self):
        return self._communicate('S?')
