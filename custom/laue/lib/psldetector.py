# - * - encoding: utf-8 - * -
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************
'''Detector class for the laue PSL detector via the windows server'''

from nicos.core import Measurable, ImageProducer, \
    ImageType, Param, Override, status

from nicos.laue.psldrv import PSLdrv
import numpy as np


class PSLDetector(ImageProducer, Measurable):

    parameters = {
        'address': Param('inet address', type=str,
                         default=''),
        'port': Param('port', type=int,
                      default='50000'),
        'imagewidth': Param('Image width',
                            type=int, default=2000, category='general'),
        'imageheight': Param('Image height',
                             type=int, default=1000, category='general'),

    }

    parameter_overrides = {
        'subdir': Override(settable=True),
    }

    def _communicate(self, cmd):
        # we need to create a fresh socket each time, as the remote
        # end closes the socket after each command
        psl = PSLdrv(self.address, self.port)
        return psl.communicate(cmd)

    def doInit(self, mode):
        # Determine image type
        try:
            data = self._communicate('GetSize')
            iwstr, ihstr = data.split(';')
        except IOError:
            self.log.warning('Error during init', exc=1)
            iwstr, ihstr = '2000', '1000'
        self._params['imagewidth'] = int(iwstr)
        self._params['imageheight'] = int(ihstr)
        shape = (self.imagewidth, self.imageheight)
        self.imagetype = ImageType(shape, np.uint16)

    def doRead(self, _maxage=0):
        return self.lastfilename

    def doStart(self):
        self._communicate('Snap')

    def readFinalImage(self):
        (shape, data) = self._communicate('GetImage')
        self._params['imagewidth'], self._params['imageheight'] = shape
        # default for detector 'I:16' mode
        na = np.frombuffer(data, '<u2')

        na = na.reshape(shape)
        return na

    def doStop(self):
        self._communicate('AbortSnap')

    def doStatus(self, maxage=0):  # pylint: disable=W0221
        if self._communicate('GetCamState') == 'ON':
            return status.BUSY, 'Exposure ongoing'
        return status.OK, 'OK'

    def doIsCompleted(self):
        if self.doStatus()[0] == status.BUSY:
            return False
        return True

    def doReadPreselection(self):
        if self.doStatus()[0] == status.OK:
            # the following call blocks during exposure
            self._preset = float(self._communicate('GetExposure')) / 1000.
        return self._preset

    def doWritePreseletion(self, exptime):
        '''exposure in seconds, hardware wants ms)'''
        self._preset = exptime
        self._communicate('SetExposure;%f' % self._preset * 1000.)

    def doSetPreset(self, **presets):
        if 't' in presets:
            self.preselection = presets['t']
