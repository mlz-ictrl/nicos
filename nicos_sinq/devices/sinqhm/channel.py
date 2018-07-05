#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
import sys

from nicos.core import Param, Attach, status, oneof
from nicos.devices.generic import ImageChannelMixin, PassiveChannel
from nicos.pycompat import iteritems
from nicos_ess.devices.datasinks.imagesink.histogramdesc import \
    HistogramDimDesc, HistogramDesc
from nicos_sinq.devices.sinqhm.connector import HttpConnector
from nicos_sinq.devices.sinqhm.configurator import HistogramConfBank


class HistogramImageChannel(ImageChannelMixin, PassiveChannel):
    """Generic image channel to obtain histogram data from histogram
    memory.

    The data can either be returned as bytearray or it can be returned
    as a numpy array containing uint32 type counts. This behaviour
    can be changed using the parameter *readbytes*

    If the data being returned is in bytes, the endianness can be
    controlled using the parameter *databyteorder. The parameter
    *serverbyteorder* provides the byte order of the data received
    from the server.

    The bank in the server where the data is to be fetched from must
    be declared using the attached device *bank*. The attached device
    *connector* is used to talk to the HTTP server.

    NOTE:
    The data that comes out of the server is assumed to be of uint32
    type with 4 bytes.
    """
    parameters = {
        'serverbyteorder': Param('Endianness of the raw data (big/little)',
                                 type=oneof('big', 'little'),
                                 default='little'),
        'databyteorder': Param('Endianness of the data returned (big/little)',
                               type=oneof('big', 'little'),
                               default=sys.byteorder),
        'readbytes': Param('Read array in bytes (returns uint32 otherwise)',
                           type=bool, default=True)
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
        readtype = bytes if self.readbytes else int
        return HistogramDesc(self.name, readtype, self._dimDesc())

    def valueInfo(self):
        # no readresult -> no values
        return ()

    def _readFromServer(self):
        # Read the raw bytes from the server
        params = (('bank', self.bank.bankid), ('start', self.startid),
                  ('end', self.endid))
        req = self.connector.get('readhmdata.egi', params)
        return req.content

    def _getBytes(self):
        """ Get the bytes from the server in the order requested
        """
        raw = bytearray(self._readFromServer())
        if self.serverbyteorder != self.databyteorder:
            # Swap the endianness using 4 bytes
            self.log.debug('Swapping the endianness')
            raw[0::4], raw[1::4], raw[2::4], raw[3::4] = \
                raw[3::4], raw[2::4], raw[1::4], raw[0::4]
        return raw

    def _getData(self):
        """ Get the data formatted with uint32 numpy array
        """
        order = '<' if self.serverbyteorder == 'little' else '>'
        dt = numpy.dtype('uint32')
        dt = dt.newbyteorder(order)
        return numpy.frombuffer(self._readFromServer(), dt)

    def doReadArray(self, quality):
        return self._getBytes() if self.readbytes else self._getData()


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
        text_info = self._text_info()
        if int(text_info['DAQ']) == 1:
            return status.BUSY, 'Acquiring..'
        else:
            return status.OK, 'Ok'

    def doInfo(self):
        ret = []
        for item, val in iteritems(self._text_info()):
            ret.append((item, val, '%s' % val, '', 'general'))
        return ret
