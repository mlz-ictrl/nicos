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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""QMesyDAQ file writer classes."""

from __future__ import absolute_import, division, print_function

from os import path

from nicos.core import Attach, DataSinkHandler, Device, Override
from nicos.core.constants import POINT
from nicos.devices.datasinks import FileSink


def countdown(fn):
    dn, bn = path.dirname(fn), path.basename(fn)
    parts = bn.split('.', 1)
    bn = '%08d.%s' % (int(parts[0])-1, parts[1])
    return path.join(dn, bn)


class HistogramSinkHandler(DataSinkHandler):
    def prepare(self):
        self.manager.assignCounter(self.dataset)
        filepaths = self.manager.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        qmname = countdown(filepaths[0])
        self.sink._attached_timer._taco_update_resource('writehistogram', 'on')
        self.sink._attached_timer._taco_update_resource('lasthistfile', qmname)


class ListmodeSinkHandler(DataSinkHandler):
    def prepare(self):
        self.manager.assignCounter(self.dataset)
        filepaths = self.manager.getFilenames(self.dataset,
                                              self.sink.filenametemplate,
                                              self.sink.subdir)[1]
        qmname = countdown(filepaths[0])
        self.sink._attached_timer._taco_update_resource('writelistmode', 'on')
        self.sink._attached_timer._taco_update_resource('lastlistfile', qmname)
        limage = self.sink._attached_liveimage
        limage._dev.filename = filepaths[0]
        limage._dev.delay = self.sink._attached_tofchannel.delay * 100
        limage._dev.timeInterval = self.sink._attached_tofchannel.divisor * 100
        limage._dev.timeChannels = self.sink._attached_tofchannel.timechannels


class QMesyDAQSink(FileSink):
    attached_devices = {
        'timer': Attach('device to set the file name', Device),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT])
    }


class HistogramSink(QMesyDAQSink):
    handlerclass = HistogramSinkHandler


class ListmodeSink(QMesyDAQSink):
    handlerclass = ListmodeSinkHandler

    attached_devices = {
        'liveimage': Attach('device to set filename', Device),
        'tofchannel': Attach('device to get TOF settings', Device),
    }
