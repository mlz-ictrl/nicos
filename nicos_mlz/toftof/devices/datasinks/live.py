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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF special Live view sink for NICOS."""

import numpy

from nicos.devices.datasinks.special import LiveViewSink, LiveViewSinkHandler


class ToftofLiveViewSinkHandler(LiveViewSinkHandler):

    def processArrays(self, result):
        data = result[1][0]
        if data is not None:
            if len(data.shape) == 2:
                treated = numpy.transpose(data)[
                    self.detector._anglemap, :].astype('<u4')
                return [treated]

    def getLabelDescs(self, result):
        return {
            'x': {'define': 'classic', 'title': 'time channels'},
            'y': {'define': 'classic', 'title': 'detectors'},
        }


class ToftofLiveViewSink(LiveViewSink):
    """A data sink that sends images to attached clients for live preview."""

    handlerclass = ToftofLiveViewSinkHandler
