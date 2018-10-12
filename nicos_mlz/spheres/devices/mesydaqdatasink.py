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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

'''
Datasink and handler for QMesydaq on Spheres.
Writes the data so it can be read by frida.
'''

from __future__ import absolute_import

from time import localtime, strftime

import numpy

from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.datasinks.special import LiveViewSink, LiveViewSinkHandler


class SpheresMesydaqHandler(SingleFileSinkHandler):
    defer_file_creation = True

    def __init__(self, sink, dataset, detector):
        SingleFileSinkHandler.__init__(self, sink, dataset, detector)

        self._resetMeta()

    def writeData(self, fp, image):
        j = 0
        for i in range(len(image)):
            fp.write('\n  %s\n' % i)
            tube = image[i]
            for entry in tube:
                fp.write('%s%s\n' % (str(j).ljust(5, ' '), entry))
                j += 1

    def putResults(self, quality, results):
        if self.detector.name in results:
            self.counts = results[self.detector.name][0][2]
            self.scanduration = results[self.detector.name][0][0]
        return SingleFileSinkHandler.putResults(self, quality, results)

    def writeHeader(self, fp, metainfo, image):
        header = ''
        header += '# events = %d\n' % self.counts
        header += '# timer = %dms\n' % (self.scanduration * 1000)
        header += strftime('# date = %d.%m.%Y  %H:%M:%S\n', localtime())

        timer = self.detector._attached_timers[0]

        header += '# histfile = %s\n' % timer.getLastListModeFile()
        header += '# listfile = %s\n' % timer.getLastHistModeFile()

        fp.write(header)

        self._resetMeta()

    def _resetMeta(self):
        self.counts = None
        self.scanduration = None
        self.creation = None


class SpheresMesydaqLiveViewSinkHandler(LiveViewSinkHandler):
    def __init__(self, sink, dataset, detector):
        LiveViewSinkHandler.__init__(self, sink, dataset, detector)

    def extractData(self,result, quality):
        return [numpy.concatenate(result[1][0])]


class SpheresMesydaqImageSink(ImageSink):
    handlerclass = SpheresMesydaqHandler


class SpheresMesydaqLiveViewSink(LiveViewSink):
    handlerclass = SpheresMesydaqLiveViewSinkHandler
