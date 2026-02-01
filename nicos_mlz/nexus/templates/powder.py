# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""Nexus data template for monochromatic powder applications."""

from nicos.nexus.elements import DeviceDataset, ImageDataset, NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, \
    TimerMonitor, axis1, signal


class PowderTemplateProvider(MLZTemplateProvider):

    definition = 'NXmonopd'

    def init(self, **kwargs):
        self.instrument = kwargs.get('instrument', 'instrument')
        self.wav = kwargs.get('wav', 'wav')
        self.tths = kwargs.get('tths', 'tths')
        self.omgs = kwargs.get('omgs', 'omgs')
        self.detector = kwargs.get('detector', 'adet')
        self.monitor = kwargs.get('monitor', 'mon')
        self.timer = kwargs.get('timer', 'tim1')

    def updateInstrument(self):
        self._inst.update({
            'mono:NXcrystal': {
                'wavelength': DeviceDataset(self.wav),
            },
        })

    def updateDetector(self):
        self._det.update({
            'polar_angle': DeviceDataset(self.tths, axis=axis1),
            'data': ImageDataset(0, 0, dtype=int, signal=signal),
        })
        self._entry.update({
            f'{self.monitor}:NXmonitor': CounterMonitor(self.monitor),
            f'{self.timer}:NXmonitor': TimerMonitor(self.timer),
        })

    def updateSample(self):
        self._sample.update({
            'rotation_angle': DeviceDataset(self.omgs, dtype='float'),
        })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'polar_angle': NXLink(
                f'/{self.entry}/{self.instrument}/{self.detector}/polar_angle'),
        })
