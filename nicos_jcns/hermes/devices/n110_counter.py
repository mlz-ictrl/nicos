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
from io import TextIOWrapper
from time import time

import numpy

from nicos import session
from nicos.core.params import Value
from nicos.devices import entangle
from nicos.devices.datasinks import image


class TOFChannel(entangle.TOFChannel):
    """N110 TOFChannel, which returns the sum of all counts per channel as an
    array in `self.readresult` (instead of the sum of all counts of all
    channels).
    """

    def doReadArray(self, quality):
        narray = entangle.TOFChannel.doReadArray(self, quality)
        if narray.shape[1] > 1:
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
        tofcounter = session.getDevice(
            session.getDevice(self.sink.detectors[0])._attached_images[0])
        timer = session.getDevice(
            session.getDevice(self.sink.detectors[0])._attached_timers[0])
        textfp = TextIOWrapper(fp, encoding='utf-8')
        textfp.write(f'# HERMES N110 TOF data userid={exp.users},'
                     f'exp={exp.proposal},file={self.dataset.counter},'
                     f'sample={exp.sample.samplename}\n')
        started = datetime.fromtimestamp(self.dataset.started)
        finished = datetime.fromtimestamp(self.dataset.finished or time())
        textfp.write(f'# start: {started.strftime("%d.%m.%Y %H:%M:%S")}\n')
        textfp.write(f'# end: {finished.strftime("%d.%m.%Y %H:%M:%S")}\n')
        textfp.write(f'# timestamp: {self.dataset.started}\n')
        textfp.write(f'# bin number: {tofcounter.timechannels}\n')
        textfp.write(f'# bin width: {tofcounter.timeinterval * 1e-6} ms\n')
        textfp.write(f'# time: {timer.read(0)[0]:.1f} s\n')
        arr = numpy.asarray(image)
        textfp.write(f'# bin_time'
                     f'{" ".join(f"channel{x}" for x in range(len(arr)))}\n')
        for i in range(tofcounter.timechannels):
            textfp.write(f'{str((i + 1) * tofcounter.timeinterval * 1e-6):>10}'
                         f'{" ".join(f"{x:8d}" for x in arr[i])}\n')
        textfp.detach()


class ImageSink(image.ImageSink):
    """Image sink that uses the image sink handler for the HERMES N110 counter
    card."""

    handlerclass = SingleFileSinkHandler
