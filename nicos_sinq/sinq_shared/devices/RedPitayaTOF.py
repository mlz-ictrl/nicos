# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Andrea Plank <andrea.plank@psi.ch>
#
# *****************************************************************************
import time
import numpy
import re

from nicos.core import Attach, ArrayDesc, Override, Param, \
    Value, floatrange, oneof, status
from nicos.devices.generic import ImageChannelMixin, PassiveChannel
from nicos_sinq.devices.sinqhm.connector import HttpConnector


class TofHistogramChannel(ImageChannelMixin, PassiveChannel):
    """
    Histogramm channel to read uint32 bytes from RedPitaya Server
    """
    parameters = {
        'channel': Param('Channel preset',
                          type = str, mandatory=True),
        'histtype': Param('Histogramtype (tof or pulseheight)',
                          type = oneof('tof', 'pulseheight'), mandatory=True),
        'update_interval': Param('Update interval for cached data in seconds',
                          type = floatrange(0, 60),
                          settable = False, userparam = False,
                          default = 3),
    }

    attached_devices = {
        'connector': Attach('HTTP Connector', HttpConnector),
    }

    parameter_overrides = {
        'unit': Override(default='counts'),
        'fmtstr': Override(default='%d', userparam=False),
    }

    def doInit(self, mode):
        self._dataTime = 0
        self._data = None
        self._active = None
        self._nbins = 4096

    def _channel_info(self):
        req = self.connector.get(
            'channelinfo',
             params = (('channel', self.channel),
                               ('histtype', self.histtype))
        )
        return req.json()

    @property
    def connector(self):
        return self._attached_connector

    @property
    def startid(self):
        return 0

    @property
    def endid(self):
        # Reads nbins from server
        if time.time() > self._dataTime + self.update_interval:
            try:
                self._nbins = self._channel_info()['nbins']
            except Exception as e:
                self.log.warning('Using old value, since nbins could not be read from server: %s', e)
        return self._nbins

    @property
    def shape(self):
        return (self.endid,)

    @property
    def arraydesc(self):
        if self.histtype == 'tof':
            dimnames = [f'{self.channel} TOF Bins', 'Counts']
        else:
            dimnames = [f'{self.channel} Pulse Height Bin', 'Counts']
        return ArrayDesc(self.name, shape = self.shape, dtype = numpy.uint32, dimnames = dimnames)

    def valueInfo(self):
        return (Value(self.name, type='counter', unit='counts'),)

    def doStart(self):
        self.readresult = [0]
        self._dataTime = 0
        try:
            data = self._channel_info()
            self._active = data['selected']
            self._nbins = data['nbins']
        except Exception as e:
            self.log.error('Could not read channelinfo: %s', e)

    def doFinish(self):
        self._dataTime = 0
        self._active = None

    def doReadArray(self, quality):
        if not self._active and self._data is None:
            return numpy.zeros(self.endid, dtype=numpy.uint32)

        if time.time() > self._dataTime + self.update_interval:
            order = '<' if self.connector.byteorder == 'little' else '>'
            dt = numpy.dtype('uint32').newbyteorder(order)

            params = (('channel', self.channel),
                      ('histtype', self.histtype),
                      ('start', self.startid),
                      ('end', self.endid))
            req = self.connector.get('readtofdata', params)
            data = numpy.frombuffer(req.content, dt)

            self.readresult = [int(sum(data))]
            if len(data) >= numpy.prod(self.shape):
                self._data = data.reshape(self.shape, order='C')
            else:
                self._data = data
            self._dataTime = time.time()
        return self._data

    def doStatus(self, maxage=0):
        return self.connector.status(maxage)


class TofTOFChannel(TofHistogramChannel):

    parameters = {
        'nbins': Param('Number of TOF Bins',
            type = oneof(1024, 2048, 4096, 8192),
            settable = True, userparam = True,
            unit = 'bins', volatile = True ),
        'binsize': Param('Binsize in us',
            type = floatrange(0.008, 10000),
            settable = True, userparam = True,
            unit = 'us', volatile = True),
        'frameoverlap': Param('Enable or Disable Frameoverlap',
            type = bool,
            settable = True, userparam = True,
            unit = '', volatile = True),
    }

    def doReadNbins(self):
        req = self.connector.get('getparam', params = (('parameter', f'{self.channel}_{self.histtype}_nchannels'),))
        return int(req.json()['value'])

    def doWriteNbins(self, value):
        self.connector.post('setparam', data = {'parameter': f'{self.channel}_{self.histtype}_nchannels', 'value': int(value)})
        return int(value)

    def doReadBinsize(self):
        req = self.connector.get('getparam', params = (('parameter', f'{self.channel}_{self.histtype}_binsize'),))
        return float(req.json()['value'])

    def doWriteBinsize(self, value):
        self.connector.post('setparam', data = {'parameter': f'{self.channel}_{self.histtype}_binsize', 'value': float(value)})
        return float(value)

    def doReadFrameoverlap(self):
        req = self.connector.get('getparam', params = (('parameter', f'{self.channel}_frameoverlap'),))
        return bool(req.json()['value'])

    def doWriteFrameoverlap(self, value):
        self.connector.post('setparam', data = {'parameter': f'{self.channel}_frameoverlap','value': int(value)})
        return bool(value)


class TofPulseheightChannel(TofHistogramChannel):

    parameters = {
        'nbins': Param('Number of Pulseheight Bins',
            type = oneof(512, 1024, 2048, 4096),
            settable = True, userparam = True,
            unit = 'bins', volatile = True ),
    }

    def doReadNbins(self):
        req = self.connector.get('getparam', params = (('parameter', f'{self.channel}_{self.histtype}_nchannels'),))
        return int(req.json()['value'])

    def doWriteNbins(self, value):
        self.connector.post('setparam', data = {'parameter': f'{self.channel}_{self.histtype}_nchannels','value': int(value)})
        return int(value)


class TofDaqController(PassiveChannel):
    """
    Controls start/stop of RedPitaya DAQ
    """

    attached_devices = {
        'connector': Attach('HTTP Connector', HttpConnector),
    }

    parameter_overrides = {
        'unit': Override(default='', userparam=False),
        'fmtstr': Override(default='', userparam=False),
        'warnlimits': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'maxage': Override(userparam=False),
    }

    @property
    def connector(self):
        return self._attached_connector

    def doRead(self, maxage=0):
        return []

    def valueInfo(self):
        return ()

    def doStart(self):
        self.connector.get('startdaq')

    def doStop(self):
        self.connector.get('stopdaq')

    def doPause(self):
        self.connector.get('pausedaq')
        return True

    def doResume(self):
        self.connector.get('continuedaq')

    def doFinish(self):
        self.connector.get('stopdaq')

    def doStatus(self, maxage=0):
        try:
            req = self.connector.get('textstatus')
            if re.search(r'^DAQ:\s*1\s*$', req.text, re.MULTILINE):
                return status.BUSY, 'Acquiring'
            return status.OK, ''
        except Exception as e:
            return status.ERROR, str(e)
