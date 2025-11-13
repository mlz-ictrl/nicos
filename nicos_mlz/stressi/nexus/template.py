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

from nicos.nexus.elements import ConstDataset, DeviceDataset

from nicos_mlz.nexus import Slit
from nicos_mlz.nexus.nexus_templates import PowderTemplateProvider


class StressiTemplateProvider(PowderTemplateProvider):

    def updateInstrument(self):
        PowderTemplateProvider.updateInstrument(self)
        self._inst.update({
            'beam_intensity_profile:NXbeam': {
                # 'beam_evaluation': ,
                # 'primary_vertical_type': ,
                # 'primary_vertical_full_width': ,
                # 'primary_vertical_width': ,
                # ...
            },
            'sample_slit:NXslit': Slit('slits'),
            'monochromator_slit:NXslit': Slit('slitm'),
        })

    def updateDetector(self):
        PowderTemplateProvider.updateDetector(self)
        self._det.update({
            'type': ConstDataset('He3 PSD', 'string'),
            'layout': ConstDataset('area', 'string'),
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
            'description': DeviceDataset(self.detector, 'description'),
            'x_pixel_size': DeviceDataset(self.detector, 'pixel_size[0]'),
            'y_pixel_size': DeviceDataset(self.detector, 'pixel_size[1]'),
            # 'distance': ,
            # 'efficiency': ,
            # 'wavelength': ,
            # 'dead_time': ,
            # 'count_time': ,
            # 'image_key': DeviceDataset('image_key'),
            # 'depends_on': ,
        })

    def updateData(self):
        PowderTemplateProvider.updateData(self)
        self._entry['data:NXdata'].update({
            # 'rotation_angle': NXLink(
            #   f'/{self.entry}/{self.sample}/rotation_angle'),
            # 'image_key': NXLink(
            #   f'/{self.entry}/{self.instrument}/{self.detector}/image_key'),
        })

    def updateSample(self):
        PowderTemplateProvider.updateSample(self)
        self._sample.update({
            'type': ConstDataset('sample', 'string'),
            # 'chemical_formula': ,

            # 'temperature': ,
            # 'temperature_log:NXlog': ,
            # 'temperature_env:NXenvironment': ,

            # 'electric_field': ,
            # 'electric_fieldlog:NXlog': ,
            # 'electric_field_env:NXenvironment': ,

            # 'magnetic_field': ,
            # 'magnetic_field_log:NXlog': ,
            # 'magnetic_field_env:NXenvironment': ,

            # 'stress_field': direction=NXAttribute('x', 'string'))
            # 'stress_field': direction=NXAttribute('x'|'y'|'z', string)
            # 'stress_field_log:NXlog': ,
            # 'stress_field_env:NXenvironment': ,

            # 'pressure': ,
            # 'pressure_log:NXlog': ,
            # 'pressure_env:NXenvironment': ,

            # 'depends_on': ,

            # 'depends_on': ,
            # 'gauge_volume:NXcollection': {
            'gauge_volume:NXparameters': {
                # 'a': ,
                # 'b': ,
                # 'h': ,
                # 'x': ,
                # 'y': ,
                # 'z': ,
            },
            # 'x_translation': DeviceDataset('stx_huber'),
            # 'y_translation': DeviceDataset('sty_huber'),
        })

        # 'definition': ,
        # 'diffraction_type': ,
        # 'experiment_documentation': ,

    def updateUsers(self):
        PowderTemplateProvider.updateUsers(self)
        self._entry.update({
            # 'experiment_responsible:NXuser': User(),
        })

    def completeTemplate(self):
        PowderTemplateProvider.completeTemplate(self)
        self._entry.update({
            # 'processing_type': ConstDataset('two-theta', 'string'),
            # 'measurement_direction': ,
            # 'experiment_documentation': ,
        })
