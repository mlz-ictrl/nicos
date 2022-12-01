#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

import time

import numpy

from nicos_ess.devices.datasinks.imagesink.histogramdesc import \
    HistogramDimDesc
from nicos_sinq.devices.sinqhm.channel import HistogramImageChannel


class ZebraChannel(HistogramImageChannel):
    """
    This class omits the empty TOF dimension at ZEBRA. Which in turn
    causes problems in data analysis. This makes the data stored to
    the NeXus file exactly like in SICS.
    """
    @property
    def shape(self):
        """ Shape of the data fetched. By default uses the
        shape of the bank, but the subclasses can override
        the shape.
        """
        return self.bank.shape[0:2]

    def _dimDesc(self):
        # This code removes the empty time binning axis at ZEBRA
        dims = []
        for ax in self.bank.axes:
            if ax.length > 1:
                dims.append(HistogramDimDesc(ax.length, ax.label, ax.unit,
                                             ax.bins))
        return dims

    def doReadBBArray(self, quality):
        if time.time() > self._dataTime + 3:
            order = '<' if self.connector.byteorder == 'little' else '>'
            dt = numpy.dtype('uint32')
            dt = dt.newbyteorder(order)

            # Read the raw bytes from the server
            params = (('bank', self.bank.bankid), ('start', self.startid),
                      ('end', self.endid))
            req = self.connector.get('readhmdata.egi', params)
            rawdata = numpy.frombuffer(req.content, dt)
            # Set the result and return data
            self.readresult = [int(sum(rawdata))]
            xdim = 256
            ydim = 128
            if len(rawdata) >= xdim * ydim:
                # do the magic zebra swap. The reasons for this lie in SINQ
                # history
                data = numpy.zeros((xdim * ydim), dtype='int32')
                for y in range(0, ydim):
                    for x in range(0, xdim):
                        val = rawdata[x * ydim + y]
                        data[y * xdim + x] = val
                data.reshape((xdim, ydim))
                self._data = data
            else:
                self._data = rawdata
            self._dataTime = time.time()
        return self._data

    def doReadF77Array(self, quality):
        """ Get the data formatted as uint32 numpy array

            It was noticed that NICOS was reading the array very frequently.
            So frequently, that storing a FOCUS file took three minutes.
            Other changes in nexussink which mitigated the problem. In addition
            this method was changed that it reads data only after a three
            seconds cache interval. This interval is reset both in doStart()
            and doFinish() in order to ensure good data always.
        """
        if time.time() > self._dataTime + 3:
            order = '<' if self.connector.byteorder == 'little' else '>'
            dt = numpy.dtype('uint32')
            dt = dt.newbyteorder(order)

            # Read the raw bytes from the server
            params = (('bank', self.bank.bankid), ('start', self.startid),
                      ('end', self.endid))
            req = self.connector.get('readhmdata.egi', params)
            data = numpy.frombuffer(req.content, dt)
            # Set the result and return data
            self.readresult = [int(sum(data))]
            if len(data) >= numpy.prod(self.shape):
                self._data = data.reshape(self.shape, order='F')
            else:
                self._data = data
            self._dataTime = time.time()
        return self._data
