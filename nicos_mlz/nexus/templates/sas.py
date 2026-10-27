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

from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceDataset, ImageDataset, \
    NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, \
    SollerCollimator, TimerMonitor, deg, mm, signal


class SansTemplateProvider(MLZTemplateProvider):

    definition = 'NXsas'

    def init(self, **kwargs):
        MLZTemplateProvider.init(self, **kwargs)
        self.mon1 = kwargs.get('mon1', 'mon1')
        self.timer = kwargs.get('timer', 'timer')
        self.wav = kwargs.get('wav', 'wav')
        self.wav_spread = kwargs.get('wav_spread', 'dwav')
        self.det_x = kwargs.get('det_x', 'det_x')
        self.col = kwargs.get('col', 'col')
        self._monitors = [self.mon1]

    def updateInstrument(self):
        self._inst.update({
            'monochromator:NXmonochromator': {
                'wavelength': DeviceDataset(self.wav),
                'wavelength_spread': DeviceDataset(self.wav_spread)
            },
            'collimator:NXcollimator': SollerCollimator(self.col),
        })

    def updateDetector(self):
        self._det.update({
            'data': ImageDataset(0, 0, dtype=int, signal=signal),
            'distance': DeviceDataset(self.det_x),
            'x_pixel_size': ConstDataset(1, 'float', units=mm),
            'y_pixel_size': ConstDataset(1, 'float', units=mm),
            'polar_angle': ConstDataset(0, 'float', units=deg),
            'azimuthal_angle': ConstDataset(0, 'float', units=deg),
            'rotation_angle': ConstDataset(0, 'float', units=deg),
            'aequatorial_angle': ConstDataset(0, 'float', units=deg),
            'beam_center_x': ConstDataset(0, 'float', units=mm),
            'beam_center_y': ConstDataset(0, 'float', units=mm),
        })

        self._entry.update({
            f'{self.mon1}:NXmonitor': CounterMonitor(self.mon1),
            f'{self.timer}:NXmonitor': TimerMonitor(self.timer),
        })

        preset = session.getDevice(self.detector).preset()
        monitor = self.timer
        for mon in self._monitors:
            if preset.get(mon):
                monitor = mon
        monitor_link = f'/{self.entry}/{monitor}'
        self._entry.update({'control:NXmonitor': {
            'mode': NXLink(f'{monitor_link}/mode'),
            'preset': NXLink(f'{monitor_link}/preset'),
            'integral': NXLink(f'{monitor_link}/integral'),
        }})
        if monitor != self.timer:
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitor_link}/type'),
            })

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
