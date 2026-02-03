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

"""Nexus data template for triple axes (TAS) applications."""

from nicos import session
from nicos.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceDataset, NXLink, NXScanLink
from nicos.nexus.specialelements import CellArray, UBMatrix

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, Reflection, \
    ScanDeviceDataset, Slit, TimerMonitor, aa, axis1, counts, nounit, signal


class TasTemplateProvider(MLZTemplateProvider):

    definition = 'NXtas'

    def init(self, **kwargs):
        self.sgu = kwargs.get('sgu', 'sgx')
        self.sgl = kwargs.get('sgl', 'sgy')
        self.stt = kwargs.get('phi', 'phi')
        self.sth = kwargs.get('psi', 'psi')
        self.ana = kwargs.get('ana', 'ana')
        self.mono = kwargs.get('mono', 'mono')
        self.mth = kwargs.get('mth', 'mth')
        self.mtt = kwargs.get('mtt', 'mtt')
        self.ath = kwargs.get('ath', 'ath')
        self.att = kwargs.get('att', 'att')
        self.ei = kwargs.get('ei', 'Ei')
        self.ef = kwargs.get('ef', 'Ef')
        self.ss1 = kwargs.get('ss1', 'ss1')
        self.ss2 = kwargs.get('ss2', 'ss2')
        self.ms = kwargs.get('ms', 'ms1')
        self.detector = kwargs.get('detector', 'det')
        self.monitor = kwargs.get('monitor', 'mon1')
        self.timer = kwargs.get('timer', 'timer')

    def updateInstrument(self):
        self._inst.update({
            'monochromator:NXcrystal': {
                'usage': ConstDataset('Bragg', 'string'),
                'type': DeviceDataset(self.mono, 'material'),
                'd_spacing': DeviceDataset(self.mono, 'dvalue', units=aa),
                'reflection': Reflection(self.mono),
                'rotation_angle': ScanDeviceDataset(self.mth),
                'polar_angle': ScanDeviceDataset(self.mtt),
                'ei': ScanDeviceDataset(self.ei, axis=axis1),
                'wavelength': DeviceDataset(self.mono, unit='A-1'),
                'focus_mode': DeviceDataset(self.mono, 'focmode', dtype='string'),
            },
            'analyser:NXcrystal': {
                'usage': ConstDataset('Bragg', 'string'),
                'type': DeviceDataset(self.ana, 'material'),
                'd_spacing': DeviceDataset(self.ana, 'dvalue', units=aa),
                'reflection': Reflection(self.ana),
                'rotation_angle': ScanDeviceDataset(self.ath),
                'polar_angle': ScanDeviceDataset(self.att),
                'ef': ScanDeviceDataset(self.ef, axis=axis1),
                'wavelength': DeviceDataset(self.ana, units='A-1'),
                'focus_mode': DeviceDataset(self.ana, 'focmode', dtype='string'),
            },
        })
        for slit, name in ((self.ss1, 'ss1'),
                           (self.ss2, 'ss2'),
                           (self.ms, 'ms'),):
            if slit in session.devices:
                self._inst.update({f'{name}:NXslit': Slit(slit)})

    def updateDetector(self):
        self._det.update({
            'polar_angle': ScanDeviceDataset(self.att),
            'data': DetectorDataset(self.detector, dtype='int', units=counts,
                                    signal=signal),
        })
        self._entry.update({
            f'{self.monitor}:NXmonitor': CounterMonitor(self.monitor),
            f'{self.timer}:NXmonitor': TimerMonitor(self.timer),
        })
        preset = session.getDevice(self.detector).preset()
        if preset.get(self.monitor):
            monitor = self.monitor
        else:
            monitor = self.timer
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
            'sgu': ScanDeviceDataset(self.sgu),
            'sgl': ScanDeviceDataset(self.sgl),
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
