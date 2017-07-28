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
#   Michael Wedel <michael.wedel@esss.se>
#
# *****************************************************************************

from nicos.devices.generic import ActiveChannel
from nicos.core import Param, host, status, Value, POLLER, Override
from nicos import session
import socket


class PixelmanUDPChannel(ActiveChannel):
    """
    Trigger detector controlled by Pixelman software via UDP service

    One of the detectors at V20 can be triggered through a simple UDP
    service which listens on the computer that controls the detector.
    It expects a keyword to start acquisition and then sends a keyword
    back once it's done. The service expects a new connection for each
    data acquisition, so the connection is established in the doStart
    method and removed in doFinish. In order to recover from
    inconsistent states, the socket is also torn down in doStop,
    although that won't stop the detector, just reset the connection.

    At the moment it's not possible to obtain count information from
    the service, but that may change in the future.
    """

    parameters = {
        'host': Param('IP and port for Pixelman Detector UDP interface.',
                      type=host),
        'acquire': Param('Keyword to send for starting the acquisition',
                         type=str),
        'finished': Param('Keyword to wait for to determine '
                          'whether the acquisition is done', type=str),
        'acquiring': Param('Internal parameter to synchronise between processes.',
                           type=bool, userparam=False, default=False, mandatory=False,
                           settable=False)
    }

    parameter_overrides = {
        'ismaster': Override(default=True, settable=False)
    }

    def valueInfo(self):
        return Value(self.name, unit=self.unit, type='other', fmtstr=self.fmtstr),

    def doInit(self, mode):
        self._socket = None

    def doStart(self):
        if self._socket is None:
            self.log.debug('Socket is None, creating socket.')
            pm_host, pm_port = self.host.split(':')
            self.log.debug('Connection: ' + self.host)
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.connect((pm_host, int(pm_port)))
            self.log.debug('Sending Keyword: ' + self.acquire)
            self._socket.sendall(self.acquire)
            self._socket.setblocking(0)

            self._setROParam('acquiring', True)

            self.log.debug('Acquisition started')
        else:
            self.log.info('Socket already exists, starting again has no effect.')

    def doFinish(self):
        self.log.debug('Finishing...')
        if self._socket is not None:
            self.log.debug('Actually shutting down...')
            self._socket.close()
            self._socket = None

        self._setROParam('acquiring', False)

    def doRead(self, maxage=0):
        return 0

    def doStop(self):
        self.doFinish()

    def doStatus(self, maxage=0):
        if not self._check_complete():
            return status.BUSY, 'Acquiring...'

        return status.OK, 'Idle'

    def duringMeasureHook(self, elapsed):
        return None

    def _check_complete(self):
        self.log.debug('Checking completion...')

        if session.sessiontype != POLLER:
            if self._socket is not None:
                self.log.debug('Actually performing check...')
                try:
                    data = self._socket.recv(1024)

                    self.log.debug('Got data: ' + data)

                    return data == self.finished
                except socket.error:
                    return False

        self.log.debug('Falling back to Cache...')

        return not self.acquiring
