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

"""HRPD specific file format(s)."""

from nicos.core import Override
from nicos.core.constants import POINT
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.pycompat import to_utf8


class HrpdFileHandler(SingleFileSinkHandler):
    """Handler for the CaressHistogram data sink."""

    filetype = 'caresshistogram'

    def __init__(self, sink, dataset, detector):
        SingleFileSinkHandler.__init__(self, sink, dataset, detector)

    def writeHeader(self, fp, metainfo, image):
        pass

    def writeData(self, fp, image):
        _metainfo = self.dataset.metainfo
        detectors = self.sink.detectors
        detector = detectors[0] if detectors else 'adet'
        _resosteps = _metainfo[detector, 'resosteps'][0]
        _range = _metainfo[detector, 'range'][0]
        _stepsize = _range / _resosteps
        _startpos = _metainfo[detector, '_startpos'][0]
        _start = _startpos - (_resosteps - 1) * _stepsize
        fp.write(b'position\tcounts\n')
        for i, v in enumerate(image):
            _pos = _start + i * _stepsize
            fp.write(to_utf8('%.2f\t%d\n' % (_pos, v.sum())))

        fp.flush()


class HrpdSink(ImageSink):
    """Data sink for the HRPD specific data file format.

    The counts of neutrons in each tube will be written in respect to the angle
    of the tube at measurement time.
    """

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_'
                                              '%(pointcounter)07d.dat']),
        'settypes': Override(default=[POINT]),
    }

    handlerclass = HrpdFileHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
