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
#   Kirill Pshenichnyi <pshcyrill@mail.ru>
#
# *****************************************************************************

""" Nexus template for NERO machine """

from nicos import session
from nicos.nexus.elements import DetectorDataset, DeviceAttribute, \
    DeviceDataset, ImageDataset
from nicos.nexus.nexussink import NexusTemplateProvider

from nicos_mlz.toftof.devices.datasinks.elements import EndTime, StartTime
from nicos_pnpi.nero.devices.datasinks.elements import FileName


class NxTemplateCount(NexusTemplateProvider):

    def getTemplate(self):
        template = {
            'NeXus_Version': 'nexusformat v0.5.3',
            'instrument': DeviceAttribute('Instrument', 'instrument'),
            'owner': DeviceAttribute('Instrument', 'responsible'),
            'users': DeviceAttribute('Exp', 'users'),
            'entry:NXentry': {
                'start_time': StartTime(),
                'end_time': EndTime(),
                'FileName': FileName(),
                'data:NXdata': {
                    'data': ImageDataset(0, 0),
                    'units': DeviceAttribute('det1_img', 'unit'),
                },
                'NERO:NXinstrument': {
                    'collimator:NXcollimator': {
                        'width': DeviceDataset('x_gap',
                                               'curvalue',
                                               dtype='float32',
                                               unit=session.getDevice(
                                                   'x_gap'
                                               ).unit),
                        'height': DeviceDataset('y_gap',
                                                'curvalue',
                                                dtype='float32',
                                                unit=session.getDevice(
                                                    'y_gap'
                                                ).unit),
                        'theta_s': DeviceDataset('theta_s',
                                                 'curvalue',
                                                 dtype='float32',
                                                 unit=session.getDevice(
                                                     'theta_s'
                                                 ).unit),
                        'x_s': DeviceDataset('x_s',
                                             'curvalue',
                                             dtype='float32',
                                             unit=session.getDevice(
                                                 'x_s'
                                             ).unit),
                        'dia1_angle': DeviceDataset('dia1_angle',
                                                    'curvalue',
                                                    dtype='float32',
                                                    unit=session.getDevice(
                                                        'dia1_angle'
                                                    ).unit),
                        'dia1_pos': DeviceDataset('dia1_pos',
                                                  'curvalue',
                                                  dtype='float32',
                                                  unit=session.getDevice(
                                                      'dia1_pos'
                                                  ).unit),
                        'dia2_angle': DeviceDataset('dia2_angle',
                                                    'curvalue',
                                                    dtype='float32',
                                                    unit=session.getDevice(
                                                        'dia1_angle'
                                                    ).unit),
                        'dia2_pos': DeviceDataset('dia2_pos',
                                                  'curvalue',
                                                  dtype='float32',
                                                  unit=session.getDevice(
                                                      'dia1_pos'
                                                  ).unit),
                        'fa': DeviceDataset('fa'),
                        'fb': DeviceDataset('fb'),
                    },
                    'monochromator:NXcrystal': {
                        'chi1': DeviceDataset('chi1',
                                              'curvalue',
                                              dtype='float32',
                                              unit=session.getDevice(
                                                  'chi1'
                                              ).unit),
                        'chi2': DeviceDataset('chi2',
                                              'curvalue',
                                              dtype='float32',
                                              unit=session.getDevice(
                                                  'chi2'
                                              ).unit),
                        'chi3': DeviceDataset('chi3',
                                              'curvalue',
                                              dtype='float32',
                                              unit=session.getDevice(
                                                  'chi3'
                                              ).unit),
                        'chi4': DeviceDataset('chi4',
                                              'curvalue',
                                              dtype='float32',
                                              unit=session.getDevice(
                                                  'chi4'
                                              ).unit),
                        'omega': DeviceDataset('omega',
                                               'curvalue',
                                               dtype='float32',
                                               unit=session.getDevice(
                                                   'omega'
                                               ).unit),
                        'x': DeviceDataset('x_mon',
                                           'curvalue',
                                           dtype='float32',
                                           unit=session.getDevice(
                                               'x_mon'
                                           ).unit),
                        'y': DeviceDataset('y_mon',
                                           'curvalue',
                                           dtype='float32',
                                           unit=session.getDevice(
                                               'y_mon'
                                           ).unit),
                        'shutter': DeviceDataset('shutter'),
                    }
                },
                'monitor:NXmonitor': {
                    'monitor': DetectorDataset('det1_mon1',
                                               dtype='int',
                                               unit=session.getDevice(
                                                   'det1_mon1'
                                               ).unit),
                    'fdetecor': DetectorDataset('fdet1',
                                                dtype='int',
                                                unit=session.getDevice(
                                                    'fdet1'
                                                ).unit),
                },
                'sample:NXsample': {
                    'samplename': DeviceAttribute('Sample', 'samplename'),
                    'alpha': DeviceDataset('alpha',
                                           'curvalue',
                                           dtype='float32',
                                           unit=session.getDevice(
                                               'alpha'
                                           ).unit),
                    'magnet_field': DeviceDataset('B',
                                                  'curvalue',
                                                  dtype='float32',
                                                  unit=session.getDevice(
                                                      'B'
                                                  ).unit),
                },
            },
        }
        return template
