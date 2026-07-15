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

from math import atan, degrees

from nicos import session
from nicos.core.errors import ConfigurationError, NicosError
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXAttribute, NXLink

from nicos_mlz.nexus import Filter, ScanDeviceDataset, SollerCollimator, \
    counts, mm, signal
from nicos_mlz.nexus.templates import TasTemplateProvider


class PumaTemplateProvider(TasTemplateProvider):

    detectors = []

    def init(self, **kwargs):
        TasTemplateProvider.init(self, **kwargs)
        self.lad = kwargs.get('lad', 'lad')
        try:
            self.detectors = [
                c.name for c in session.getDevice(self.detector).valueInfo()
                if c.type == 'counter']
            if not self.detectors:
                raise ConfigurationError('No counters in detector device')
        except AttributeError as e:
            session.log.error('%s, there will be no detector data in file', e)
        except ConfigurationError as e:
            session.log.error('%s, there will be no detector data in file', e)
        except NicosError as e:
            session.log.error('%s, there will be no detector data in file', e)

    def updateData(self):
        for det in self.detectors:
            self._entry.update({
                f'{det}_data:NXdata': {
                    'data': NXLink(f'/{self.entry}/{self.instrument}/{det}/data'),
                    'ei': NXLink(f'/{self.entry}/{self.instrument}/monochromator/ei'),
                    'ef': NXLink(f'/{self.entry}/{self.instrument}/analyser/ef'),
                    'en': NXLink(f'/{self.entry}/{self.sample}/en'),
                    'qh': NXLink(f'/{self.entry}/{self.sample}/qh'),
                    'qk': NXLink(f'/{self.entry}/{self.sample}/qk'),
                    'ql': NXLink(f'/{self.entry}/{self.sample}/ql'),
                }
            })
        if self.detectors:
            self._entry.update({
                'default': NXAttribute(f'{self.detectors[0]}_data', 'string'),
            })

    def updateInstrument(self):
        TasTemplateProvider.updateInstrument(self)
        self._inst.update({
            'ca1:NXcollimator': SollerCollimator('alpha3'),
            'ca2:NXcollimator': SollerCollimator('alpha4'),
            'attenuator:NXattenuator': {
                'type': ConstDataset('unknown', dtype='string'),
                'thickness': ConstDataset(5, dtype='float', units=mm),
                # 'status': ,
                'attenuator_transmission': DeviceDataset('att'),
            },
            # 'polarizer:NXpolarizer': Polarizer(reflection=0.99),
            'filter_pg_1:NXfilter': Filter('fpg1', 'Pyrolytic Graphite'),
            'filter_pg_2:NXfilter': Filter('fpg1', 'Pyrolytic Graphite'),
            'erbium_filter:NXfilter': Filter('erbium', 'Erbium'),
            'sapphire_filter:NXfilter': Filter('sapphire', 'Sapphire'),
        })

    def updateDetector(self):
        inch = 25.4
        lad = 762
        TasTemplateProvider.updateDetector(self)
        self._inst.pop(f'{self.detector}:NXdetector', None)
        try:
            lad = session.getDevice(self.lad).read(0)
        except AttributeError as e:
            session.log.error('%s, use default lad value', e)
        except ConfigurationError as e:
            session.log.error('%s, use default lad value', e)
        except NicosError as e:
            session.log.error('%s, use default lad value', e)

        for i, det in enumerate(self.detectors, 1):
            if i > 3:
                d = lambda x: x + inch
                ofs = degrees(atan(inch / 2 / (lad + inch)))
                if i == 4:
                    a = lambda x, offset=ofs: x + offset
                else:
                    a = lambda x, offset=ofs: x - offset
            else:
                d = lambda x: x
                ofs = degrees(atan(inch / lad))
                if i == 1:
                    a = lambda x, offset=ofs: x + offset
                elif i == 3:
                    a = lambda x, offset=ofs: x - offset
                else:
                    a = lambda x: x
            self._inst[f'{det}:NXdetector'] = {
                'acquisition_mode': ConstDataset('pulse counting', 'string'),
                'data': DetectorDataset(det, dtype='int', units=counts,
                                        signal=signal),
                'diameter': ConstDataset(inch, 'float', units=mm),
                'distance': DeviceDataset('lad', mapping=d),
                'layout': ConstDataset('point', 'string'),
                'polar_angle': ScanDeviceDataset(self.att, mapping=a),
                'signal': NXAttribute('data', 'string'),
                'type': ConstDataset('He3 Gas cylinder', 'string'),
            }

        preset = session.getDevice(self.detector).preset()
        if preset.get(self.monitor):
            monitor = self.monitor
        # elif preset.get('mon2'):
        #     monitor = 'mon2'
        # elif preset.get('mon3'):
        #     monitor = 'mon3'
        else:
            monitor = self.timer

        monitor_link = f'/{self.entry}/{monitor}/'
        self._entry.update({'control:NXmonitor': {
            'mode': NXLink(f'{monitor_link}/mode'),
            'preset': NXLink(f'{monitor_link}/preset'),
            'integral': NXLink(f'{monitor_link}/integral'),
            # 'data': NXLink(f'{monitor_link}/integral'),
        }})
        if monitor != self.timer:
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitor_link}/type'),
            })

    def completeTemplate(self):
        TasTemplateProvider.completeTemplate(self)
        self._entry.update({
            'entry': f'{self.entry}',
        })
