# - * - encoding: utf-8 - * -
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Detector class for the laue PSL detector via the windows server."""

from nicos.core import ArrayDesc, Param, status
from nicos.devices.generic.detector import ImageChannelMixin, ActiveChannel

import numpy as np

from nicos.laue.psldrv import PSLdrv


class PSLDetector(ImageChannelMixin, ActiveChannel):

    parameters = {
        'address': Param('inet address', type=str,
                         default=''),
        'port': Param('port', type=int,
                      default='50000'),
        'imagewidth': Param('Image width',
                            type=int, default=2000, category='general'),
        'imageheight': Param('Image height',
                             type=int, default=1598, category='general'),

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
            iwstr, ihstr = '2000', '1598'
        self._setROParam('imagewidth', int(iwstr))
        self._setROParam('imageheight', int(ihstr))
        shape = (self.imagewidth, self.imageheight)
        self.arraydesc = ArrayDesc('data', shape, np.uint16)

    def doStart(self):
        self._communicate('Snap')

    _modemap = {'I;16': '<u2',
                'I': '<u4',
                'F': '<f4', }

    # XXX this needs a virtual timer to read the current elapsed time
    # def doRead(self, maxage=0): ...

    def doReadArray(self, quality):
        (shape, data) = self._communicate('GetImage')
        mode = self._communicate('GetMode')
        self._setROParam('imagewidth', shape[0])
        self._setROParam('imageheight', shape[1])
        # default for detector 'I:16' mode
        self.arraydesc = ArrayDesc('data', shape, self._modemap[mode])
        na = np.frombuffer(data, self._modemap[mode])

        na = na.reshape(shape)
        return na

    def doFinish(self):
        pass

    def doStop(self):
        self._communicate('AbortSnap')
        return False

    def doStatus(self, maxage=0):
        if self._communicate('GetCamState') == 'ON':
            if self._attached_timer:
                remain = self._preset - self._attached_timer.read(0)[0]
                return status.BUSY, '%.1f s remaining' % remain
            return status.BUSY, 'Exposure ongoing'
        return status.OK, 'OK'

    def doReadPreselection(self):
        if self.doStatus()[0] == status.OK:
            # the following call blocks during exposure
            self._preset = float(self._communicate('GetExposure')) / 1000.
        return self._preset

    def doWritePreselection(self, exptime):
        """exposure in seconds, hardware wants ms"""
        self._preset = exptime
        self._communicate('SetExposure;%f' % (exptime * 1000.))
