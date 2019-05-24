#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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


from nicos.nexus.elements import ConstDataset, DeviceAttribute, \
    DeviceDataset, NXAttribute
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_mlz.toftof.devices.datasinks.elements import DetInfo, Duration, \
    ElasticPeakGuess, EndTime, EntryIdentifier, ExperimentTitle, FileName, \
    GonioDataset, HVDataset, List, LVDataset, Mode, MonitorData, MonitorRate, \
    MonitorTof, MonitorValue, SampleCountRate, SampleCounts, StartTime, \
    Status, TableDataset, TOFTOFImageDataset, ToGo

seconds = NXAttribute('s', 'string')
signal = NXAttribute(1, 'int64')


class TofTofNexusLegacyTemplate(NexusTemplateProvider):

    def getTemplate(self):
        return {
            'NeXus_Version': '4.3.0',
            'instrument': 'TOFTOF',
            'owner': DeviceAttribute('TOFTOF', 'responsible'),
            'Scan:NXentry': {
                'wavelength': DeviceDataset('chWL', dtype='float32'),
                'title': DeviceDataset('det', 'usercomment'),
                'proposal': DeviceDataset('Exp', 'title'),
                'proposal_number': DeviceDataset('Exp', 'proposal'),
                'experiment_identifier': ExperimentTitle(),
                'entry_identifier': EntryIdentifier(),
                'start_time': StartTime(),
                'end_time': EndTime(),
                'duration': Duration(),
                'FileName': FileName(),
                'instrument:NXinstrument': {
                    'name': ConstDataset('TOFTOF', 'string'),
                    'platform': ConstDataset('Linux', 'string'),
                    'chopper:NXchopper': {
                        'crc': DeviceDataset('chCRC', dtype='float32'),
                        'delay': DeviceDataset('det', 'delay'),
                        'num_of_channels': DeviceDataset('det',
                                                         'timechannels'),
                        'num_of_detectors': DeviceDataset('det', 'numinputs'),
                        'ratio': DeviceDataset('chRatio'),
                        'rotation_speed': DeviceDataset('ch'),
                        'slit_type': DeviceDataset('chST'),
                        'tof_ch5_90deg_offset': DeviceDataset(
                            'ch', 'ch5_90deg_offset'),
                        'tof_num_inputs': DeviceDataset('det', 'numinputs'),
                        'tof_time_preselection': DeviceDataset('det', 'preset',
                                                               units=seconds),
                    },
                    'detector:NXdetector': {
                        'box_chan': DetInfo(15),
                        'box_nr': DetInfo(14),
                        'det_plate': DetInfo(2),
                        'det_pos': DetInfo(3),
                        'det_rack': DetInfo(1),
                        'det_rpos': DetInfo(4),
                        'detector_number': DetInfo(0),
                        'ele_card': DetInfo(10),
                        'ele_chan': DetInfo(11),
                        'ele_total': DetInfo(12),
                        'pixel_mask': DetInfo(13),
                        'polar_angle': DetInfo(5),
                    },
                    'chopper_vac0': DeviceDataset('vac0'),
                    'chopper_vac1': DeviceDataset('vac1'),
                    'chopper_vac2': DeviceDataset('vac2'),
                    'chopper_vac3': DeviceDataset('vac3'),
                    'goniometer_phicxcy': GonioDataset(),
                    'goniometer_xyz': TableDataset(),
                    'hv_power_supplies': HVDataset(),
                    'lv_power_supplies': LVDataset(),
                },
                'mode': Mode(),
                'status': Status(),
                'to_go': ToGo(),
                # 'slit_hg': DeviceDataset('slit.centerx'),
                # 'slit_ho': DeviceDataset('slit.centery'),
                # 'slit_vg': DeviceDataset('slit.width'),
                # 'slit_vo': DeviceDataset('slit.height'),
                'user1:NXuser': {
                    'name': DeviceDataset('Exp', 'localcontact'),
                    'role': ConstDataset('local_contact', 'string'),
                },
                'user2:NXuser': {
                    'name': DeviceDataset('Exp', 'users'),
                    'role': ConstDataset('experiment_team', 'string'),
                },
                'sample:NXSample': {
                    'description': DeviceDataset('Sample', 'samplename'),
                    'total_counts': SampleCounts(),
                    'total_count_rate': SampleCountRate(),
                },
                'monitor:NXmonitor': {
                    'tof_monitor_input': DeviceDataset('det',
                                                       'monitorchannel'),
                    'tof_time_interval': DeviceDataset('det', 'timeinterval'),
                    'data': MonitorData(),
                    'elastic_peak': ElasticPeakGuess(),
                    'integral': MonitorValue(),
                    'monitor_count_rate': MonitorRate(),
                    'time_of_flight': MonitorTof(),
                },
                'data:NXdata': {
                    'channel_number': List(0, 1023),
                    'data': TOFTOFImageDataset(
                        0, 0, signal=signal, units='counts',
                        axes='2theta:channel_number'),
                    'polar_angle': DetInfo(5),
                },
            },
        }
