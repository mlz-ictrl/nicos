#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""Varian Mini-TASK vacuum pump device."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from IO import StringIO

from nicos import status
from nicos.taco import TacoDevice
from nicos.device import Readable, Override
from nicos.errors import CommunicationError

def addcrc(msg):
    crc = 0
    for c in msg[1:]:
        crc ^= ord(c)
    return msg + '%02X' % crc

class VarianPump(TacoDevice, Readable):
    """
    Device object for a Varian Mini-Task (AG81 type) pump.
    """
    taco_class = StringIO

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='mbar'),
    }

    def _communicate(self, window, read=True, data=''):
        window = '%03d' % window
        msg = '\x02\x80%s%s\x03' % (window, '\x30' if read else '\x31')
        resp = self._taco_guard(self._dev.communicate, addcrc(msg))
        if resp[:2] != '\x02\x80' or resp[2:5] != window or resp[-3] != '\x03':
            raise CommunicationError(self, 'invalid response %r' % resp)
        return resp[5:-3]

    def doRead(self):
        return float(self._communicate(224))

    def doStatus(self):
        stcode = int(self._communicate(205))
        errorcode = int(self._communicate(206))
        frequency = self._communicate(226)
        sttext = {0: 'stopped', 1: 'waiting interlock', 2: 'starting',
                  3: 'auto-tuning', 4: 'braking', 5: 'normal', 6: 'fail'
                  }[stcode]
        stval = {0: status.ERROR, 1: status.BUSY, 2: status.BUSY,
                 3: status.OK, 4: status.BUSY, 5: status.OK, 6: status.ERROR
                 }[stcode]
        errtext = []
        # XXX make this a utility function
        if errorcode & 1: errtext.append('no connection')
        if errorcode & 2: errtext.append('pump overtemperature')
        if errorcode & 4: errtext.append('controller overtemperature')
        if errorcode & 32: errtext.append('overvoltage')
        if errorcode & 64: errtext.append('short circuit')
        if errorcode & 128: errtext.append('too high load')
        return stval, 'status: %s, error: %s, frequency: %s' % \
               (sttext, ', '.join(errtext or ['none']), frequency)
