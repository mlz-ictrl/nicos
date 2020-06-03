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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

import pytest

pytest.importorskip('graypy')

from nicos_ess.nexus.converter import NexusTemplateConverter
from nicos_ess.nexus.elements import DeviceAttribute, DeviceDataset, \
    EventStream, NXAttribute, NXDataset, NXGroup

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
         'dataset': {
             'size': [1]
         },
         'attributes': {'unit': 'unit'}
         },
    ('dataset_float', DeviceDataset('dev1')):
        {'values': 1.0,
         'type': 'dataset',
         'name': 'dataset_float',
         'dataset': {
             'size': [1]
         },
         'attributes': {
             'nicos_name': 'dev1',
             'units': 'unit',
             'nicos_param': 'value'}
         },
    ('dataset_int', DeviceDataset('dev1', 'parint')):
        {'values': 1,
         'type': 'dataset',
         'name': 'dataset_int',
         'dataset': {
             'size': [1]
         },
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
             'size': [1],
             'string_size': 7,
             'type': 'string'}
         },
    ('event_stream', EventStream(topic='topic', source='source',
                                 broker="localhost:9092", dtype="uint32")):
        {'type': 'stream',
         'stream': {'topic': 'topic', 'source': 'source',
                    'type': 'uint32',
                    'broker': 'localhost:9092',
                    'writer_module': 'ev42'}
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
                    "dataset": {
                        'size': [1]
                    },
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
    def compare_lists(list1, list2):
        """ Compare that all items in list1 exists in list 2
        :param list1:
        :param list2:
        :return:
        """
        if not isinstance(list1, list):
            return False, '%s is not a list' % list1
        if not isinstance(list2, list):
            return False, '%s is not a list' % list2

        if len(list1) != len(list2):
            return False, 'The lengths of the list do not match'

        # Sorting list with dicts is difficult!
        # Brute force: Do nXn comparisons
        for v1 in list1:
            if isinstance(v1, dict):
                found = False
                for v2 in list2:
                    if isinstance(v2, dict) and \
                            TestNexusTemplate.compare_dicts(v1, v2)[0]:
                        found = True
                        break
                if not found:
                    return False, '%s\nNOT FOUND IN\n%s' % (v1, list2)
            elif isinstance(v1, list):
                found = False
                for v2 in list2:
                    if isinstance(v2, list) and \
                            TestNexusTemplate.compare_lists(v1, v2)[0]:
                        found = True
                        break
                if not found:
                    return False, '%s\nNOT FOUND IN\n%s' % (v1, list2)
            elif v1 not in list2:
                return False, '%s NOT FOUND IN %s' % (v1, list2)

        return True, ''

    @staticmethod
    def compare_dicts(dict1, dict2):
        if not isinstance(dict1, dict):
            return False, '%s is not a dict' % dict1

        if not isinstance(dict2, dict):
            return False, '%s is not a dict' % dict2

        # Check for the keys
        if not set(dict1.keys()) == set(dict2.keys()):
            return False, 'Keys do not match in both dict: %s and %s' % \
                   (set(dict1.keys()), set(dict2.keys()))

        # Compare the values
        for val1, val2 in [(dict1[k], dict2[k]) for k in set(dict1.keys())]:
            if isinstance(val1, dict):
                eq, msg = TestNexusTemplate.compare_dicts(val1, val2)
                if not eq:
                    return eq, msg
            elif isinstance(val1, list):
                eq, msg = TestNexusTemplate.compare_lists(val1, val2)
                if not eq:
                    return eq, msg
                eq, msg = TestNexusTemplate.compare_lists(val2, val1)
                if not eq:
                    return eq, msg
            elif val1 != val2:
                return False, '%s != %s' % (val1, val2)

        return True, ''

    #  pylint: disable=dict-keys-not-iterating
    @pytest.mark.parametrize("element", elements.keys())
    def test_element_provides_correct_json(self, element):
        """ Test that elements provide correct JSON structures
        """
        name, elem = element
        eq, msg = self.compare_dicts(elem.structure(name, metainfo)[0],
                                     elements[element])
        assert eq, msg

    def test_template_conversion_to_json(self, session):
        """ Test that template is correctly converted to JSON format
        """
        converter = NexusTemplateConverter()
        eq, msg = self.compare_dicts(converter.convert(template, metainfo),
                                     converted)
        assert eq, msg
