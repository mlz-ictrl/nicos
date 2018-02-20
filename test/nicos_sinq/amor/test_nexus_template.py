#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

import pytest

from nicos.pycompat import iteritems
from nicos_ess.nexus.elements import NXGroup, NXDataset, NXAttribute, \
    DeviceDataset, DeviceAttribute, EventStream
from nicos_ess.nexus.converter import NexusTemplateConverter

session_setup = 'sinq_amor_system'

# Dummy metainfo of a device
metainfo = {
    ('dev1', 'value'): (1.0, '1.000', 'unit', 'general'),
    ('dev1', 'status'): ((200, 'Ok'), 'ok: Ok', '', 'status'),
    ('dev1', 'parstr'): ('parstr', 'parstr', '', 'general'),
    ('dev1', 'parint'): (1, '1', 'int', 'general'),
}

# Various Nexus elements mapped to their JSON structures
elements = {
    ('attribute_explicit', NXAttribute(1.0)):
        {'attribute_explicit': 1.0
         },
    ('attribute_dev', DeviceAttribute('dev1')):
        {'attribute_dev': 1.0
         },
    ('dataset', NXDataset(1.0, unit="unit")):
        {'values': 1.0,
         'type': 'dataset',
         'name': 'dataset',
         'attributes': {'unit': 'unit'}
         },
    ('dataset_float', DeviceDataset('dev1')):
        {'values': 1.0,
         'type': 'dataset',
         'name': 'dataset_float',
         'attributes': {
             'nicos_name': 'dev1',
             'units': 'unit',
             'nicos_param': 'value'}
         },
    ('dataset_int', DeviceDataset('dev1', 'parint')):
        {'values': 1,
         'type': 'dataset',
         'name': 'dataset_int',
         'attributes': {
             'nicos_name': 'dev1',
             'units': 'int',
             'nicos_param': 'parint'}
         },
    ('dataset_str', DeviceDataset('dev1', 'parstr')):
        {'values': 'parstr',
         'attributes': {
             'nicos_name': 'dev1',
             'nicos_param': 'parstr'},
         'type': 'dataset',
         'name': 'dataset_str',
         'dataset': {
             'string_size': 7,
             'type': 'string'}
         },
    ('event_stream', EventStream(topic='topic', source='source',
                                 broker="localhost:9092", type="uint32")):
        {'attributes': {'NX_class': 'NXevent_data'},
         'type': 'group',
         'name': 'event_stream',
         'children':
             [{
                 'attributes': {'type': 'uint32'},
                 'type': 'stream',
                 'stream': {'topic': 'topic', 'source': 'source',
                            'type': 'uint64',
                            'broker': 'localhost:9092',
                            'module': 'ev42'}}]
         },
    ('group_normal', NXGroup('NXgroup')):
        {'attributes': {'NX_class': 'NXgroup'},
         'type': 'group',
         'name': 'group_normal',
         'children': []
         },
}

# A dummy template to be tested
template = {
    'group_dict:NXgroup': {
        'attr': 'top_attr',
        'child_group:NXchild': {
            'child_child_attr': 1.0
        },
        'child_dataset': NXDataset(1.0, unit="unit"),
    }
}

# Converted structure from the dummy template
converted = {
    "attributes": {"NX_class": "NXroot"},
    "children": [
        {
            "attributes": {"attr": "top_attr", "NX_class": "NXgroup"},
            "type": "group",
            "name": "group_dict",
            "children": [
                {
                    "attributes": {"child_child_attr": 1.0,
                                   "NX_class": "NXchild"},
                    "type": "group",
                    "name": "child_group",
                    "children": []
                },
                {
                    "values": 1.0,
                    "type": "dataset",
                    "name": "child_dataset",
                    "attributes": {"unit": "unit"}
                }
            ]
        }
    ]
}


class TestNexusTemplate(object):
    """ Tests to check if the NeXus templates are converted correctly
    """

    @staticmethod
    def equals(dict1, dict2):
        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            return False
        for key, value in iteritems(dict1):
            if key not in dict2:
                return False
            if (isinstance(value, dict) and
                    not TestNexusTemplate.equals(value, dict2[key])):
                return False
            if value != dict2[key]:
                return False

        return True

    @pytest.mark.parametrize("element", elements.keys())
    def test_element_provides_correct_json(self, element):
        """ Test that elements provide correct JSON structures
        """
        name, elem = element
        assert self.equals(elem.structure(name, metainfo), elements[element])

    def test_template_conversion_to_json(self, session):
        """ Test that template is correctly converted to JSON format
        """
        converter = NexusTemplateConverter()
        assert self.equals(converter.convert(template, metainfo), converted)
