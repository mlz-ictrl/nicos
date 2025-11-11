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

"""Nexus data template for TOFTOF."""


from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceDataset, ImageDataset, \
    NXAttribute, NXLink

from nicos_mlz.nexus import CounterMonitor, MLZTemplateProvider, \
    TimerMonitor, axis2, signal
from nicos_mlz.toftof.lib import calculations as calc
from nicos_mlz.toftof.nexus.elements import AzimutalAngles, \
    DetectorDistances, DetInfo, Duration, EntryIdentifier, MonitorMode, \
    NeutronEnergy, TimeOfFlight
from nicos_mlz.nexus.structures import Slit

# from nicos_mlz.toftof.nexus.elements import ChannelList, ElasticPeakGuess, \
#     ExperimentTitle, GonioDataset, MonitorData, MonitorRate, MonitorTof, \
#     MonitorValue, SampleCountRate, SampleCounts, Status, TableDataset, \
#     TOFTOFImageDataset

useconds = NXAttribute('us', 'string')


class TofTofTemplate(MLZTemplateProvider):

    definition = 'NXdirecttof'

    def updateInstrument(self):
        self._inst.update({
            'disk_chopper:NXdisk_chopper': {
                'rotation_speed': DeviceDataset('ch', dtype='float32'),
                'wavelength': DeviceDataset('chWL', dtype='float32'),
                'energy': NeutronEnergy(),
                # 'type': ???,
                'ratio': DeviceDataset('chRatio', dtype='int32'),
                'delay': DeviceDataset('chdelay', dtype='int32', units=useconds),
                'crc': DeviceDataset('chCRC', dtype='int32'),
                'slit_type': DeviceDataset('chST', dtype='int32'),
                'tof_ch5_90deg_offset': DeviceDataset(
                    'ch', 'ch5_90deg_offset', dtype='int32'),
                # 'num_of_detectors': DeviceDataset(
                #     'det', 'numinputs', dtype='int32'),
                # 'tof_num_inputs': DeviceDataset(
                #     'det', 'numinputs', dtype='int32'),
                # 'tof_time_preselection': DeviceDataset(
                #     'det', 'preset', dtype='float32', units=seconds),
            },
            'chopper_vacuum:NXcollection': {
                'chopper_vac0': DeviceDataset('vac0', dtype='float32'),
                'chopper_vac1': DeviceDataset('vac1', dtype='float32'),
                'chopper_vac2': DeviceDataset('vac2', dtype='float32'),
                'chopper_vac3': DeviceDataset('vac3', dtype='float32'),
            },
            'timer:NXmonitor': TimerMonitor('timer'),
            'monitor:NXmonitor': CounterMonitor('monitor'),
            'slit:NXslit': Slit('slit'),
            # 'goniometer_phicxcy': GonioDataset(),
            # 'goniometer_xyz': TableDataset(),
            # 'status': Status(),
        })

    def updateDetector(self):
        self._det.update({
            'data': ImageDataset(
                0, 0, signal=signal, units='counts'),
            # axes='2theta:detector_number'),
            'distance': DetectorDistances(),
            'time_of_flight': TimeOfFlight(),
            'polar_angle': DetInfo(5, units='deg'),
            'azimuthal_angle': AzimutalAngles(),
            'crate': DetInfo(1),
            'detector_number': DetInfo(0, axis=axis2),

            'det_arrangement:NXcollection': {
                'det_plate': DetInfo(2),
                'det_pos': DetInfo(3),
                'det_rpos': DetInfo(4),
                'ele_card': DetInfo(10),
                'ele_chan': DetInfo(11),
                'ele_total': DetInfo(12),
                'pixel_mask': DetInfo(13),
                'box_nr': DetInfo(14),
                'box_chan': DetInfo(15),
            },
            'num_of_channels': DeviceDataset('det', 'timechannels'),
            'tof_monitor_input': DeviceDataset('det', 'monitorchannel'),
            'hv_power_supplies:NXcollection': {
                f'hv{i}': DeviceDataset(f'hv{i}', dtype='float32')
                for i in range(3)
            },
            'lv_power_supplies:NXcollection': {
                f'lv{i}': DeviceDataset(f'lv{i}', dtype='string')
                for i in range(7)
            },
        })

    def updateData(self):
        det_path = f'/{self.entry}/{self.instrument}/{self.detector}'
        self._entry['data:NXdata'].update({
            'detector_number': NXLink(f'{det_path}/detector_number'),
            'time_of_flight': NXLink(f'{det_path}/time_of_flight'),
            # 'channel_number': ChannelList(),
        })

    def updateSample(self):
        self._sample.update({
            'nature': DeviceDataset(
                session.experiment.sample.name, 'nature'),
            # 'description': DeviceDataset('Sample', 'samplename'),
            # 'total_counts': SampleCounts(),
            # 'total_count_rate': SampleCountRate(),
        })

    def completeTemplate(self):
        MLZTemplateProvider.completeTemplate(self)
        self._entry.update({
            'duration': Duration('float32'),
            'run_number': EntryIdentifier(dtype='int32'),
            'pre_sample_flightpath': ConstDataset(
                calc.Lpre_sample, 'float32', units='mm'),
            'user:NXuser': {
                'name': NXLink(f'/{self.entry}/proposal_user/name'),
                'email': NXLink(f'/{self.entry}/proposal_user/email'),
                'role': NXLink(f'/{self.entry}/proposal_user/role'),
            },
            # 'proposal': DeviceDataset('Exp', 'title'),
            # 'proposal_number': DeviceDataset('Exp', 'proposal'),
            # 'experiment_identifier': ExperimentTitle(),
            # 'entry_identifier': EntryIdentifier(),
        })
        preset = session.getDevice('det').preset()
        monitor = 'monitor'
        if preset.get('timer'):
            monitor = 'timer'
        monitorlink = f'/{self.entry}/{self.instrument}/{monitor}'
        det_path = f'/{self.entry}/{self.instrument}/{self.detector}'
        self._entry.update({
            'control:NXmonitor': {
                'mode': MonitorMode(),
                # 'mode': NXLink(f'{monitorlink}/mode'),
                'preset': NXLink(f'{monitorlink}/preset'),
                'integral_counts': NXLink(
                    f'/{self.entry}/{self.instrument}/monitor/integral'),
                'data': NXLink(f'{monitorlink}/integral'),
                'distance': ConstDataset('15', dtype='float32', units='mm'),
                'time_of_flight': NXLink(f'{det_path}/time_of_flight'),
                # 'tof_time_interval': DeviceDataset('ch', 'frametime'),
                # 'data': MonitorData(),
                # 'elastic_peak': ElasticPeakGuess(),
                # 'integral': MonitorValue(),
                # 'monitor_count_rate': MonitorRate(),
                # 'time_of_flight': MonitorTof(),
            },
        })
        if monitor != 'timer':
            self._entry['control:NXmonitor'].update({
                'type': NXLink(f'{monitorlink}/type'),
            })
