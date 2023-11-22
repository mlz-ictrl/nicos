# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Alexander Book <alexander.book@frm2.tum.de>
#
# *****************************************************************************

from nicos.core.params import Attach, Param, floatrange, intrange, oneof, \
    tupleof
from nicos.devices.entangle import ImageChannel
from nicos.devices.tango import PyTangoDevice

anode_mapping = {
    'Cr': (5.41, 4.80),
    'Cu': (8.05, 6.40),
    'Mo': (17.48, 8.74),
    'Ag': (22.16, 11.08),
}


class Detector(ImageChannel):

    attached_devices = {
        'config': Attach('Dectris configuration device', PyTangoDevice),
    }

    parameters = {
        'pixel_size': Param('Size of a single pixel (in mm)',
                            type=tupleof(floatrange(0), floatrange(0)),
                            volatile=False, settable=False, default=(0.05, 10),
                            unit='mm', category='instrument'),
        'pixel_count': Param('Number of detector pixels',
                             type=intrange(1, 100000), volatile=True,
                             settable=False, category='instrument'),
        'precision': Param('Precision for comparison of the energy values to '
                           'find out the used anode material',
                           type=floatrange(0), default=0.01, unit='keV'),
        'anode': Param('X-ray Anode material',
                       type=oneof(*anode_mapping),
                       settable=True, userparam=True, category='instrument',
                       volatile=True),
        'flip': Param('Flipping spectrum',
                      type=bool, settable=False,
                      volatile=False, default=False,
                      category='general'),
    }

    def doReadArray(self, quality):
        narray = ImageChannel.doReadArray(self, quality)
        if self.flip:
            narray = narray[::-1]
        return narray

    def doReadPixel_Count(self):
        if self.arraydesc:
            return self.arraydesc.shape[0]
        return self._dev.detectorSize[0]

    def doReadAnode(self):
        photon, threshold = self._attached_config._dev.energy
        for name, vals in anode_mapping.items():
            if (abs(photon - vals[0]) <= self.precision and
               abs(threshold - vals[1]) <= self.precision):
                return name
        raise ValueError(
            self, f'unknown anode material: Photon energy: {photon} keV, '
            f' threshold: {threshold} keV')

    def doWriteAnode(self, value):
        self._attached_config._dev.energy = anode_mapping[value]
