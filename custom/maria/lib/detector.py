# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

import numpy as np

from nicos.core import status, Value, ArrayDesc
from nicos.devices.tango import PyTangoDevice
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel


class DenexImage(PyTangoDevice, ImageChannelMixin, PassiveChannel):

    def doInit(self, mode):
        self.arraydesc = ArrayDesc("coincimg", (1024, 1024), np.uint32)

    def valueInfo(self):
        return Value(name='total', type='counter', fmtstr='%d'),

    def doReadArray(self, _quality):
        narray = self._dev.value
        self.readresult = [narray.sum()]
        return narray.reshape(self.arraydesc.shape)

    def doPrepare(self):
        self._dev.Clear()

    def doStart(self):
        self._dev.Start()

    def doFinish(self):
        self._dev.Stop()

    def doStop(self):
        self._dev.Stop()

    def doStatus(self, maxage=0):
        return status.OK, "idle"
