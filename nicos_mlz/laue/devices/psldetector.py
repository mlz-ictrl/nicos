# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

import numpy as np

from nicos.core import ArrayDesc, Param, status
from nicos.core.constants import SIMULATION
from nicos.devices.generic.detector import ActiveChannel, Detector, \
    ImageChannelMixin

from nicos_mlz.laue.devices.psldrv import PSLdrv


class SyncedDetector(Detector):
    """A special synced detector for NLAUE

    This detector propagates the time preset to all devices, not only to the
    first timer as the default implementation does.

    The timer here is typically just a virtual device, while the true timing
    is done by the image device (but that one can not be read back).
    """

    def doSetPreset(self, **preset):
        if not preset:
            return

        if 't' in preset:
            for img in self._attached_images:
                img.preselection = preset['t']
                img.ismaster = True
            for timer in self._attached_timers:
                timer.preselection = preset['t']
                timer.ismaster = False


class PSLDetector(ImageChannelMixin, ActiveChannel):
    """PhotonicScience detector

    This detector is an interface to the PhotonicScience AUI server
    """

    parameters = {
        'address': Param('Inet address', type=str,
                         default=''),
        'port': Param('Port', type=int,
                      default='50000'),
        'imagewidth': Param('Image width',
                            type=int, default=2000, category='general'),
        'imageheight': Param('Image height',
                             type=int, default=1598, category='general'),

    }

    def valueInfo(self):
        return ()

    def _communicate(self, cmd):
        # we need to create a fresh socket each time, as the remote
        # end closes the socket after each command
        psl = PSLdrv(self.address, self.port)
        return psl.communicate(cmd)

    def doInit(self, mode):
        # Determine image type
        self._preset=0
        if mode == SIMULATION:
            iwstr, ihstr = '2000', '1598'
        else:
            try:
                data = self._communicate('GetSize')
                self.doReadPreselection()
                iwstr, ihstr = data.split(';')
            except OSError:
                self.log.warning('Error during init', exc=1)
                iwstr, ihstr = '2000', '1598'
        self._setROParam('imagewidth', int(iwstr))
        self._setROParam('imageheight', int(ihstr))
        shape = (self.imagewidth, self.imageheight)
        self.arraydesc = ArrayDesc(self.name, shape, np.uint16)

    def doStart(self):
        self._communicate('Snap')

    _modemap = {'I;16': '<u2',
                'I': '<u4',
                'F': '<f4', }

    # XXX this needs a virtual timer to read the current elapsed time
    # def doRead(self, maxage=0): ...

    def doReadArray(self, quality):
        if not self._sim_intercept:
            (shape, data) = self._communicate('GetImage')
            mode = self._communicate('GetMode')
        else:
            shape = (self.imagewidth, self.imageheight)
            data = b'0' * self.imagewidth * self.imageheight
        self._setROParam('imagewidth', shape[0])
        self._setROParam('imageheight', shape[1])
        # default for detector 'I:16' mode
        self.arraydesc = ArrayDesc(self.name, shape, self._modemap[mode])
        na = np.frombuffer(bytearray(data), self._modemap[mode])

        na = np.flipud(na.reshape(shape))
        # as flipud creates a view, we need to copy first
        return np.require(na, None, ['C', 'O'])

    def doFinish(self):
        pass

    def doStop(self):
        self._communicate('AbortSnap')

    def doStatus(self, maxage=0):
        if self._communicate('GetCamState') == 'ON':
            # if self._attached_timer:
            #     remain = self._preset - self._attached_timer.read(0)[0]
            #     return status.BUSY, '%.1f s remaining' % remain
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
