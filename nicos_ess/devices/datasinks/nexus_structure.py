#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
import copy
import json
import time

from nicos.core import Device, NicosError, Override, Param, relative_path

from nicos_ess.nexus.converter import NexusTemplateConverter


class NexusStructureProvider(Device):

    parameter_overrides = {
        'lowlevel': Override(default=True),
    }

    def get_structure(self, dataset, start_time):
        raise NotImplementedError('must implement get_structure method')


class NexusStructureJsonFile(NexusStructureProvider):
    parameters = {
        'nexus_config_path': Param('NeXus configuration filepath',
            type=relative_path, mandatory=True, userparam=True, settable=True),
    }

    def get_structure(self, dataset, start_time):
        with open(self.nexus_config_path, 'r', encoding='utf-8') as file:
            structure = file.read()
        return self._insert_metadata(structure, dataset.metainfo)

    def _insert_metadata(self, structure, metainfo):
        structure = structure.replace('$TITLE$', metainfo[('Exp', 'title')][0])
        structure = structure.replace('$EXP_ID$',
                                      metainfo[('Exp', 'proposal')][0])
        structure = self._insert_users(structure, metainfo)
        return structure

    def _insert_users(self, structure, metainfo):
        users = []
        for user in metainfo[('Exp', 'users')][0]:
            username = user.get('name', '').replace(" ", "")
            if not username:
                continue

            result = {
                'type': 'group',
                'name': f'user_{username}',
                'attributes': {'NX_class': 'NXuser'},
                'children': [],
            }
            for n, v in user.items():
                result['children'].append(
                    {
                        'module': 'dataset',
                        'config': {
                            'name': n,
                            'values': v,
                            'dtype': 'string'
                        }
                    }
                )

            users.append(json.dumps(result))
        users_str = ','.join(users) + ',' if users else ''
        return structure.replace('$USERS$', users_str)


class NexusStructureTemplate(NexusStructureProvider):
    parameters = {
        'templatesmodule': Param(
            'Python module containing NeXus nexus_templates',
            type=str, mandatory=True),
        'templatename': Param('Template name from the nexus_templates module',
            type=str, mandatory=True),
    }

    _templates = []
    _template = None

    def doInit(self, mode):
        self.log.info(self.templatesmodule)
        self._templates = __import__(
            self.templatesmodule, fromlist=[self.templatename]
        )
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
            raise NicosError(
                'Template %s not found in module %s'
                % (val, self.templatesmodule)
            )

        self._template = getattr(self._templates, val)

        if self.templatename != val:
            self._setROParam('templatename', val)

    def _add_start_time(self, dataset):
        if ('dataset', 'starttime') not in dataset.metainfo:
            start_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime(dataset.started))
            dataset.metainfo[('dataset', 'starttime')] = (start_time,
                                                          start_time,
                                                          '', 'general')

    def get_structure(self, dataset, start_time):
        template = copy.deepcopy(self._template)
        self._add_start_time(dataset)
        converter = NexusTemplateConverter()
        structure = converter.convert(template, dataset.metainfo)
        return json.dumps(structure)
