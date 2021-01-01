#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

"""
This module contains the NICOS integration of the Attocube IDS 3010
interferometer.
"""

from time import time as currenttime

import requests
from numpy import cos, pi

from nicos import session
from nicos.core import SIMULATION, Attach, Device, HasCommunication, \
    Measurable, Moveable, Override, Param, Readable, status
from nicos.core.errors import CommunicationError
from nicos.core.params import ipv4, oneof


class JsonRpcClient:
    def __init__(self, url):
        self.url = url

    def call(self, method, args):
        payload = {
            'method': method,
            'params': list(args),
            'jsonrpc': '2.0',
            'id': 0,
        }
        try:
            response = requests.post(self.url, json=payload).json()
            if response['id'] != 0 or not response['jsonrpc']:
                raise CommunicationError('invalid reply')
            return response['result']
        except Exception as err:
            raise CommunicationError('RPC call error: %s' % err) from err


class IDS3010Server(HasCommunication, Device):
    """Handle communication to interferometer
    """

    parameters = {
        'ip': Param('IP address of interferometer',
                    default=ipv4('192.168.1.1'), type=ipv4, preinit=True),
    }

    def doPreinit(self, mode):
        if mode != SIMULATION:
            self._client = JsonRpcClient('http://%s:8080/api/json' % self.ip)
            self.log.info('Server Initialized')

    def communicate(self, attribute, *args):
        return self._com_retry(
            'jsonrpc call',
            lambda: self._client.call('com.attocube.ids.' + attribute, args))


class IDS3010Axis(Readable):
    """Read interferometer inputs
    """

    parameters = {
        'axis': Param('Index of the axis to be read', default=1, type=int),
        'absolute': Param('Absolute position value', type=float,
                          category='general', unit='um'),
    }

    parameter_overrides = {
        'unit': Override(default='um', mandatory=False, settable=False,
                         userparam=False),
    }

    attached_devices = {
        'server': Attach('Server for communication', IDS3010Server)
    }

    valuetype = float

    def doRead(self, maxage=0):
        return self._attached_server.communicate(
            'displacement.getAxisDisplacement', int(self.axis - 1))[1] * 1e-6

    def doReadAbsolute(self):
        return self._attached_server.communicate(
            'displacement.getAbsolutePosition', int(self.axis - 1))[1] * 1e-6

    def doStatus(self, maxage=0):
        mode = self._attached_server.communicate('system.getCurrentMode')[0]
        if mode == 'measurement running':
            return status.OK, 'Measuring'
        elif mode == 'measurement starting':
            return status.BUSY, 'Starting'
        else:
            return status.WARN, 'Off'

    def doReset(self):
        self._attached_server.communicate(
            'system.resetAxis', int(self.axis - 1))

    def doPoll(self, n, maxage=0):
        self._pollParam('absolute')


class IDS3010Control(Moveable):
    """Control interferometer measurement and alignment options.
    """

    _modes = {
        "system idle": status.OK,
        "measurement starting": status.BUSY,
        "measurement running": status.OK,
        "optics alignment starting": status.BUSY,
        "optics alignment running": status.OK,
        "pilot laser enabled": status.OK,
    }

    parameters = {
        'pilot': Param('Pilot laser for alignment', type=oneof('on', 'off'),
                       settable=True, category='general', chatty=True, ),
        'align': Param('Measure in alignment mode', type=oneof('on', 'off'),
                       settable=True, category='general', chatty=True, ),
        'contrast1': Param('Measure in alignment mode', type=float,
                           settable=False, category='general', chatty=True,
                           unit='%'),
        'contrast2': Param('Measure in alignment mode', type=float,
                           settable=False, category='general', chatty=True,
                           unit='%'),
        'contrast3': Param('Measure in alignment mode', type=float,
                           settable=False, category='general', chatty=True,
                           unit='%'),
    }

    parameter_overrides = {
        'unit': Override(default='', mandatory=False, settable=False,
                         userparam=False),
        'target': Override(userparam=False)
    }

    attached_devices = {
        'server': Attach('Server for communication', IDS3010Server)
    }

    valuetype = oneof('on', 'off')

    def doStatus(self, maxage=0):
        mode = self._attached_server.communicate('system.getCurrentMode')[0]
        return self._modes[mode], mode

    def doRead(self, maxage=0):
        return 'on' if self.status()[1] == "measurement running" else 'off'

    def doStart(self, value):
        self._attached_server.communicate('system.startMeasurement'
                                          if value == 'on' else
                                          'system.stopMeasurement')

    def doReadPilot(self):
        enabled = self._attached_server.communicate('pilotlaser.isEnabled')[0]
        return 'on' if enabled else 'off'

    def doWritePilot(self, value):
        self._attached_server.communicate('pilotlaser.enable' if value == 'on'
                                          else 'pilotlaser.disable')

    def doReadAlign(self):
        enabled = self._attached_server.communicate(
            'system.getCurrentMode')[0].startswith('optics alignment')
        return 'on' if enabled else 'off'

    def doWriteAlign(self, value):
        if (value == 'on' and
                self._attached_server.communicate(
                    'system.getCurrentMode')[0] == "system idle"):
            self._attached_server.communicate('system.startOpticsAlignment')
        else:
            self._attached_server.communicate('system.stopOpticsAlignment')

    def doReadContrast1(self):
        return self._attached_server.communicate(
            'adjustment.getContrastInPermille', 0)[1] * 0.1

    def doReadContrast2(self):
        return self._attached_server.communicate(
            'adjustment.getContrastInPermille', 1)[1] * 0.1

    def doReadContrast3(self):
        return self._attached_server.communicate(
            'adjustment.getContrastInPermille', 2)[1] * 0.1

    def doReset(self):
        self._attached_server.com.attocube.system.rebootSystem()

    def doPoll(self, n, maxage=0):
        # poll contrast values when in alignment mode
        if self.align=='on':
            self._pollParam('contrast1')
            self._pollParam('contrast2')
            self._pollParam('contrast3')


class MirrorDistance(Measurable):
    """
    Use geometric parameters to calculate mirror distance from the IDS measurement.
    """

    parameters = {
        'angle': Param('Index of the axis to be read', default=5.0, type=float,
                       settable=True),
        'offset': Param('Offset of device zero to hardware zero', unit='main',
                        settable=True, category='offsets', chatty=True,
                        fmtstr='main'),
    }

    parameter_overrides = {
        'unit': Override(default='um', mandatory=False, settable=False,
                         userparam=False),
    }

    attached_devices = {
        'axis': Attach('IDS Axis for the measurement', IDS3010Axis)
    }

    valuetype = float

    @property
    def axis(self):
        return self._attached_axis

    def doInit(self, mode):
        self._lastpreset = {'t': 1}
        self._counting_started = 0
        self._pause_time = 0

    def doRead(self, maxage=0):
        value = self.axis.doRead(maxage=maxage)
        return value * 0.5 * cos(self.angle / 360. * pi) + self.offset

    def doStatus(self, maxage=0):
        return self.axis.status()

    def doReset(self):
        self.axis.reset()

    def presetInfo(self):
        return ['t']

    def doSetPreset(self, **preset):
        if not preset:
            return  # keep previous settings
        self._lastpreset = preset

    def doStart(self):
        self._counting_started = currenttime()

    def doPause(self):
        self._pause_time = currenttime()
        return True

    def doResume(self):
        if self._pause_time:
            self._counting_started += (currenttime() - self._pause_time)
        return True

    def doFinish(self):
        self._counting_started = 0

    def doStop(self):
        self.doFinish()

    def doIsCompleted(self):
        return (currenttime() - self._counting_started) >= \
               self._lastpreset['t']

    def doWriteOffset(self, value):
        """Adapt the limits to the new offset."""
        old_offset = self.offset
        diff = value - old_offset

        # For movables, also adjust target to avoid getting value and
        # target out of sync
        if 'target' in self.parameters and self.target is not None:
            self._setROParam('target', self.target - diff)

        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value', self.doRead(0) - diff,
                            currenttime(), self.maxage)

        session.elogEvent('offset', (str(self), old_offset, value))
