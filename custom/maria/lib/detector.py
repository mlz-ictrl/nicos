# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.core import status, Value, ArrayDesc
from nicos.core.errors import ConfigurationError
from nicos.core.params import Param, listof, tupleof, Override
from nicos.devices.tango import PyTangoDevice
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel, \
    Detector


class PostprocessPassiveChannel(PassiveChannel):

    parameters = {
        "readresult": Param("Storage for scalar results from image "
                            "filtering, to be returned from doRead()",
                            type=listof(float), settable=True,
                            userparam=False),
    }

    def doRead(self, maxage=0):
        return self.readresult

    def setReadResult(self, arrays):
        """This method should set `readresult` for corresponding `arrays`"""
        raise NotImplementedError("implement setReadResult")


class RectROIChannel(PostprocessPassiveChannel):

    parameters = {
        "roi": Param("Rectangular region of interest (x, y, width, height)",
                     tupleof(int, int, int, int),
                     settable=True,
                    ),
    }

    parameter_overrides = {
        "unit":   Override(default="cts"),
        'fmtstr': Override(default="%d"),
    }

    def setReadResult(self, arrays):
        if any(self.roi):
            x, y, w, h = self.roi
            self.readresult = [arrays[0][y:y+h, x:x+w].sum()]
        else:
            self.readresult = [arrays[0].sum()]

    def valueInfo(self):
        return Value(name=self.name, type="counter", fmtstr="%d"),


class MariaDetector(Detector):

    parameters = {
        "postprocess": Param("Post processing list containing tuples of "
                             "(PostprocessPassiveChannel, ImageChannelMixin, "
                             "...)",
                             listof(tuple),
                            ),
    }

    def doInit(self, _mode):
        self._postprocess = []
        for tup in self.postprocess:
            postdev = session.getDevice(tup[0])
            imgdevs = [session.getDevice(name) for name in tup[1:]]
            if not isinstance(postdev, PostprocessPassiveChannel):
                raise ConfigurationError("Device '%s' is not a "
                                         "PostprocessPassiveChannel" %
                                         postdev.name)
            if postdev not in self._channels:
                raise ConfigurationError("Device '%s' has not been configured "
                                         "for this detector" % postdev.name)
            for idev in imgdevs:
                if not isinstance(idev, ImageChannelMixin):
                    raise ConfigurationError("Device '%s' is not a "
                                             "ImageChannelMixin" % idev.name)
                if idev not in self._attached_images:
                    raise ConfigurationError("Device '%s' has not been "
                                             "configured for this detector" %
                                             idev.name)
            self._postprocess.append((postdev, imgdevs))

    def doReadArrays(self, quality):
        arrays = [img.readArray(quality) for img in self._attached_images]
        for postdev, imgdevs in self._postprocess:
            postarrays = [arrays[i] for i in (self._attached_images.index(
                idev) for idev in imgdevs)]
            postdev.setReadResult(postarrays)
        return arrays


class DenexImage(PyTangoDevice, ImageChannelMixin, PassiveChannel):

    def doInit(self, mode):
        self.arraydesc = ArrayDesc("coincimg", (1024, 1024), np.uint32)

    def valueInfo(self):
        return Value(name="total", type="counter", fmtstr="%d"),

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
