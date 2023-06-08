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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

from numpy import arange, arctan, array, rad2deg as deg

from nicos.core import ArrayDesc, Attach, Readable
from nicos.core.params import Param, Value
from nicos.devices.generic.detector import ActiveChannel, ImageChannelMixin


class Detector(ImageChannelMixin, ActiveChannel):

    attached_devices = {
        'det': Attach('Underlying pixel detector (1 dim)', ActiveChannel),
        # 'ttheta': Attach('2Theta axis encoder', Readable)
    }

    parameters = {
        'radius': Param('Distance detector to the goniometer center (in mm)',
                        type=float, volatile=False, settable=False),
        'pixel_size': Param('Size of a single pixel (in mm)',
                            type=float, volatile=False, settable=False,
                            category='instrument'),
        'pixel_count': Param('Number of detector pixels',
                             type=int, volatile=False, settable=False,
                             default=1280, category='instrument'),
    }

    def doInit(self, mode):
        self._attached_det.doInit(mode)
        # self.arraydesc = ArrayDesc(self.name, (2, self.pixel_count), 'f8')
        # self._ttheta_range = deg(
        #     arctan((arange(0, self.pixel_count) - self.pixel_count / 2 + 0.5) *
        #            self.pixel_size / self.radius))

    def doReadArray(self, quality):
        # ttheta = self._attached_ttheta.doRead()
        cts = self._attached_det.doReadArray(quality)
        # ttheta_range = self._ttheta_range + ttheta
        self.readresult = self._attached_det.readresult
        # return array([ttheta_range, cts], dtype='f8')
        return array([cts])

    def doStart(self):
        return self._attached_det.doStart()

    def doFinish(self):
        return self._attached_det.doFinish()

    def doStop(self):
        return self._attached_det.doStop()

    def doRead(self, maxage=0):
        return self._attached_det.doRead()

    def valueInfo(self):
        return self._attached_det.valueInfo()

    def doStatus(self, maxage=0):
        return self._attached_det.doStatus(maxage)

    def doPrepare(self):
        return self._attached_det.doPrepare()

    def doResume(self):
        return self._attached_det.doResume()

    def valueInfo(self):
        return (Value(self.name + '.sum', unit='cts', type='counter',
                      errors='sqrt', fmtstr='%d'), )
