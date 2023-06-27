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

from nicos_mlz.nexus import CounterMonitor, LocalContact, \
    MLZTemplateProvider, TimerMonitor, User, axis1, signal


class StressiNexusTemplateProvider(MLZTemplateProvider):

    definition = 'NXstress'
    # instrument = 'STRESS-SPEC'
    sample = 'SAMPLE_DESCRIPTION'
    source = 'SOURCE'
    detector = 'DETECTOR'

    def updateInstrument(self):
        self._inst.update({
            'mono:NXcrystal': {
                'wavelength': DeviceDataset('wav'),
            },
            'beam_intensity_profile:NXbeam': {
                # 'beam_evaluation': ,
                # 'primary_vertical_type': ,
                # 'primary_vertical_full_width': ,
                # 'primary_vertical_width': ,
                # ...
            },
        })

    def updateDetector(self):
        self._det.update({
            # 'description': ,
            # 'distance': ,
            # 'efficiency': ,
            # 'wavelenght': ,
            # 'dead_time': ,
            # 'count_time': ,
            # 'depends_on': ,
            'polar_angle': DeviceDataset('tths', axis=axis1),
            'layout': ConstDataset('area', 'string'),
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
            # 'image_key': DeviceDataset('image_key'),
            'data': DetectorDataset('adet', int, signal=signal),
            'type': ConstDataset('He3 PSD', 'string'),
            # 'data': ImageDataset(0, 0, dtype=int, signal=signal),
        })
        self._entry.update({
            'mon:NXmonitor': CounterMonitor('mon'),
            'tim1:NXmonitor': TimerMonitor('tim1'),
        })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'polar_angle': NXLink(
                f'/{self.entry}/{self.instrument}/{self.detector}/polar_angle'),
            # 'rotation_angle': NXLink(
            #   f'/{self.entry}/{self.sample}/rotation_angle'),
            # 'image_key': NXLink(
            #   f'/{self.entry}/{self.instrument}/{self.detector}/image_key'),
        })

    def updateSample(self):
        self._sample.update({
            # 'chemical_formula': ,
            # 'temperature': ,
            # 'stress_field', direction=NXAttribute('x', 'string'))
            # 'stress_field': , direction=NXAttribute('x'|'y'|'z', string)
            # 'depends_on': ,
            'gauge_volume:NXparameters': {
                # 'a': ,
                # 'b': ,
                # 'h': ,
                # 'x': ,
                # 'y': ,
                # 'z': ,
            },
            'rotation_angle': DeviceDataset('omgs', dtype='float'),
            # 'x_translation': DeviceDataset('stx_huber'),
            # 'y_translation': DeviceDataset('sty_huber'),
        })

    def updateUsers(self):
        self._entry.update({
            'local_contact:NXuser': LocalContact(),
            'experiment_responsible:NXuser': User(),
        })

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'processing_type': ConstDataset('two-theta', 'string'),
            # 'measurement_direction': ,
            # 'experiment_documentation': ,
            # 'processing_type': ,
        })
