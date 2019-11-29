#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import copy

from nicos import session

from nicos_sinq.nexus.elements import ConstDataset, DetectorDataset, \
    DeviceAttribute, DeviceDataset, ImageDataset, NexusSampleEnv, \
    NXAttribute, NXLink, NXScanLink, NXTime
from nicos_sinq.nexus.nexussink import NexusTemplateProvider


class BOATemplateProvider(NexusTemplateProvider):
    """
      NeXus template generation for BOA at SINQ
    """
    _boa_default = {"NeXus_Version": "4.3.0", "instrument": "BOA",
                    "owner": DeviceAttribute('BOA', 'responsible'),
                    "entry:NXentry": {"title": DeviceDataset('Exp', 'title'),
                                      "proposal_title": DeviceDataset('Exp',
                                                                      'title'),
                                      "proposal_id": DeviceDataset('Exp',
                                                                   'proposal'),
                                      "start_time": NXTime(),
                                      "end_time": NXTime(), "user:NXuser": {
                            "name": DeviceDataset('Exp', 'users'),
                            "email": DeviceDataset('Exp', 'localcontact')},
                                      "sample:NXsample": {

                                          "sample_name": DeviceDataset(
                                              'Sample', 'samplename'),
                                          "hugo": NexusSampleEnv(), },
                                      "control:NXmonitor": {
                                          "mode": DetectorDataset('mode',
                                                                  "string"),
                                          "Monitor": DetectorDataset(
                                              'monitorval', 'float32',
                                              units=NXAttribute('counts',
                                                                'string')),
                                          "preset": DetectorDataset('preset',
                                                                    'float32'),
                                          "time": DetectorDataset(
                                              'elapsedtime', 'float32',
                                              units=NXAttribute('seconds',
                                                                'string')), },
                                      "proton_beam:NXmonitor": {
                                          "data": DetectorDataset(
                                                   'protoncurr',
                                                   'int32',
                                                   units=NXAttribute(
                                                       'counts',
                                                       'string'))},
                                      "white_beam:NXmonitor": {
                                          "data": DetectorDataset(
                                               'monitorval',
                                               'int32',
                                               units=NXAttribute('counts',
                                                                 'string'))},
                                      }, }
    _tables = ['Table2', 'Table3', 'Table4', 'Table5', 'Table6']
    _detectors = ['embl', 'andor', 'single_el737']
    _detector = None

    def containsDetector(self, table):
        for det in self._detectors:
            if det in table.setups:
                return det
        return None

    def makeTable(self, table_name):
        table = session.getDevice(table_name)
        det = self.containsDetector(table)
        if det:
            self._detector = det
            table.removeSetup(det)
        devices = table.getTableDevices()
        content = dict()
        for d in devices:
            try:
                dev = session.getDevice(d)
                content[dev.name] = DeviceDataset(dev.name,
                                                  dtype='float32',
                                                  units=NXAttribute(dev.unit,
                                                                    'string'))
            except Exception as e:
                session.log.info('Failed to write device %s, Exception: %s',
                                 d, e)
        equipment = ','.join(table.setups)
        content['equipment'] = ConstDataset(equipment, 'string')
        if det:
            table.addSetup(det)
            content['detector'] = ConstDataset(det, 'string')
        return content

    def makeDetector(self):
        name = self._detector
        if 'single' in name:
            name = 'single'
        content = dict()
        if name == 'single':
            content['data'] = DetectorDataset('countval', 'int32',
                                              units=NXAttribute(
                                                  'counts', 'string'))
        elif name == 'andor':
            content['data'] = ImageDataset(0, 0,
                                           signal=NXAttribute(1, 'int32'))
        elif name == 'embl':
            content['data'] = ImageDataset(0, 0,
                                           signal=NXAttribute(1, 'int32'))
        return name, content

    def makeData(self, name):
        content = dict()
        content['data'] = NXLink('/entry/%s/data' % (name))
        content['None'] = NXScanLink()
        return content

    def getTemplate(self):
        boa_template = copy.deepcopy(self._boa_default)
        entry = boa_template['entry:NXentry']
        for tbl in self._tables:
            tblcontent = self.makeTable(tbl)
            entry[tbl.lower() + ':NXcollection'] = tblcontent
        if self._detector:
            name, content = self.makeDetector()
            entry[name + ':NXdetector'] = content
            entry['data:Nxdata'] = self.makeData(name)
        else:
            session.log.info('No detector FOUND! May be: check setup???')
        return boa_template
