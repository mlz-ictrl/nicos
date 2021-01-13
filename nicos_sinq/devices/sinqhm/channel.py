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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import numpy

from nicos.core import Attach, Override, Param, Value, dictof, status
from nicos.devices.generic import ImageChannelMixin, PassiveChannel

from nicos_ess.devices.datasinks.imagesink.histogramdesc import HistogramDesc, \
    HistogramDimDesc
from nicos_sinq.devices.sinqhm.configurator import HistogramConfBank
from nicos_sinq.devices.sinqhm.connector import HttpConnector


class HistogramImageChannel(ImageChannelMixin, PassiveChannel):
    """Generic image channel to obtain histogram data from histogram
    memory.

    The data is returned as a numpy array containing uint32 type counts.

    The bank in the server where the data is to be fetched from must
    be declared using the attached device *bank*. The attached device
    *connector* is used to talk to the HTTP server.

    NOTE:
    The data that comes out of the server is assumed to be of uint32
    type with 4 bytes.
    """

    parameter_overrides = {
        'fmtstr': Override(default='%d', userparam=False)
    }

    attached_devices = {
        'bank': Attach('The bank to be used for fetching the data',
                       HistogramConfBank),
        'connector': Attach('HTTP Connector for Histogram Memory Server',
                            HttpConnector),
    }

    @property
    def bank(self):
        return self._attached_bank

    @property
    def connector(self):
        return self._attached_connector

    @property
    def startid(self):
        """ The start id of the data to be fetched from the bank.
        This method should be overridden if the starting index is
        not 0.
        """
        return 0

    @property
    def endid(self):
        """ The end id of the data to be fetched from the bank.
        By default uses the full banks capacity, but can be
        overridden in case a smaller range is required
        """
        return numpy.prod(self.shape)

    @property
    def shape(self):
        """ Shape of the data fetched. By default uses the
        shape of the bank, but the subclasses can override
        the shape.
        """
        return self.bank.shape

    def _dimDesc(self):
        # Provides a description of dimensions in the histogram
        return [HistogramDimDesc(ax.length, ax.label, ax.unit, ax.bins)
                for ax in self.bank.axes]

    @property
    def arraydesc(self):
        return HistogramDesc(self.name, 'uint32', self._dimDesc())

    def valueInfo(self):
        return [Value(self.name, type='counter', unit=self.unit)]

    def doStart(self):
        self.readresult = [0]

    def doReadArray(self, quality):
        """ Get the data formatted with uint32 numpy array
        """
        order = '<' if self.connector.byteorder == 'little' else '>'
        dt = numpy.dtype('uint32')
        dt = dt.newbyteorder(order)

        # Read the raw bytes from the server
        params = (('bank', self.bank.bankid), ('start', self.startid),
                  ('end', self.endid()))
        req = self.connector.get('readhmdata.egi', params)
        data = numpy.frombuffer(req.content, dt)
        # Set the result and return data
        self.readresult = [int(sum(data))]
        return data

    def doStatus(self, maxage=0):
        return self.connector.status(maxage)


class ReshapeHistogramImageChannel(HistogramImageChannel):
    """
    An image channel which can reshape the data. This is sometimes necessary.
    """

    parameters = {
        'dimensions': Param('Desired shape of the data',
                            type=dictof(str, int),
                            ),
    }

    _shape = None
    _HM_dim_desc = None

    def doInit(self, mode):
        self._shape = tuple(self.dimensions.values())
        res = []
        for name, dim in self.dimensions.items():
            res.append(HistogramDimDesc(dim, name, ''))
        self._HM_dim_desc = res

    def doReadArray(self, quality):
        data = HistogramImageChannel.doReadArray(self, quality)
        if len(data) >= numpy.prod(self.shape):
            return data.reshape(self.shape)
        return data

    @property
    def shape(self):
        return self._shape

    def _dimDesc(self):
        return self._HM_dim_desc


class HistogramMemoryChannel(PassiveChannel):
    """ Channel which configures the histogram memory start and stop.

    For staring and stopping data acquisition the following paths
    are to be used:
    startdaq.egi initializes the histogram memory data and
        eventual counters to zero and starts data acquisition.
    stopdaq.egi stops data acquisition.
    pausedaq.egi pauses data acquisition. The data in the histogram
        memory is not modified.
    continuedaq.egi continues a paused data acquisition.

    The attached *connector* is used to talk to the server
    """
    attached_devices = {
        'connector': Attach('HTTP Connector for Histogram Memory Server',
                            HttpConnector),
    }

    parameter_overrides = {
        'fmtstr': Override(default='', userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False),
        'unit': Override(userparam=False)
    }

    @property
    def connector(self):
        return self._attached_connector

    def _text_info(self):
        # Get the text information from the server
        req = self.connector.get('textstatus.egi')
        textinfo = {}
        for entry in req.text.split('\n'):
            vals = str(entry).split(':')
            if len(vals) > 1:
                key = vals[0]
                val = ':'.join(vals[1:])
                if key:
                    textinfo[key] = val
        return textinfo

    def doRead(self, maxage=0):
        # No need to return the arrays back. Not required.
        return []

    def valueInfo(self):
        return ()

    def doStart(self):
        self.connector.get('startdaq.egi')

    def doStop(self):
        self.connector.get('stopdaq.egi')

    def doPause(self):
        self.connector.get('pausedaq.egi')

    def doResume(self):
        self.connector.get('continuedaq.egi')

    def doFinish(self):
        self.connector.get('stopdaq.egi')

    def doStatus(self, maxage=0):
        conn_status = self._attached_connector.status(maxage)
        if conn_status[0] != status.OK:
            return conn_status

        text_info = self._text_info()
        if int(text_info['DAQ']) == 1:
            return status.BUSY, 'Acquiring..'

        return status.OK, ''

    def doInfo(self):
        ret = []
        for item, val in self._text_info().items():
            ret.append((item, val, '%s' % val, '', 'general'))
        return ret
