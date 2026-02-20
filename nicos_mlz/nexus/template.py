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

"""Some convenience classes, methods for NeXus data writing."""

from nicos import session
from nicos.nexus.elements import ConstDataset, DeviceDataset, EndTime, \
    NXAttribute, NXLink, StartTime
from nicos.nexus.nexussink import NexusTemplateProvider, copy_nexus_template
from nicos.nexus.specialelements import NicosProgramDataset

from nicos_mlz.nexus import LocalContact, ReactorSource, SampleEnv, User

NeXus_version = NXAttribute('4.4.3', 'string')
NXDL_version = NXAttribute('v2024.02', 'string')


class MLZTemplateProvider(NexusTemplateProvider):

    detector = 'detector'
    entry = 'entry'
    instrument = 'instrument'
    sample = 'sample'
    version = '1.0'
    definition = ''
    source = 'source'

    def init(self, **kwargs):
        self.temp_env = kwargs.get('temp_env', ['T', 'Ts', ])
        self.magnet_env = kwargs.get('magnet_env', ['B'])
        self.stress_env = kwargs.get('stress_env', ['teload', 'tepos', 'teext', ])
        self.efield_env = kwargs.get('efield_env', [])

    def getBase(self):

        # definition_url = 'https://manual.nexusformat.org/classes/'
        #                  f'applications/{self.definition}.html'
        definition_url = 'https://github.com/nexusformat/definitions/blob/' \
                         f'main/applications/{self.definition}.nxdl.xml'

        return {
            'NeXus_version': NeXus_version,
            f'{self.entry}:NXentry': {
                'version': NXAttribute(self.version, 'string'),
                'program_name': NicosProgramDataset(),
                'title': DeviceDataset(session.experiment.name, 'title'),
                'start_time': StartTime(),
                'end_time': EndTime(),
                'definition': ConstDataset(
                    self.definition, 'string', version=NXDL_version,
                    URL=NXAttribute(definition_url, 'string')),
                'experiment_description': DeviceDataset(
                    session.experiment.name, 'title'),
                'experiment_identifier': DeviceDataset(
                    session.experiment.name, 'proposal'),
                # 'collection_identifier': ,
                # 'collection_description': ,
                # 'entry_identifier': ,
                # 'entry_identifier_uuid': ,
                # 'run_cycle': ,
                f'{self.instrument}:NXinstrument': {
                    'name': DeviceDataset(
                        session.instrument.name, 'instrument'),
                    f'{self.source}:NXsource': ReactorSource('ReactorPower'),
                    f'{self.detector}:NXdetector': {
                    },
                },
                f'{self.sample}:NXsample': {
                    'name': DeviceDataset(
                        session.experiment.sample.name, 'samplename'),
                },
                'data:NXdata': {
                    'data': NXLink(f'/{self.entry}/{self.instrument}/'
                                   f'{self.detector}/data'),
                    'signal': NXAttribute('data', 'string'),
                },
                'default': NXAttribute('data', 'string'),
            },
        }

    def updateInstrument(self):
        raise NotImplementedError

    def updateDetector(self):
        raise NotImplementedError

    def updateData(self):
        raise NotImplementedError

    def updateSample(self):
        if any(e in session.devices for e in self.temp_env):
            self._sample.update({
                'temperature_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(self.temp_env),
                },
            })
        if any(e in session.devices for e in self.magnet_env):
            self._sample.update({
                'magnetic_field_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(self.magnet_env),
                },
            })
        if any(e in session.devices for e in self.stress_env):
            self._sample.update({
                'stress_field_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(self.stress_env, 1),
                },
            })
        if any(e in session.devices for e in self.efield_env):
            self._sample.update({
                'electric_field_env:NXenvironment': {
                    'value_log:NXlog': SampleEnv(self.efield_env),
                },
            })

    def updateUsers(self):
        self._entry.update({
            'local_contact:NXuser': LocalContact(),
            'proposal_user:NXuser': User(),
        })

    def completeTemplate(self):
        """Fill `self._template` dictionary with desired NeXus structure."""
        self.updateInstrument()
        self.updateDetector()
        self.updateUsers()
        self.updateSample()
        self.updateData()

    def getTemplate(self):
        self._template = self.getBase()
        self._entry = self._template[f'{self.entry}:NXentry']
        self._inst = self._entry[f'{self.instrument}:NXinstrument']
        self._det = self._inst[f'{self.detector}:NXdetector']
        self._sample = self._entry[f'{self.sample}:NXsample']

        self.completeTemplate()
        return copy_nexus_template(self._template)
