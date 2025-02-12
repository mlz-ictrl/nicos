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

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXLink, NXScanLink
from nicos.nexus.specialelements import CellArray, UBMatrix

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, Reflection, \
    ScanDeviceDataset, TimerMonitor, aa, axis1, counts, nounit, signal


class TasTemplateProvider(MLZTemplateProvider):

    definition = 'NXtas'

    def init(self, **kwargs):
        self.det = kwargs.get('det', 'det')
        self.sgx = kwargs.get('sgx', 'sgx')
        self.sgy = kwargs.get('sgy', 'sgy')
        self.stt = kwargs.get('phi', 'phi')
        self.sth = kwargs.get('psi', 'psi')
        self.ana = kwargs.get('ana', 'ana')
        self.mono = kwargs.get('mono', 'mono')
        self.ei = kwargs.get('ei', 'Ei')
        self.ef = kwargs.get('ef', 'Ef')

    def updateInstrument(self):
        self._inst.update({
            'monochromator:NXcrystal': {
                'usage': ConstDataset('Bragg', 'string'),
                'type': DeviceDataset(self.mono, 'material'),
                'd_spacing': DeviceDataset(self.mono, 'dvalue', units=aa),
                'reflection': Reflection(self.mono),
                'rotation_angle': ScanDeviceDataset('mth'),
                'polar_angle': ScanDeviceDataset('mtt'),
                'ei': ScanDeviceDataset(self.ei, axis=axis1),
                'wavelength': DeviceDataset(self.mono, unit='A-1'),
            },
            'analyser:NXcrystal': {
                'usage': ConstDataset('Bragg', 'string'),
                'type': DeviceDataset(self.ana, 'material'),
                'd_spacing': DeviceDataset(self.ana, 'dvalue', units=aa),
                'reflection': Reflection(self.ana),
                'rotation_angle': ScanDeviceDataset('ath'),
                'polar_angle': ScanDeviceDataset('att'),
                'ef': ScanDeviceDataset(self.ef, axis=axis1),
                'wavelength': DeviceDataset(self.ana, units='A-1'),
            },
        })

    def updateDetector(self):
        self._det.update({
            'polar_angle': ScanDeviceDataset('att'),
            'data': DetectorDataset(self.det, dtype='int', units=counts,
                                    signal=signal),
        })
        self._entry.update({
            'mon1:NXmonitor': CounterMonitor('mon1'),
            'timer:NXmonitor': TimerMonitor('timer'),
        })
        preset = session.getDevice(self.det).preset()
        if preset.get('mon1'):
            monitor = 'monitor1'
        else:
            monitor = 'timer'
        monitor_link = f'/{self.entry}/{monitor}'
        self._entry.update({
            'control:NXmonitor': {
                'mode': NXLink(f'{monitor_link}/mode'),
                'preset': NXLink(f'{monitor_link}/preset'),
                'data': NXLink(f'{monitor_link}/integral'),
            },
        })
        if monitor != 'timer':
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitor_link}/type'),
            })

    def updateSample(self):
        self._sample.update({
            'orientation_matrix': UBMatrix(),
            'unit_cell': CellArray(),
            'sgu': ScanDeviceDataset(self.sgx),
            'sgl': ScanDeviceDataset(self.sgy),
            'polar_angle': ScanDeviceDataset(self.stt),
            'rotation_angle': ScanDeviceDataset(self.sth),
            'qh': ScanDeviceDataset('h', units=nounit, axis=axis1),
            'qk': ScanDeviceDataset('k', units=nounit, axis=axis1),
            'ql': ScanDeviceDataset('l', units=nounit, axis=axis1),
            'en': ScanDeviceDataset('E', axis=axis1),
        })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'ei': NXLink(f'/{self.entry}/{self.instrument}/monochromator/ei'),
            'ef': NXLink(f'/{self.entry}/{self.instrument}/analyser/ef'),
            'en': NXLink(f'/{self.entry}/{self.sample}/en'),
            'qh': NXLink(f'/{self.entry}/{self.sample}/qh'),
            'qk': NXLink(f'/{self.entry}/{self.sample}/qk'),
            'ql': NXLink(f'/{self.entry}/{self.sample}/ql'),
            'None': NXScanLink(),
        })

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'comment': DeviceDataset('Exp', 'remark'),
        })
