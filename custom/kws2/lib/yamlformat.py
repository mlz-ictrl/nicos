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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS-2 file format saver with YAML."""

from nicos import session
from nicos.kws1.yamlformat import YAMLFileSink as KWS1YAMLFileSink, \
    YAMLFileSinkHandler as KWS1YAMLFileSinkHandler


class YAMLFileSinkHandler(KWS1YAMLFileSinkHandler):

    filetype = 'MLZ.KWS2.2.0-beta1'

    def setDetectorPos(self, det):
        if session.getDevice('det_img').alias == 'det_img_jum':
            det['x_displacement'] = self._readdev('psd_x')
            det['y_displacement'] = self._readdev('psd_y')
            det['z_displacement'] = 17000
        else:
            det['beamstop_x_displacement'] = self._readdev('beamstop_x')
            det['beamstop_y_displacement'] = self._readdev('beamstop_y')
            det['z_displacement'] = self._readdev('det_z') * 1000

    def setDetectorInfo(self, det1):
        det_img = session.getDevice('det_img')
        if det_img.alias == 'det_img_jum':
            det1['pixel_width'] = 0.5
            det1['pixel_height'] = 0.5
        else:
            det1['pixel_width'] = 8.0
            if getattr(det_img, 'rebin8x8', False):
                det1['pixel_height'] = 8.0
            else:
                det1['pixel_height'] = 4.0


class YAMLFileSink(KWS1YAMLFileSink):
    """Saves image data and header in yaml format"""

    handlerclass = YAMLFileSinkHandler
