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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""QMesyDAQ related classes."""

from nicos.core import Attach, DataSinkHandler, Device, Override
from nicos.core.constants import POINT
from nicos.devices.datasinks import FileSink
from nicos.devices.entangle import CounterChannel


class HistogramSinkHandler(DataSinkHandler):
    def prepare(self):
        self.manager.assignCounter(self.dataset)
        filepaths = self.manager.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        qmname = filepaths[0]
        self.sink._attached_image._dev.SetProperties(['writehistogram', 'true'])
        self.sink._attached_image._dev.SetProperties(['lasthistfile', qmname])


class ListmodeSinkHandler(DataSinkHandler):
    def prepare(self):
        self.manager.assignCounter(self.dataset)
        filepaths = self.manager.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        qmname = filepaths[0]
        self.sink._attached_image._dev.SetProperties(['writelistmode', 'true'])
        self.sink._attached_image._dev.SetProperties(['lastlistfile', qmname])
        limage = self.sink._attached_liveimage
        if limage:
            limage._dev.filename = filepaths[0]
            limage._dev.delay = self.sink._attached_tofchannel.delay
            limage._dev.timeInterval = self.sink._attached_tofchannel.timeinterval
            limage._dev.timeChannels = self.sink._attached_tofchannel.timechannels


class QMesyDAQSink(FileSink):
    attached_devices = {
        'image': Attach('Device to set the file name', Device),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT])
    }


class HistogramSink(QMesyDAQSink):
    handlerclass = HistogramSinkHandler


class ListmodeSink(QMesyDAQSink):
    handlerclass = ListmodeSinkHandler

    attached_devices = {
        'liveimage': Attach('device to set filename', Device, optional=True),
        'tofchannel': Attach('device to get TOF settings', Device),
    }


class ImageCounterChannel(CounterChannel):
    """Counter channel that is based on an image on the Tango side."""

    def doRead(self, maxage=0):
        return self._dev.value.sum()
