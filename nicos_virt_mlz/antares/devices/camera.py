# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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

"""Virtual camera based on a virtual detector image."""

import time

import numpy as np
from PIL import Image

from nicos.core.params import ArrayDesc, Override, Param, intrange, none_or, \
    oneof, tupleof
from nicos.devices.generic import VirtualImage
from nicos.utils import createThread
from nicos.utils.timer import Timer


class Camera(VirtualImage):

    parameters = {
        'roi': Param('Region of interest (x, y, width, height), '
                     'x y of the left bottom corner, '
                     'width to the right, height to the top',
                     type=tupleof(int, int, int, int),
                     default=(0, 0, 0, 0),
                     settable=True, category='general'),
        'bin': Param('Binning (x,y)',
                     type=tupleof(oneof(1, 2, 4, 8), oneof(1, 2, 4, 8)),
                     settable=True, default=(1, 1), category='general'),
        'flip': Param('Flipping (x,y)',
                      type=tupleof(bool, bool), settable=True,
                      default=(False, False), category='general'),
        'rotation': Param('Rotation',
                          type=oneof(0, 90, 180, 270), settable=True,
                          default=0, category='general'),
        'expotime': Param('Exposure time',
                          type=float, settable=False,  # volatile=True,
                          category='general'),
        'cameramodel': Param('Camera type/model',
                             type=str, settable=False, category='general'),
        'shutteropentime': Param('Shutter open time',
                                 type=none_or(float), settable=True,
                                 default=0, category='general'),
        'shutterclosetime': Param('Shutter closed time',
                                  type=none_or(float), settable=True,
                                  default=0,  # volatile=False,
                                  category='general'),
        'shuttermode': Param('Shutter mode',
                             type=none_or(oneof('always_open',
                                                'always_closed',
                                                'auto')),
                             settable=True, default='auto',
                             category='general'),
        'hwsize': Param('Full detector size',
                        type=tupleof(intrange(1, 10240), intrange(1, 10240)),
                        userparam=False, settable=False, category='general'),
    }

    parameter_overrides = {
        'size': Override(type=tupleof(int, int), settable=False,
                         mandatory=False, volatile=True),
    }

    @property
    def arraydesc(self):
        return ArrayDesc(self.name, self.size[::-1], '<u2')

    @arraydesc.setter
    def arraydesc(self, val):
        pass

    def doPrepare(self):
        if self._mythread and self._mythread.is_alive():
            self._stopflag = True
            self._mythread.join()
        self._mythread = None
        self._buf = self._generate(0).astype('<u2')
        self.readresult = [self._buf.sum()]

    def doStart(self):
        self._last_update = 0
        self._timer = Timer()
        self._timer.start()
        self._stopflag = False
        if self._buf is None:
            self._buf = self._generate(0).astype('<u2')
            self.readresult = [self._buf.sum()]
        if not self._mythread:
            self._mythread = createThread('virtual camera %s' % self, self._run)

    def doReadArray(self, _quality):
        if self.bin == (1, 1):
            img = Image.fromarray(self._buf, mode='I;16')
        else:
            # w = self._buf.shape[0] // self.bin[0]
            # h = self._buf.shape[1] // self.bin[1]
            w, h = self.size
            shape = (w, self.bin[0], h, self.bin[1])
            img = Image.fromarray(self._buf.reshape(shape).sum(
                axis=(1, 3), dtype=self._buf.dtype), mode='I;16')
        if self.flip != (False, False):
            if self.flip[0]:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            if self.flip[1]:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if self.rotation:
            # PIL rotates counterclockwise
            img = img.transpose({
                90: Image.ROTATE_270,
                180: Image.ROTATE_180,
                270: Image.ROTATE_90}[self.rotation])
        return np.array(img).T

    def doReadSize(self):
        return (self.hwsize[0] // self.bin[0], self.hwsize[1] // self.bin[1])

    def _run(self):
        while not self._stopflag:
            elapsed = self._timer.elapsed_time()
            self.log.debug('update image: elapsed = %.1f', elapsed)
            if self._timer.is_running():
                array = self._generate(self._base_loop_delay).astype('<u2')
                self._buf += array
                self.readresult = [self._buf.sum()]
            time.sleep(self._base_loop_delay)

    def _generate(self, t):
        dst = ((self._attached_distance.read() * 5) if self._attached_distance
               else 5)
        coll = (self._attached_collimation.read() if self._attached_collimation
                else '15m')
        xl, yl = self.hwsize
        xx, yy = np.meshgrid(np.linspace(-(xl // 2), (xl // 2) - 1, xl),
                             np.linspace(-(yl // 2), (yl // 2) - 1, yl))
        beam = (t * 100 * np.exp(-xx**2/50) * np.exp(-yy**2/50)).astype(int)
        sigma2 = coll == '10m' and 200 or (coll == '15m' and 150 or 100)
        beam += (
            t * 30 * np.exp(-(xx-dst)**2/sigma2) * np.exp(-yy**2/sigma2) +
            t * 30 * np.exp(-(xx+dst)**2/sigma2) * np.exp(-yy**2/sigma2) +
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy-dst)**2/sigma2) +
            t * 20 * np.exp(-xx**2/sigma2) * np.exp(-(yy+dst)**2/sigma2)
        ).astype(int)
        return np.random.poisson(np.ascontiguousarray(beam.T +
                                                      self.background))
