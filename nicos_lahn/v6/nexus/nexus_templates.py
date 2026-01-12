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
#   Facundo Silberstein <facundosilberstein@cnea.gob.ar>
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
# *****************************************************************************

from nicos.nexus.elements import ConstDataset, DetectorDataset, DeviceDataset, \
    ImageDataset, NXLink, NXTime
from nicos.nexus.nexussink import NexusTemplateProvider
from nicos import session
from nicos_lahn.commands.secoplist import ListSecopDevices

sample_entry = {
    "name": DeviceDataset('Sample', 'samplename'),
    "y_translation": DeviceDataset('y'),
    "z_translation": DeviceDataset('z'),
    "high_s_translation": DeviceDataset('high_s'),
}
if "sampletable_1" in session.loaded_setups:
    sample_entry["rotation_angle"] = DeviceDataset('chi')
    sample_entry["omega_s_rotation"] = DeviceDataset('omega_s')

rnp_default = {
    "NeXus_Version": "nexusformat v0.5.3",
    "instrument": "RNP",
    "owner": DeviceDataset('RNP', 'responsible'),
    "entry:NXentry": {
        "title": DeviceDataset('Exp', 'title'),
        "proposal_id": DeviceDataset('Exp', 'proposal'),
        "start_time": NXTime(),
        "end_time": NXTime(),
        "user:NXuser": {
            "name": DeviceDataset('Exp', 'users'),
            "email": DeviceDataset('Exp', 'localcontact'),
        },
        "RNP:NXinstrument": {
            "source:NXsource": {
                "type": ConstDataset('Reactor Neutron Source', 'string'),
                "name": ConstDataset('RA10', 'string'),
                "probe": ConstDataset('neutron', 'string'),
            },
            "detector:NXdetector": {
                "polar_angle": DeviceDataset('delta_d'),
                "data": ImageDataset(0, 0),
            },
            "monochromator:NXmonochromator": {
                "wavelength": DeviceDataset('wavelength', dtype='float',
                                            units='angstrom'),
            }
        },
        "sample:NXsample": sample_entry,
        "monitor:NXmonitor": {
            "mode": ConstDataset('timer', 'string'),
            "preset": DetectorDataset('timer', 'float32'),
            "integral": DetectorDataset('monitor', 'int32'),
        },
        "data:NXdata": {
            "data": NXLink('/entry/RNP/detector/data'),
        },
    }
}

devices = ListSecopDevices()
node_info = devices[0]

sample_environment = {}

for mod_info in devices[1:]:
    sample_environment[f"{mod_info['name']}:NXsensor"] = {
        "name": ConstDataset(node_info['name'], 'string'),
        "measurement": ConstDataset(mod_info['description'], 'string'),
        "value": DeviceDataset(mod_info['name']),
    }


class RNPTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        if 'sample_environment' in session.loaded_setups:
            rnp_default["entry:NXentry"]["sample_environment:NXenvironment"] = sample_environment
        return rnp_default
