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

"""KWS file format saver, KWS2 overrides"""

from nicos import session
from nicos.core import Override
from nicos_mlz.kws1.devices.kwsfileformat import KWSFileSink as KWS1FileSink, \
    KWSFileSinkHandler as KWS1FileSinkHandler


class KWSFileSinkHandler(KWS1FileSinkHandler):

    def getDetectorPos(self):
        """Return (x, y, z) for detector position."""
        if session.getDevice('det_img').alias == 'det_img_jum':
            x = session.getDevice('psd_x').read()
            y = session.getDevice('psd_y').read()
            z = 17.0
        else:
            x = session.getDevice('beamstop_x').read()
            y = session.getDevice('beamstop_y').read()
            z = session.getDevice('det_z').read()
        return (x, y, z)


class KWSFileSink(KWS1FileSink):
    """Saves KWS image and header data into a single file"""

    handlerclass = KWSFileSinkHandler

    parameter_overrides = {
        'instrname': Override(default='KWS2'),
    }
