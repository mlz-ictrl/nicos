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
#   Mark.Koennecke@psi.ch
#
# *****************************************************************************
from copy import deepcopy

from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceAttribute, \
    DeviceDataset, NamedImageDataset, NexusSampleEnv, NXAttribute, NXLink, \
    NXScanLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_sinq.nexus.specialelements import AbsoluteTime

icon_default = {'NeXus_Version': '4.4.0',
                'instrument': 'ICON at SINQ',
                'owner': DeviceAttribute('ICON', 'responsible'),
                'entry:NXentry': {
                    'title': DeviceDataset('Exp', 'title'),
                    'proposal_title': DeviceDataset('Exp', 'title'),
                    'proposal_id': DeviceDataset('Exp', 'proposal'),
                    'start_time': NXTime(),
                    'end_time': NXTime(),
                    'definition': ConstDataset('NXtomo', 'string'),
                    'user:NXuser': {
                        'name': DeviceDataset('Exp', 'users'),
                        'email': DeviceDataset('Exp', 'localcontact')
                    },
                    'proposal_user:NXuser': {
                        'name': DeviceDataset('Exp', 'users'),
                    },
                    'control:NXmonitor': {
                        'data': DeviceDataset('beam_current'),
                        'count_time': DeviceDataset('exp_time'),
                    }
                }  # entry
                }  # root

sample_common = {
    'name': DeviceDataset('Sample', 'samplename'),
    'hugo': NexusSampleEnv(),
    'temperature': DeviceDataset('temperature', 'value', defaultval=0.0),
    'magfield': DeviceDataset('magfield', 'value', defaultval=0.0),
}

instrument = {
    'sinq:NXsource': {
        'name': ConstDataset('SINQ', 'string'),
        'probe': ConstDataset('neutron', 'string'),
        'type': ConstDataset('continuous flux spallation neutron source',
                             'string'),
    }
}


class ICONTemplateProvider(NexusTemplateProvider):
    _tables = ['sample_pos1', 'sample_pos2', 'sample_pos3']
    _detector = None
    _detector_setups = ['andor', 'simad', 'simad2']
    _excluded_devices = ['shuttersink', 'he_sopen', 'he_sclose',
                         'he_ropen', 'he_rclose', 'he_renabled',
                         'he_popen', 'he_pclose', 'fs_sopen',
                         'fs_sclose', 'fs_ropen', 'fs_rclose',
                         'fs_renabled', 'fs_popen', 'fs_pclose',
                         'exp_sopen', 'exp_slcose', 'exp_sslow',
                         'exp_sfast', 'exp_ropen', 'exp_rclose',
                         'exp_renabled', 'exp_rfast', 'exp_popen',
                         'exp_pclose', 'exp_pslow', 'exp_pfast',
                         'bl1', 'bl2']
    _detectors = set()

    def containsDetector(self, table):
        dets = []
        for det in self._detector_setups:
            if det in table.setups:
                dets.append(det)
        return dets

    def makeTable(self, table_name):
        table = session.getDevice(table_name)
        det = self.containsDetector(table)
        for d in det:
            self._detectors.add(d)
            table.detach(d)
        devices = table.getTableDevices()
        content = {}
        for d in devices:
            if d in self._excluded_devices:
                continue
            try:
                dev = session.getDevice(d)
                content[dev.name] = DeviceDataset(dev.name,
                                                  units=NXAttribute(dev.unit,
                                                                    'string'))
            except Exception as e:
                session.log.info('Failed to write device %s, Exception: %s',
                                 d, e)
        equipment = ','.join(table.setups)
        content['equipment'] = ConstDataset(equipment, 'string')
        for d in det:
            table.attach(d)
            content['detector'] = ConstDataset(d, 'string')
        return content

    def makeDetector(self, name):
        content = {}
        content['image_key'] = DeviceDataset('image_key', dtype='int32')
        content['x_pixel_size'] = DeviceDataset('pixel_size')
        content['y_pixel_size'] = DeviceDataset('pixel_size')
        content['distance'] = DeviceDataset('detector_distance')
        content['lens'] = DeviceDataset('lenses')
        content['sensor_material'] = DeviceDataset('scintillator')
        content['sensor_thickness'] = DeviceDataset('scintillator_thickness')
        content['data'] = NamedImageDataset('%s_image' % name,
                                            signal=NXAttribute(1, 'int32'))
        content['time_stamp'] = AbsoluteTime()
        return name, content

    def makeData(self, name):
        content = {}
        content['data'] = NXLink('/entry/%s/data' % (name))
        content['image_key'] = NXLink('/entry/%s/image_key' % name)
        content['None'] = NXScanLink()
        return content

    def _find_rotation_angle(self):
        rot_link = None
        try:
            session.getDevice('sp2_ry')
            rot_link = '/entry/sample_pos2/sp2_ry'
        except Exception:
            pass
        try:
            session.getDevice('sp3_ry')
            rot_link = '/entry/sample_pos3/sp3_ry'
        except Exception:
            pass
        return rot_link

    def getTemplate(self):
        self._detectors = set()
        full = deepcopy(icon_default)
        entry = full['entry:NXentry']
        entry['sample:NXsample'] = deepcopy(sample_common)
        # Find the rotation angle
        rot_link = self._find_rotation_angle()
        if rot_link:
            entry['sample:NXsample']['rotation_angle'] = NXLink(rot_link)
        for tbl in self._tables:
            tblcontent = self.makeTable(tbl)
            entry[tbl.lower() + ':NXcollection'] = tblcontent
        detcontent = self.makeTable('detector_pos')
        for det in self._detectors:
            name, content = self.makeDetector(det)
            content.update(detcontent)
            entry[name + ':NXdetector'] = content
            entry['data' + name + ':NXdata'] = self.makeData(name)
            if rot_link:
                entry['data' + name + ':NXdata']['rotation_angle'] =\
                    NXLink(rot_link)
        if not self._detectors:
            session.log.error('Configuration error: no detectors found')
        entry['icon:NXinstrument'] = deepcopy(instrument)
        entry['icon:NXinstrument'][name] = NXLink('/entry/' + name)
        return full
