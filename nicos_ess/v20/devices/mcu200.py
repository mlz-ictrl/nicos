#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import socket
from time import sleep

from nicos.core import ADMIN, CommunicationError, HasPrecision, Override, \
    Param, host, requires, status
from nicos.devices.abstract import Motor

STATUS_MAP = {
    -6: (status.WARN, 'Aborting movement.'),
    -5: (status.ERROR, 'Axis is deactivated.'),
    -4: (status.ERROR, 'Hardware stop activated.'),
    -3: (status.ERROR, 'Motor is inhibited.'),
    0: (status.OK, 'Ready for movement.'),
    5: (status.BUSY, 'Moving to target.')
}


class MCU200Motor(Motor):
    parameters = {
        'host': Param('IP and port of the motor controller.', type=host),
        'index': Param('Motor number', type=int),
    }

    parameter_overrides = {
        'speed': Override(volatile=True, settable=False),
    }

    def doRead(self, maxage=0):
        return float(self._send_command('Q', '10'))

    def doStatus(self, maxage=0):
        devstatus = int(self._send_command('P', '00'))

        return STATUS_MAP.get(devstatus,
                              (status.UNKNOWN,
                               'Unknown device status: {}'.format(devstatus)))

    def doStart(self, pos):
        self._send_command('Q', '01={}'.format(pos))
        self._send_command('M', '=1')

    def doStop(self):
        self._send_command('M', '=8')

    @requires(level=ADMIN)
    def doReference(self):
        self._send_command('M', '=9')

    def doReadSpeed(self):
        return float(self._send_command('Q', '04'))

    def doReset(self):
        self._send_command('M', '14=0')
        self._send_command('M', '14=1')

    def doIsAtTarget(self, pos):
        return (int(self._send_command('P', '00')) == 0
                and HasPrecision.doIsAtTarget(self, pos))

    def doFinish(self):
        pos = self.read(0)
        if not self.isAtTarget(pos):
            if self.isInRetry():
                self.log.error('Moving to 0 during retry did not work. '
                               'Resetting retry status, continuing.')
            else:
                self._retry()

            self._set_retry(False)

    def _retry(self):
        self._set_retry(True)
        self.log.warning('Did not reach target on first try. '
                         'Moving back to 0 and trying again.')
        old_target = float(self.target)
        self.maw(0)
        self.maw(old_target)

    def _set_retry(self, value):
        self._cache.put(self, 'inretry', value)

    def isInRetry(self):
        return self._cache.get(self, 'inretry', False)

    def _send_command(self, prefix, command, retry=None):
        try:
            # Connect once for each request to avoid problems with overlapping
            # commands/responses to/from the Serial->Ethernet device.
            ip, port = self.host.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, int(port)))

            message = '{}{}{}\r'.format(prefix, self.index, command)
            self.log.debug('Sending message: ' + message)
            sock.send(message)
            self.log.debug('Message sent, waiting for reply')
            reply = sock.recv(1024)
            self.log.debug('Got reply: ' + str(len(reply)) + ' ' + str(reply))
            sock.close()
            try:
                if reply.endswith('\x06'):
                    return reply[:-1]
                return reply
            except TypeError:
                return None
        except socket.error:
            if retry is not None:
                self.log.debug('Retry unsuccessful, raising error.')
                raise CommunicationError('Communication error with device.')

            self.log.debug('Socket error, retrying after 0.1 second sleep.')
            sleep(0.1)
            return self._send_command(prefix, command, True)
