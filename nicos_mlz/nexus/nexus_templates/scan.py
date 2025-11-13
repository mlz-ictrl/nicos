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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, \
    TimerMonitor, signal
#   ScanDeviceDataset, aa, axis1, counts, nounit


class ScanTemplateProvider(MLZTemplateProvider):

    definition = 'NXscan'

    def init(self, **kwargs):
        self.sample = kwargs.get('sample', 'sample')
        self.omgs = kwargs.get('omgs')
        self.detector = kwargs.get('detector', 'det')
        self.monitor = kwargs.get('monitor', 'mon')
        self.timer = kwargs.get('timer', 'timer')

    def updateInstrument(self):
        # self._inst.update({
        #     'mono:NXcrystal': {
        #         'wavelength': DeviceDataset(self.wav),
        #     },
        # })
        pass

    def updateDetector(self):
        self._det.update({
            'data': DetectorDataset(self.detector, int, signal=signal),
        })
        self._entry.update({
            'mon:NXmonitor': CounterMonitor(self.monitor),
            'tim1:NXmonitor': TimerMonitor(self.timer),
        })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'rotation_angle': NXLink(
                f'/{self.entry}/{self.sample}/rotation_angle'),
        })

    def updateSample(self):
        if self.omgs:  # sample rotation device exists
            self._sample.update({
                'rotation_angle': DeviceDataset(self.omgs, dtype='float'),
            })
        else:
            self._sample.update({
                'rotation_angle': ConstDataset(0, dtype='float'),
            })
