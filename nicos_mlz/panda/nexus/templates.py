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
#   Alexander Zaft <a.zaft@fz-juelich.de>
#
# *****************************************************************************

from nicos.nexus.elements import ConstDataset, DeviceAttribute, \
    DeviceDataset, EndTime, NXLink, StartTime

from nicos_mlz.nexus import Filter, SollerCollimator, mm
from nicos_mlz.nexus.templates import TasTemplateProvider


class TemplateProvider(TasTemplateProvider):

    def updateInstrument(self):
        TasTemplateProvider.updateInstrument(self)
        self._inst.update({
            'ca1:NXcollimator': SollerCollimator('ca1'),
            'ca2:NXcollimator': SollerCollimator('ca2'),
            'ms:NXslit': {
                'x_gap': DeviceDataset(f'{self.ms}', units=mm),
                'y_gap': ConstDataset(0, 'float32'),  # fixed, get constant
                'center:NXtransformations': {
                    'x': ConstDataset(0, 'float32'),
                    'y': ConstDataset(0, 'float32'),
                },
            },
            'filter_epithermal:NXfilter': Filter('saph', 'Sapphire'),
            'filter_ki:NXfilter': Filter('befilter', 'Beryllium, Berylliumoxide'),
            'filter_kf:NXfilter': Filter('pgfilter', 'Beryllium, Pyrolytic Graphite'),
            'attenuator:NXattenuator': {
                'type': ConstDataset('unknown', dtype='string'),
                'thickness': ConstDataset(0, dtype='float', units=mm),
                # 'status': ,
                # 'attenuator_transmission': DeviceDataset(''),
            },
        })
        self._inst['monochromator:NXcrystal'].update({
            'segment_width': DeviceDataset('mono', 'segment_width'),
            'segment_height': DeviceDataset('mono', 'segment_height'),
            'segment_columns': DeviceDataset('mono', 'segment_columns'),
            'segment_rows': DeviceDataset('mono', 'segment_rows'),
            'curvature_vertical': DeviceDataset('mfv'),
            'curvature_horizontal': DeviceDataset('mfh'),
            'scattering_vector': DeviceDataset('ki'),
        })
        self._inst['analyser:NXcrystal'].update({
            'segment_width': DeviceDataset('ana', 'segment_width'),
            'segment_height': DeviceDataset('ana', 'segment_height'),
            'segment_columns': DeviceDataset('ana', 'segment_columns'),
            'segment_rows': DeviceDataset('ana', 'segment_rows'),
            'curvature_vertical': ConstDataset(0, 'float32'),
            'curvature_horizontal': DeviceDataset('afh'),
            'scattering_vector': DeviceDataset('kf'),
        })

    def updateDetector(self):
        TasTemplateProvider.updateDetector(self)
        self._det.update({
            'type': ConstDataset('He3 Gas cylinder', 'string'),
            'diameter': ConstDataset(0, 'float', units=mm),

        })
        self._entry[f'{self.monitor}:NXmonitor'].update({
            'start_time': StartTime(),
            'end_time': EndTime(),
        })

    def updateSample(self):
        TasTemplateProvider.updateSample(self)
        self._sample.update({
            'description': DeviceAttribute('Sample', 'sampledescription'),
        })

    def updateData(self):
        TasTemplateProvider.updateData(self)
        self._entry['data:NXdata'].update({
            'temperature': NXLink(f'/{self.entry}/{self.sample}/temperature'),
            'monitor_counts': NXLink(f'/{self.entry}/{self.monitor}/data'),
        })
