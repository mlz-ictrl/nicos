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
#   Mark Koennecke, February 2020
#
# *****************************************************************************

import numpy as np

from nicos import session
from nicos.core.constants import FINAL
from nicos.core.device import Moveable
from nicos.core.params import Attach, Param, Value, oneof, tupleof
from nicos.core.status import BUSY, OK
from nicos.core.utils import usermethod
from nicos.devices.generic import ActiveChannel, ImageChannelMixin

from nicos_ess.devices.datasinks.imagesink.histogramdesc import \
    HistogramDesc, HistogramDimDesc
from nicos_sinq.devices.sinqhm.connector import HttpConnector


class CCDWWWConnector(HttpConnector):
    """
    Just a HTTP connector without authentication
    """
    def _get_auth(self):
        return ''

    def doInit(self, mode):
        # ccdwww hangs up on the doInit() in HttpConnector
        pass


class CCDWWWImageChannel(ImageChannelMixin, ActiveChannel):
    """
    This is an ImageChannel which communicates with the CCDWWW
    http based CCD server.
    """
    # Parameters which need to be considered for configuration
    _config_list = []
    iscontroller = True

    attached_devices = {
        'connector': Attach('The connector to the CCDWWW HTTP server',
                            CCDWWWConnector),
    }

    parameters = {
        'shape': Param('Shape of the image to expect',
                       tupleof(int, int),
                       settable=True,
                       userparam=True),
    }

    _isExposing = False
    _data = None
    _readData = False

    def doStart(self):
        params = {'time': str(self.preselection)}
        self.readresult = [0]
        # No result to HTTP GET expected
        self.connector.get('expose', params)
        self._isExposing = True
        self._readData = True

    def doStop(self):
        # No result to HTTP GET expected
        self.connector.get('interrupt')

    def doFinish(self):
        # No result to HTTP GET expected
        self.connector.get('interrupt')

    def presetInfo(self):
        return ['t', ]

    def doStatus(self, maxage=0):
        conn_status = self.connector.status(maxage)
        if conn_status[0] != OK:
            return conn_status
        stat = self.connector.get('locked')
        if stat == 1:
            return BUSY, 'Counting'
        self._isExposing = False
        return OK, 'Idle'

    def doReadArray(self, quality):
        if quality == FINAL and not self._isExposing and self._readData:
            # Read the raw bytes from the server
            # session.log.info('Reading CCD data.. \n')
            req = self.connector.get('data')
            order = '<' if self.connector.byteorder == 'little' else '>'
            dt = np.dtype('uint32')
            dt = dt.newbyteorder(order)
            data = np.frombuffer(req.content, dt)
            # Set the result and return data
            self.readresult = [int(sum(data))]
            self._data = data.reshape(self.shape)
            self._readData = False
        return self._data

    @usermethod
    def configure(self):
        # The XML digested by ccdwww is not very standard in that there
        # is no root, thus manual generation
        xml = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n'
        for par in self._config_list:
            xml += '<%s>%s</%s>\n' % (par, str(getattr(self, par)), par)
        self.connector.post('configure', data=xml)

    @property
    def connector(self):
        return self._attached_connector

    def _dimDesc(self):
        # Provides a description of dimensions in the histogram
        return [HistogramDimDesc(self.shape[0], 'x', 'pixel', None),
                HistogramDimDesc(self.shape[1], 'y', 'pixel', None)]

    @property
    def arraydesc(self):
        return HistogramDesc(self.name, 'uint32', self._dimDesc())

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]


class AndorCCD(CCDWWWImageChannel):
    """
    Class for the acutual ANDOR CCD. Just adds the many parameters
    to CCDWWWImageChannel
    """
    parameters = {
        'daqmode': Param('Data acquisition mode',
                         str, default='single'),
        'accucycle': Param('Cyling time during accumulation',
                           int, settable=True, default=20),
        'accucounts': Param('Accumulation count',
                            int, settable=True, default=5),
        'triggermode': Param('Camera trigger mode',
                             int, default=7, settable=True),
        'imagepar': Param('Image configuration',
                          str, default='1 1 1 1024 1 1025',
                          settable=True),
        'shutterlevel': Param('Level for opening shutter',
                              oneof(0, 1), default=0,
                              settable=True),
        'shuttermode': Param('Shutter mode',
                             oneof(0, 1, 2), default=0,
                             settable=True),
        'openingtime': Param('Shutter opening time',
                             int, default=20, settable=True),
        'closingtime': Param('Shutter closing time',
                             int, default=20, settable=True),
        'flip': Param('Image flipping configuration',
                      str, default='1 1', settable=True),
        'rotate': Param('Image rotation',
                        int, default=0, settable=True),
        'hspeed': Param('horizontal reading speed',
                        int, default=2, settable=True),
        'vspeed': Param('Vertical reading speed',
                        int, default=0, settable=True),
        'vamp': Param('Read out amplitude',
                      int, default=1, settable=True),
        'writetiff': Param('Flag if the ccdwww writes a tiff file',
                           oneof(0, 1), default=0, settable=True)
    }
    _config_list = ['daqmode', 'accucycle', 'accucounts', 'triggermode',
                    'imagepar', 'shutterlevel', 'shuttermode',
                    'openingtime', 'closingtime',
                    'flip', 'rotate', 'hspeed', 'vspeed', 'vamp',
                    'writetiff']

    def doStart(self):
        # This code figures out the current filename and point number
        cur = session.experiment.data._current
        if cur.filenames:
            filename = cur.filenames[0]
            np = 0
        else:
            scan = session.experiment.data.getLastScans()[-1]
            filename = scan.filenames[0]
            np = cur.number
        # This creates the tiff image file name on ccdwww
        filename = 'images/%s.%4.4d.tif' % (filename, np)
        params = {'time': str(self.preselection),
                  'filename': filename, 'NP': np}
        self.readresult = [0]
        # No result to HTTP GET expected
        self.connector.get('expose', params)
        self._isExposing = True
        self._readData = True

    def presetInfo(self):
        if int(self.triggermode) == 7:
            return ['t', 'm']
        return ['t', ]


class CCDCooler(Moveable):
    """
    This class controls the temperature of the CCD camera.
    """
    valuetype = oneof('on', 'off')
    _target = None

    attached_devices = {
        'connector': Attach('The connector to the CCDWWW HTTP server',
                            CCDWWWConnector),
    }

    parameters = {
        'temperature': Param('Actual temperature reading',
                             float, unit='C', volatile=True),
    }

    def doInit(self, mode):
        self._target = self.read(0)

    @property
    def connector(self):
        return self._attached_connector

    def doStart(self, target):
        param = {'status': target}
        # No result to HTTP GET expected
        self.connector.get('cooling', param)
        self._target = target

    def doRead(self, maxage=0):
        req = self.connector.get('iscooling')
        if int(req.content) == 1:
            return 'on'
        return 'off'

    def doReadTemperature(self):
        req = self.connector.get('temperature')
        return float(req.content)

    def doStatus(self, maxage=0):
        if self.read(0) == self._target:
            return OK, ''
        return BUSY, 'Switching'
