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

from nicos.nexus.elements import ConstDataset, DeviceDataset, NXLink

from nicos_mlz.nexus import BeamStop, CounterMonitor, Polarizer, Selector, \
    deg, mm
from nicos_mlz.nexus.templates import SansTemplateProvider


class SANSTemplateProvider(SansTemplateProvider):

    def init(self, **kwargs):
        SansTemplateProvider.init(self, **kwargs)
        # self.instrument = kwargs.get('instrument', 'instrument')
        # self.wav = kwargs.get('wav', 'wav')
        # self.tths = kwargs.get('tths', 'tths')
        # self.omgs = kwargs.get('omgs', 'omgs')
        # self.ysd = kwargs.get('ysd', 'ysd')
        self.mon2 = kwargs.get('mon2', 'mon2')
        self.mon3 = kwargs.get('mon3', 'mon3')
        self.att = kwargs.get('att', 'att')
        self.bs = kwargs.get('bs', 'bs1')
        self._monitors.extend([self.mon2, self.mon3])

    def updateInstrument(self):
        SansTemplateProvider.updateInstrument(self)
        self._inst.update({
            'monochromator:NXmonochromator': {
                'wavelength': NXLink(
                    f'/{self.entry}/{self.instrument}/monochromator/velocity_selector/wavelength'),
                'wavelength_spread': NXLink(
                    f'/{self.entry}/{self.instrument}/monochromator/velocity_selector/wavelength_spread'),
                'velocity_selector:NXvelocity_selector': Selector(
                    'selector_rpm', 'selector_lambda', 'selector_delta_lambda',
                    'selector_tilt'),
            },
            'attenuator:NXattenuator': {
                'attenuator_transmission': DeviceDataset(self.att),
            },
            'beam_stop:NXbeam_stop': BeamStop(self.bs),
            'polarizer:NXpolarizer': Polarizer(reflection=0.99),
        })

    def updateDetector(self):
        self._entry.update({
            f'{self.mon2}:NXmonitor': CounterMonitor(self.mon2),
            # f'{self.mon3}:NXmonitor': CounterMonitor(self.mon3),
        })

        SansTemplateProvider.updateDetector(self)
        self._det.update({
            'x_pixel_size': ConstDataset(8, 'float', units=mm),
            'y_pixel_size': ConstDataset(8, 'float', units=mm),

            'polar_angle': ConstDataset(0, 'float', units=deg),
            'azimuthal_angle': ConstDataset(0, 'float', units=deg),
            'rotation_angle': ConstDataset(0, 'float', units=deg),
            'aequatorial_angle': ConstDataset(0, 'float', units=deg),

            'beam_center_x': ConstDataset(0, 'float', units=mm),
            'beam_center_y': ConstDataset(0, 'float', units=mm),

            'type': ConstDataset('He3 PSD', 'string'),
            'layout': ConstDataset('area', 'string'),
            'diameter': ConstDataset(8, 'float', units=mm),
            # TODO: find out how to set the correct value for tisane
            'acquisition_mode': ConstDataset('histogrammed', 'string'),
        })

    def completeTemplate(self):
        SansTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
