# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

from nicos.nexus.elements import ConstDataset, DetectorDataset, DeviceDataset, \
    ImageDataset, NXLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider
from nicos import session

andes_default = {
    "NeXus_Version": "nexusformat v0.5.3",
    "instrument": "ANDES",
    "owner": DeviceDataset('Andes', 'responsible'),
    "entry:NXentry": {
        "title": DeviceDataset('Exp', 'title'),
        "proposal_id": DeviceDataset('Exp', 'proposal'),
        "start_time": NXTime(),
        "end_time": NXTime(),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact'),
        },
        "ANDES:NXinstrument": {
            "source:NXsource": {
                "type": ConstDataset('Reactor Neutron Source', 'string'),
                "name": ConstDataset('RA10', 'string'),
                "probe": ConstDataset('neutron', 'string'),
            },
            "detector:NXdetector": {
                "polar_angle": DeviceDataset('stt'),
                "data": ImageDataset(0, 0),
                "distance": DeviceDataset('lsd'),
            },
            "monochromator:NXmonochromator": {
                "polar_angle": DeviceDataset('mtt'),
                "crystal:NXcrystal": {
                    "type": DeviceDataset('crystal'),
                },
                "d_spacing": DeviceDataset('wavelength', 'plane'),
                "wavelength": DeviceDataset('wavelength', dtype='float',
                                            units='angstrom'),
            }
        },
        "sample:NXsample": {
            "name": DeviceDataset('Sample', 'samplename'),
            "distance": DeviceDataset('lms'),
            "x_translation": DeviceDataset('x'),
            "y_translation": DeviceDataset('y'),
            "z_translation": DeviceDataset('z'),
            "rotation_angle": DeviceDataset('phi'),
        },
        "monitor:NXmonitor": {
            "mode": ConstDataset('timer', 'string'),
            "preset": DetectorDataset('timer', 'float32'),
            "integral": DetectorDataset('monitor', 'int32'),
        },
        "data:NXdata": {
            "data": NXLink('/entry/ANDES/detector/data')
        },
    }
}

gashandling = {
    "name": ConstDataset('Gas Handling', 'string'),
    "sensor:NXsensor": {
        "measurement": ConstDataset('temperature', 'string'),
        "value": DeviceDataset('sensor'),
    }
}


class ANDESTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        if 'gashandling' in session.loaded_setups:
            andes_default["entry:NXentry"]["gashandling:NXenvironment"] = gashandling
        return andes_default
