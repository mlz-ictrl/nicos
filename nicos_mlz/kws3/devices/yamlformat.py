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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS3 specific adaptation of the KWS YAML format."""

from nicos import session

from nicos_mlz.kws1.devices import yamlformat


class YAMLFileSinkHandler(yamlformat.YAMLFileSinkHandler):

    def _set_detector_resolution(self, det1):
        det_img = session.getDevice('det_img')
        if det_img.alias == 'det_img_vhrd':
            det1['pixel_width'] = 0.2
            det1['pixel_height'] = 0.2
        else:
            det1['pixel_width'] = 0.5
            det1['pixel_height'] = 0.5


class YAMLFileSink(yamlformat.YAMLFileSink):

    handlerclass = YAMLFileSinkHandler
