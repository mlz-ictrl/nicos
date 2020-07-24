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
#   Michael Wedel <michael.wedel@esss.se>
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from lewis.core.control_client import ControlClient

from nicos import session
from nicos.core import POLLER, SIMULATION, ConfigurationError, \
    DeviceMixinBase, Override, Param, Value, host, status
from nicos.devices.generic import ActiveChannel, CounterChannelMixin, \
    Detector, PassiveChannel, TimerChannelMixin


class LewisControlClientDevice(DeviceMixinBase):
    parameters = {
        'host': Param('HOST:PORT string for JSON-RPC connection.',
                      type=host, settable=False, mandatory=True),
        'remoteobj': Param('Name of remote object to mirror.',
                           type=str, settable=False, mandatory=True,
                           userparam=False)
    }

    _client = None
    _obj = None

    def doPreinit(self, mode):
        if mode != SIMULATION:
            host, port = self.host.split(':')
            self._client = ControlClient(host, port)
            remote_objects = self._client.get_object_collection()

            if self.remoteobj not in remote_objects.keys():
                raise ConfigurationError('No such object on {}: {}'.format(
                    self.host, self.remoteobj))

            self._obj = remote_objects[self.remoteobj]


class TsDauChannelBase(LewisControlClientDevice):
    def doStatus(self, maxage=0):
        raw_status = self._obj.status

        if raw_status == 'busy':
            return status.BUSY, 'Counting'

        if raw_status in ('ready', 'off'):
            return status.OK, 'Idle'

        return status.ERROR, 'Device is offline.'


class TsDauTimeChannel(TsDauChannelBase, TimerChannelMixin, ActiveChannel):
    parameter_overrides = {
        'ismain': Override(default=True),
        'preselection': Override(type=int)
    }

    def doInit(self, mode):
        if mode != SIMULATION and session.sessiontype != POLLER:
            self._obj.do_init()

    def doRead(self, maxage=0):
        self.log.info('reading %s', session.sessiontype == POLLER)
        return self._obj.elapsed_time

    def doStart(self):
        self.log.info('Starting timer')
        self._obj.preset_time = self.preselection
        self._obj.do_record()

    def doStop(self):
        self._obj.do_cancel()

    def doFinish(self):
        self._obj.do_save()


class TsDauCounterChannel(TsDauChannelBase, CounterChannelMixin, PassiveChannel):
    def doRead(self, maxage=0):
        return self._obj.counts


class TsDauFilenameChannel(TsDauChannelBase, ActiveChannel):
    parameters = {
        'directory': Param('Directory for files', type=str, default=''),
    }

    parameter_overrides = {
        'preselection': Override(type=str)
    }

    def valueInfo(self):
        return Value(self.name, type='filename', fmtstr='%s'),

    def doWritePreselection(self, new_val):
        self._obj.filename = self.directory + new_val
        self._params['preselection'] = new_val

    def doStart(self):
        self.log.info('Starting filename')

    def doRead(self, maxage=0):
        return self._obj.filename


class TsDauDetector(Detector):
    def _presetiter(self):
        for i in Detector._presetiter(self):
            yield i

        for dev in self._attached_others:
            if isinstance(dev, TsDauFilenameChannel):
                yield ('f', dev)
