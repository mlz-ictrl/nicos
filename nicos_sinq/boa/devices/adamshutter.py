#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import select
import socket

from nicos import session
from nicos.core import SIMULATION, CommunicationError, Param, \
    ProgrammingError, status
from nicos.core.device import Moveable
from nicos.core.errors import MoveError
from nicos.core.params import oneof
from nicos.devices.generic.sequence import SeqMethod, SeqSleep, SequencerMixin
from nicos.utils import closeSocket


class AdamShutter(SequencerMixin, Moveable):
    """
    At BOA the new SINQ shutter system is controlled via a Adam6051 binary I/O
    module. This module speaks modbus over TCP/IP.
    """

    parameters = {
        'host':      Param('Hostname (or IP) of network2serial converter',
                           type=str, settable=True, mandatory=True),
        'port':      Param('TCP Port on network2serial converter',
                           type=int, default=4001),
    }
    valuetype = oneof('open', 'closed', 'enclosure broken')
    _connection = None
    readRequest = bytearray([1, 0, 0, 0, 0, 6, 1, 1, 0, 0, 0, 12])
    zeroRequest = [2, 0, 0, 0, 0, 6, 1, 5, 0, 0, 0, 0]
    setRequest = [2, 0, 0, 0, 0, 6, 1, 5, 0, 0, 255, 0]
    busTimeout = 50

    def doInit(self, mode):
        if mode != SIMULATION:
            try:
                self.doReset()
            except Exception:
                self.log.exception('Failed to connect to adam shutter module')

    def doIsAllowed(self, target):
        if self.read(0) == 'enclosure broken':
            return False, 'Cannot move shutter when enclosure is broken'
        return True, ''

    def _transact(self, request, expected_bytes):
        self._connection.sendall(request)
        p = select.select([self._connection], [], [], self.busTimeout)
        if self._connection in p[0]:
            data = self._connection.recv(expected_bytes)
        else:
            raise CommunicationError('No response from adam-6051')
        return bytearray(data)

    def doRead(self, maxage=0):
        byte_data = self._transact(self.readRequest, 11)
        stat = byte_data[9]
        if stat & 8:
            return 'enclosure broken'
        elif stat & 2:
            return 'open'
        elif stat & 1:
            return 'closed'
        raise ProgrammingError('Cannot interpret adam code %d' % stat)

    def doStart(self, target):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self.target == self.read(0):
            session.log.info('Shutter is alread at %s', self.target)
            return

        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))

    def _generateSequence(self, target):

        seq = []
        if target == 'open':
            address = 16
        else:
            address = 17
        self.zeroRequest[9] = address
        self.setRequest[9] = address

        # This implements pulsing the bit
        seq.append(SeqMethod(self, '_transact', bytearray(self.zeroRequest),
                             12))

        seq.append(SeqSleep(.1))

        seq.append(SeqMethod(self, '_transact', bytearray(self.setRequest),
                             12))

        seq.append(SeqSleep(.2))

        seq.append(SeqMethod(self, '_transact', bytearray(self.zeroRequest),
                             12))

        seq.append(SeqSleep(.1))

        return seq

    def doStatus(self, maxage=0):
        if self.read(maxage) == self.target:
            return status.OK, ''
        return status.BUSY, ''

    def doReset(self):
        if self._connection:
            closeSocket(self._connection)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._connection.connect((self.host, self.port))

    def doShutdown(self):
        if self._connection:
            closeSocket(self._connection)
