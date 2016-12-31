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
#   Pascal Neubert <pascal.neubert@frm2.tum.de>
#
# *****************************************************************************

"""
These classes implement the simple communication protocol into NICOS by
using it to communicate with other hardware.
The SimpleComm devices create a connection to a server that understands the
Simple Communication Protocol. They support TCP and serial connection.
"""

import select
import time
import serial
import threading
import re
import ast

from nicos.core import Readable, Moveable, status, Param, CommunicationError, SIMULATION
from nicos.core.mixins import HasCommunication
from nicos.core.device import Device
from nicos.core.params import host, Attach
from nicos.utils import tcpSocket, closeSocket


class Communicator(HasCommunication, Device):
    """
    This is the base class for all communicator classes.
    It is used in places where any type of communicator is needed.
    """

    parameters = {
        'timeout':    Param('The timeout for the communication', type=float,
                            settable=True, default=3.0),
    }

    def doInit(self, mode):
        self._CRLF = '\r\n'
        self._connected = False
        if mode != SIMULATION:
            self._com_retry(None, self._connect)

    def _connect(self):
        pass

    def communicate(self, data):
        if self._connected:
            return self._com_retry(None, self._communicate, data=data)
        else:
            if self._mode != SIMULATION:
                self._com_retry(None, self._connect)
                if self._connected:
                    return self.communicate(data)

    def _close(self):
        """
        Close the connection.
        """
        self._connected = False

    def doShutdown(self):
        self._close()

    def _parseData(self, sent, recv):
        """
        This method parses the data received from the server
        to check if it matches the sent data and the SCP protocol as well.
        """
        reGeneral = re.match('^([0-9]) (.+)$', recv)
        if reGeneral:
            if reGeneral.group(1) == '0':
                reStd = re.match(r'^([0-9]) ((\w+)/(\w+))([=])(.+)$', recv)
                reMessage = re.match(r'^((\w+)/(\w+))(.+)$', sent)
                if reStd and reMessage:
                    # compare the device and params which should equal
                    if reStd.group(2) == reMessage.group(1):
                        return ast.literal_eval(reStd.group(6))
        raise CommunicationError('Response not matching protocol: %r' % recv)


class EthernetCommunicator(Communicator):
    """
    This communicator class handles the TCP connection to the
    SCP Server.
    """

    parameters = {
        'host':       Param('The server address',
                            type=host, mandatory=True),
    }

    def doInit(self, mode):
        self._sock = None
        Communicator.doInit(self, mode)

    def _connect(self):
        self.log.info('Connecting to %r', self.host)
        self._sock = tcpSocket(self.host, defaultport=14728)
        # set connected true if tcpSocket does not raise a socket.error
        self._connected = True

    def _communicate(self, data):
        self._sock.sendall(data + self._CRLF)
        res = ''
        startTime = time.time()
        while time.time() - startTime < self.timeout:
            if select.select([self._sock], [], [], 0.2)[0]:
                recvData = self._sock.recv(select.PIPE_BUF)
                if recvData:
                    res += recvData
                    if recvData.find('\n') >= 0:
                        break
                else:
                    self._close()
                    raise CommunicationError('Broken Connection')
        return self._parseData(data, res.rstrip(self._CRLF))

    def _close(self):
        """
        Close the socket and set it to None to clean up.
        """
        Communicator._close(self)
        if self._sock:
            closeSocket(self._sock)
            self._sock = None


class SerialCommunicator(Communicator):
    """
    This communicator class handles the serial connection to the
    SCP Server
    """

    parameters = {
        'devfile':    Param('The location of the device file',
                            type=str, mandatory=True),
    }

    def doInit(self, mode):
        self._dev = None
        Communicator.doInit(self, mode)

    def _connect(self):
        try:
            self._dev = serial.Serial(self.devfile, timeout=self.timeout)
            self.log.info('Connected to %r', self.devfile)
            self._connected = True
        except serial.SerialException:
            raise serial.SerialException('Could not connect to %r' % self.devfile)
        self._lock = threading.RLock()

    def _communicate(self, data):
        with self._lock:
            self._dev.write(data + self._CRLF)
            res = ''
            while res.find('\n') < 0:
                res = self._dev.readline()
            return self._parseData(data, res.rstrip(self._CRLF))

    def _close(self):
        """
        Close the serial connection and set the
        object to None to clean up.
        """
        Communicator._close(self)
        if self._dev:
            self._dev.close()
            self._dev = None


class SimpleCommReadable(Readable):
    """
    This class represents a readable device that communicates via the
    simple communication protocol.
    """

    attached_devices = {
        'comm': Attach('Device for communication', Communicator),
    }

    def doInit(self, mode):
        pass

    def doRead(self, maxage=0):
        data = self._attached_comm.communicate(self.name + '/value?')
        return data

    def doStatus(self, maxage=0):
        data = self._attached_comm.communicate(self.name + '/status?')
        if isinstance(data, (list, tuple)):
            if data[0] == 'IDLE':
                return status.OK, data[0].lower()
            elif data[0] == 'BUSY':
                return status.BUSY, data[0].lower()
            elif data[0] == 'ERROR':
                return status.ERROR, data[0].lower()
        return status.UNKNOWN, 'unknown'


class SimpleCommMoveable(SimpleCommReadable, Moveable):
    """
    This class represents a moveable device that communicates via the
    simple communication protocol.
    """

    parameters = {
        'speed': Param('The movement speed of the device',
                       type=float, unit='main/s', settable=True, default=1.0)
    }

    def doStart(self, target):
        msg = self.name + '/target=' + str(target)
        reTarget = self._attached_comm.communicate(msg)
        if reTarget != target:
            self.log.warn('Target value has not been updated')

    def doStop(self):
        self.start(self.read())

    def doWriteSpeed(self, newValue):
        msg = self.name + '/speed=' + str(newValue)
        reValue = self._attached_comm.communicate(msg)
        if reValue != newValue:
            self.log.warn('Speed value has not been updated')
