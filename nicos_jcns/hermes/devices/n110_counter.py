#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

from datetime import datetime
from time import time

import numpy

from nicos import session
from nicos.core.params import Value
from nicos.devices import entangle
from nicos.devices.datasinks import image


class TOFChannel(entangle.TOFChannel):

    def doReadArray(self, quality):
        narray = entangle.TOFChannel.doReadArray(self, quality)
        # sum all counts per time channel if more than one was configured
        if self.doReadTimechannels() > 1:
            self.readresult = list(numpy.sum(narray, axis=0))
        return narray

    def valueInfo(self):
        return tuple(Value(name=f'{self.name}[{i}]', type='counter',
                           fmtstr='%d', errors='sqrt', unit='cts')
                     for i in range(len(self.readresult)))


class SingleFileSinkHandler(image.SingleFileSinkHandler):
    """Single file sink handler to use when measuring with the HERMES N110
    counter card that writes its count values to a data file.
    """

    def writeData(self, fp, image):
        exp = session.experiment
        tofcounter = session.getDevice('tofcounter')
        fp.write(f'# HERMES N110 TOF data userid={exp.users},'
                 f'exp={exp.proposal},file={self.dataset.counter},'
                 f'sample={exp.sample.samplename}\n'.encode('utf-8'))
        started = datetime.fromtimestamp(self.dataset.started)
        finished = datetime.fromtimestamp(self.dataset.finished or time())
        fp.write(f'# start: {started.strftime("%d.%m.%Y %H:%M:%S")}'
                 f'\n'.encode('utf-8'))
        fp.write(f'# end: {finished.strftime("%d.%m.%Y %H:%M:%S")}'
                 f'\n'.encode('utf-8'))
        fp.write(f'# timestamp: {self.dataset.started}\n'.encode('utf-8'))
        fp.write(f'# bin number: {tofcounter.timechannels}\n'.encode('utf-8'))
        fp.write(f'# bin width: {tofcounter.timeinterval * 1e-6} ms'
                 f'\n'.encode('utf-8'))
        fp.write(f'# time: {session.getDevice("timer").read(0)[0]:.1f} s'
                 f'\n'.encode('utf-8'))
        fp.write(f'# refresh time: ???\n'.encode('utf-8'))  # TODO
        fp.write('# bin_time channel0 channel1 channel2 channel3 '
                 'channel4\n'.encode('utf-8'))
        arr = numpy.asarray(image)
        for i in range(tofcounter.timechannels):
            fp.write(f'{str((i + 1) * tofcounter.timeinterval * 1e-6):>10}'
                     f'{" ".join(f"{x:8d}" for x in arr[i])}\n'.encode('utf-8'))
        fp.flush()


class ImageSink(image.ImageSink):
    """Image sink that uses the image sink handler for the HERMES N110 counter
    card."""

    handlerclass = SingleFileSinkHandler
