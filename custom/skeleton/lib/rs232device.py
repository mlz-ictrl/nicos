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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""
Skeleton module for using directly or TACO attached RS232 devices.

Please remember to change the class names if copying from this file!
"""

from time import sleep

from IO import StringIO
import serial

from nicos.core import Readable, Moveable, Param, CommunicationError, NicosError
from nicos.devices.taco import TacoDevice
from nicos.core import SIMULATION


class RS232Example(Readable):
    """Example class using  direct RS232 communication via pyserial

    Attention: this class does not serialize access to the serial port,
    so devices from this class should only be used from one instance.
    This means: Do not poll these devices with the poller.

    To black-list a setup from polling, add its name to the "neverpoll"
    parameter of the Poller device in setups/special/poller.py.  To
    black-list a single device, add its name to the "blacklist" parameter
    of the Poller device.

    EOL characters need to be added explicitly.
    """

    parameters = {
        'port': Param('RS232 port', type=str,
                      settable=False, mandatory=True),
        'param1': Param('first param', unit='Hz', settable=False,
                        category='general'),
        'param2': Param('second param', unit='Vrms',
                        settable=True, category='general'),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        self._dev = serial.Serial(self.port)

        # sanity check: try to ask the device for its identification and
        # make sure a suitable string is received
        self._dev.write('*IDN?\n')
        reply = self._dev.readline()
        if not reply.startswith('<some string>'):
            raise CommunicationError('wrong identification: %r' % reply)

    def communicate(self, query):
        # NB: this should be factored out into the common RS232 base class
        # once it is created.
        try:
            self._dev.write('%s\n' % query)
            value = self._dev.readline()
        except ValueError:
            # retry communication/handle error after a bit of sleeping
            sleep(0.2)
            self._dev.write('%s\n' % query)
            try:
                value = self._dev.readline()
            except ValueError:
                raise CommunicationError(self, 'could not read reply')
        return value

    def doRead(self, maxage=0):
        return float(self.communicate('something'))

    def doReadParam1(self):
        try:
            return float(self.communicate('something param1'))
        except (NicosError, ValueError):
            return 0

    def doReadParam2(self):
        try:
            return float(self.communicate('something param2'))
        except (NicosError, ValueError):
            return 0

    def doWriteParam2(self, value):
        self._dev.write('something param2 %s\n' % value)


class RS232TACOExample(TacoDevice, Moveable):
    """RS232 example class uisng a TACO RS232 server

    This class is properly serialized through the server
    and EOL handling is done by the server as well.
    """

    parameters = {
        'param1': Param('first param', unit='Hz', settable=False,
                        category='general'),
        'param2': Param('second param', unit='Vrms',
                        settable=True, category='general'),
    }

    taco_class = StringIO

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        reply = self._taco_guard(self._dev.communicate, '*IDN?')
        if not reply.startswith('<some string>'):
            raise CommunicationError('wrong identification: %r' % reply)

    def doRead(self, maxage=0):
        try:
            value = float(self._taco_guard(self._dev.communicate, 'OUTP? 1'))
        except (NicosError, ValueError):
            # retry communication/handle error
            value = float(self._taco_guard(self._dev.communicate, 'OUTP? 1'))
        return value

    def doReadParam1(self):
        try:
            value = float(self._taco_guard(self._dev.communicate,
                                           'read param 1'))
        except (NicosError, ValueError):
            value = 0
        return value

    def doReadParam2(self):
        try:
            value = float(self._taco_guard(self._dev.communicate,
                                           'read param 2'))
        except (NicosError, ValueError):
            value = 0
        return value

    def doWriteParam2(self, value):
        float(self._taco_guard(self._dev.communicate, 'read param 2%s' % value))
