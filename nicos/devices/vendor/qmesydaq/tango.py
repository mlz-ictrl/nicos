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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Detector devices for QMesyDAQ type detectors (TANGO)."""

from nicos.core.params import Param, oneof
from nicos.devices.tango import ImageChannel as BaseImageChannel
from nicos.devices.vendor.qmesydaq import Image as QMesyDAQImage


class ImageChannel(QMesyDAQImage, BaseImageChannel):

    parameters = {
        'readout': Param('Readout mode of the Detector', settable=True,
                         type=oneof('raw', 'mapped', 'amplitude'),
                         default='mapped', mandatory=False, chatty=True),
    }

    def doWriteListmode(self, value):
        self._dev.SetProperties(['writelistmode', '%s' % value])
        return self._getProperty('writelistmode')

    def doWriteHistogram(self, value):
        self._dev.SetProperties('writehistogram', '%s' % value)
        return self._getProperty('writehistogram')

    def doWriteReadout(self, value):
        self._dev.SetProperties(['histogram', '%s' % value])
        return self._getProperty('histogram')

    def doWriteListmodefile(self, value):
        self._dev.SetProperties(['lastlistfile', '%s' % value])
        return self._getProperty('lastlistfile')

#   def doReadListmodefile(self):
#       return self._getProperty('lastlistfile')

    def doWriteHistogramfile(self, value):
        self._taco_update_resource('lasthistfile', '%s' % value)
        return self._getProperty('lasthistfile')

#   def doReadHistogramfile(self):
#       return self._getProperty('lasthistfile')

    def doReadConfigfile(self):
        return self._getProperty('configfile')

    def doReadCalibrationfile(self):
        return self._getProperty('calibrationfile')
