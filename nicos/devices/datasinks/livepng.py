#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

from time import time as currenttime

import numpy as np
try:
    import PIL
    from PIL import Image
except ImportError as e:
    PIL = None
    _import_error = e

from nicos.core import Param, Override, DataSinkHandler, NicosError
from nicos.devices.datasinks.image import ImageSink


def makeLUT(n, spec):
    lut = np.ones(n + 1, np.uint8)
    nold = 0
    yold = spec[0][2]
    for x, y1, y2 in spec[1:]:
        ni = int(x * n)
        # this 255 is due to 8 bpp, not due to size of LUT
        lut[nold:ni] = np.linspace(yold, y1, ni - nold) * 255
        nold = ni
        yold = y2
    assert ni == n
    lut[n] = lut[n - 1]
    return lut

# "Jet" colormap parametrized as in Matplotlib
colormap = {
    'red':   ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89, 1, 1),
              (1, 0.5, 0.5)),
    'green': ((0., 0, 0), (0.125, 0, 0), (0.375, 1, 1), (0.64, 1, 1),
              (0.91, 0, 0), (1, 0, 0)),
    'blue':  ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1),
              (0.65, 0, 0), (1, 0, 0))
}

# Generate lookup table
LUT_r = makeLUT(256, colormap['red'])
LUT_g = makeLUT(256, colormap['green'])
LUT_b = makeLUT(256, colormap['blue'])


class PNGLiveFileSinkHandler(DataSinkHandler):
    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._last_saved = 0

    def putResults(self, quality, results):
        if currenttime() - self._last_saved > self.sink.interval:
            if self.detector.name in results:
                data = results[self.detector.name][1][0]
                if data is not None:
                    self._writeData(data)

    def _writeData(self, data):
        image = np.array(data)
        max_pixel = image.max()
        if self.sink.log10:
            zeros = (image == 0)
            image = np.log10(image)
            max_pixel_log = np.log10(max_pixel) if max_pixel else 1
            norm_arr = image.astype(float) * 255. / max_pixel_log
            norm_arr = norm_arr.astype(np.uint8)
            norm_arr[zeros] = 0
        else:
            if max_pixel == 0:
                norm_arr = image
            else:
                norm_arr = image.astype(float) * 255. / max_pixel
                norm_arr = norm_arr.astype(np.uint8)
        try:
            rgb_arr = np.zeros(image.shape + (3,), np.uint8)
            rgb_arr[..., 0] = LUT_r[norm_arr]
            rgb_arr[..., 1] = LUT_g[norm_arr]
            rgb_arr[..., 2] = LUT_b[norm_arr]
            Image.fromarray(rgb_arr, 'RGB').save(self.sink.filename)
        except Exception:
            self.log.warning('could not save live PNG', exc=1)
        self._last_saved = currenttime()


class PNGLiveFileSink(ImageSink):
    """Writes (live) data to a PNG file, possibly with a log-10 color scale.

    Data is normalized to the highest-value pixel, and the used color map is
    the commonly used "Jet" colormap.

    This is not intended for data result storage, but to create images of the
    live measurement for quick view, e.g. in status monitors.
    """

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['']),
    }

    parameters = {
        'interval': Param('Interval to write file to disk', unit='s',
                          default=5),
        'filename': Param('File name for .png image', type=str, mandatory=True),
        'log10':    Param('Use logarithmic counts for image', type=bool,
                          default=False),
    }

    handlerclass = PNGLiveFileSinkHandler

    def doPreinit(self, mode):
        if PIL is None:
            self.log.error(_import_error)
            raise NicosError(self, 'Python Image Library (PIL) is not ' +
                             'available. Please check wether it is installed ' +
                             'and in your PYTHONPATH')

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
