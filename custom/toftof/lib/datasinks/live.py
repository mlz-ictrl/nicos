#  -*- coding: utf-8 -*-
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF special Live view sink for NICOS."""

from time import time as currenttime

from nicos import session
from nicos.core import Override
from nicos.pycompat import memory_buffer
from nicos.toftof.datasinks.base import TofSink, TofSinkHandler


class ToftofLiveViewSinkHandler(TofSinkHandler):

    def __init__(self, sink, dataset, detector):
        TofSinkHandler.__init__(self, sink, dataset, detector)

    def putResults(self, quality, results):
        if self.detector.name in results:
            data = results[self.detector.name][1][0]
            if data is not None:
                if len(data.shape) == 2:
                    treated = data[self.detector._anglemap, :].astype('<u4',
                                                                      order='C')
                    (resY, resX), resZ = treated.shape, 1
                    session.updateLiveData('Live', '', '<u4', resX, resY, resZ,
                                           currenttime() - self.dataset.started,
                                           memory_buffer(treated))


class ToftofLiveViewSink(TofSink):
    """A data sink that sends images to attached clients for live preview."""

    parameter_overrides = {
        # this is not really used, so we give it a default that would
        # raise if used as a template filename
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['']),
    }

    handlerclass = ToftofLiveViewSinkHandler
