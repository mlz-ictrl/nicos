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
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#
# *****************************************************************************
import copy
import json
import time

from nicos import session
from nicos.core import Device, NicosError, Override, Param, relative_path
from nicos.core.device import DeviceParInfo

from nicos_sinq.nexus.converter import NexusTemplateConverter


class NexusStructureProvider(Device):

    parameter_overrides = {
        'visibility':
            Override(default=()),
    }

    def get_structure(self, dataset):
        raise NotImplementedError('must implement get_structure method')


class NexusStructureJsonFile(NexusStructureProvider):
    parameters = {
        'nexus_config_path':
            Param('NeXus configuration filepath',
                  type=relative_path,
                  mandatory=True,
                  userparam=True,
                  settable=True),
    }

    def get_structure(self, dataset):
        structure = self._load_structure()
        structure = self._filter_structure(structure)
        structure = self._insert_metadata(
            structure,
            dataset.metainfo,
            dataset.counter,
        )
        return structure

    def _load_structure(self):
        with open(self.nexus_config_path, 'r', encoding='utf-8') as file:
            structure = file.read()
        return structure

    def _filter_structure(self, structure):
        loaded_devices = [str(dev) for dev in session.devices]
        nexus_alias = session.getDevice('NexusStructure').alias

        structure = json.loads(structure)
        self._filter_items(structure, self._are_required_devices_loaded,
                           loaded_devices)
        self._filter_items(structure, self._is_nexus_alias_correct,
                           nexus_alias)
        return json.dumps(structure)

    def _filter_items(self, data, condition_func, condition_arg):
        data['children'] = [
            item for item in data['children']
            if condition_func(item, condition_arg)
            ]

        for item in data['children']:
            if 'children' in item:
                self._filter_items(item, condition_func, condition_arg)

    def _are_required_devices_loaded(self, item, loaded_devices):
        if not isinstance(item, dict) or 'required_devices' not in item:
            return True

        return all(
            dev in loaded_devices
            for dev in item['required_devices']
        )

    def _is_nexus_alias_correct(self, item, nexus_alias):
        if not isinstance(item, dict) or not item.get('required_nexus'):
            return True

        return item['required_nexus'] == nexus_alias

    def _insert_metadata(self, structure, metainfo, counter):
        structure = structure.replace('$TITLE$', metainfo[('Exp', 'title')][0])
        structure = structure.replace('$EXP_ID$',
                                      metainfo[('Exp', 'proposal')][0])
        structure = structure.replace('$ENTRY_ID$', str(counter))
        structure = structure.replace('$JOB_ID$',
                                      metainfo[('Exp', 'job_id')][0])
        structure = self._insert_users(structure, metainfo)
        structure = self._insert_samples(structure, metainfo)
        return structure

    def _generate_nxclass_template(self,
                                   nx_class,
                                   prefix,
                                   entities,
                                   skip_keys=None):
        temp = []
        for entity in entities:
            entity_name = entity.get('name', '').replace(' ', '')
            if not entity_name:
                continue

            result = {
                'type': 'group',
                'name': f'{prefix}_{entity_name}',
                'attributes': {
                    'NX_class': nx_class
                },
                'children': [],
            }
            for n, v in entity.items():
                if skip_keys and n in skip_keys:
                    continue
                result['children'].append({
                    'module': 'dataset',
                    'config': {
                        'name': n,
                        'values': v,
                        'dtype': 'string'
                    }
                })
            temp.append(json.dumps(result))
        return ','.join(temp) if temp else ''

    def _insert_samples(self, structure, metainfo):
        samples_info = metainfo.get(('Sample', 'samples'))
        if not samples_info:
            return structure

        samples_str = self._generate_nxclass_template(
            'NXsample', 'sample', samples_info[0].values(),
            skip_keys=['number_of'])

        if samples_str:
            structure = structure.replace('"$SAMPLES$"', samples_str)
        return structure

    def _insert_users(self, structure, metainfo):
        users_str = self._generate_nxclass_template(
            'NXuser',
            'user',
            metainfo[('Exp', 'users')][0],
        )
        if users_str:
            structure = structure.replace('"$USERS$"', users_str)
        return structure


class NexusStructureAreaDetector(NexusStructureJsonFile):
    """
    This class adds some extra consideration to instrument setups with
    area detectors with changing image size (e.g. neutron or light tomography).
    """
    parameters = {
        'area_det_collector_device':
            Param('Area collector device name',
                  type=str,
                  mandatory=True,
                  userparam=True,
                  settable=True),
    }

    def get_structure(self, dataset):
        structure = NexusStructureJsonFile._load_structure(self)
        structure = NexusStructureJsonFile._insert_metadata(
            self,
            structure,
            dataset.metainfo,
            dataset.counter,
        )
        structure = self._add_area_detector_array_size(structure)
        return structure

    def _add_area_detector_array_size(self, structure):
        structure = json.loads(structure)
        self._replace_area_detector_placeholder(structure)
        return json.dumps(structure)

    def _replace_area_detector_placeholder(self, data):
        for item in data['children']:
            if 'config' in item and 'array_size' in item['config']:
                if item['config']['array_size'] == '$AREADET$':
                    item['config']['array_size'] = []
                    for val in self._get_detector_device_array_size(
                            item['config']):
                        item['config']['array_size'].append(val)
            if 'children' in item:
                self._replace_area_detector_placeholder(item)

    def _get_detector_device_array_size(self, json_config):
        area_detector_collector = session.getDevice(
            self.area_det_collector_device)
        return area_detector_collector.get_array_size(json_config['topic'],
                                                      json_config['source'])


class NexusStructureTemplate(NexusStructureProvider):
    parameters = {
        'templatesmodule':
            Param('Python module containing NeXus nexus_templates',
                  type=str,
                  mandatory=True),
        'templatename':
            Param('Template name from the nexus_templates module',
                  type=str,
                  mandatory=True),
    }

    _templates = []
    _template = None

    def doInit(self, mode):
        self.log.info(self.templatesmodule)
        self._templates = __import__(self.templatesmodule,
                                     fromlist=[self.templatename])
        self.log.info('Finished importing nexus_templates')
        self.set_template(self.templatename)

    def set_template(self, val):
        """
        Sets the template from the given template modules.
        Parses the template using *parserclass* method parse. The parsed
        root, event kafka streams and device placeholders are then set.
        :param val: template name
        """
        if not hasattr(self._templates, val):
            raise NicosError('Template %s not found in module %s' %
                             (val, self.templatesmodule))

        self._template = getattr(self._templates, val)

        if self.templatename != val:
            self._setROParam('templatename', val)

    def _add_start_time(self, dataset):
        if ('dataset', 'starttime') not in dataset.metainfo:
            start_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(dataset.started))
            dataset.metainfo[('dataset', 'starttime')] = DeviceParInfo(start_time, start_time, '', 'general')

    def get_structure(self, dataset):
        template = copy.deepcopy(self._template)
        self._add_start_time(dataset)
        converter = NexusTemplateConverter()
        structure = converter.convert(template, dataset.metainfo)
        return json.dumps(structure)
