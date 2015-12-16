#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Base classes for the QMesyDAQ devices."""

from nicos.core import Param, Value
from nicos.devices.generic.detector import ImageChannelMixin, PassiveChannel, \
    ImageType


class Image(ImageChannelMixin, PassiveChannel):
    """Channel that returns the image, histogram, or spectrogram."""

    # initial imagetype, will be updated upon readImage
    imagetype = ImageType((128, 128), '<u4')

    parameters = {
        'listmodefile': Param('List mode data file name (if it is empty, no '
                              'file will be written)',
                              type=str, settable=True, default='',
                              ),
        'histogramfile': Param('Histogram data file name (if it is empty, no '
                               'file will be written)',
                               type=str, settable=True, default='',
                               ),
    }

    def valueInfo(self):
        return Value('%s.sum' % self, type='counter', errors='sqrt',
                     unit='cts', fmtstr='%d'),

    def readLiveImage(self):
        return self.readFinalImage()
