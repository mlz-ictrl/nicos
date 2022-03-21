# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from collections.abc import MutableMapping

import pytest

pytest.importorskip('lxml')

from nicos.core import Param, tupleof
from nicos.devices.instrument import Instrument

from nicos_sinq.camea.nexus.nexus_templates import CameaCCDTemplateProvider, \
    CameaTemplateProvider

session_setup = 'nexus'


class MockInstrument(Instrument):
    parameters = {
        'orienting_reflections': Param('Reflections from which the UB was '
                                       'calculated',
                                       type=tupleof(int, int), settable=True,
                                       default=(0, 0)),
    }


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def dict_recursive_search(dictionary, where):
    if len(where) == 1:
        return dictionary.get(where[0], None)
    for key, value in dictionary.items():
        if key.startswith(f'{where[0]}:'):
            return dict_recursive_search(value, where[1:])
    return None


@pytest.fixture
def detector_dict():
    return CameaTemplateProvider().getTemplate()


@pytest.fixture
def ccd_dict():
    return CameaCCDTemplateProvider().getTemplate()


@pytest.fixture
def detector_list(detector_dict):
    return flatten(detector_dict)


@pytest.fixture
def ccd_list(ccd_dict):
    return flatten(ccd_dict)


def test_detector_has_calib(session, detector_list):

    prefix = 'entry:NXentry_CAMEA:NXinstrument'
    for index in [1, 3, 8]:
        for parameter in ['a4offset', 'amplitude', 'background', 'boundaries',
                          'final_energy', 'width']:
            key = f'{prefix}_calib{index}:NXcollection_{parameter}'
            assert key in detector_list


def test_detector_fields(session, detector_list):

    prefix = 'entry:NXentry_CAMEA:NXinstrument'
    det = 'detector:NXdetector'

    for element in [f'{prefix}_{det}_detector_selection',
                    f'{prefix}_{det}_data',
                    f'{prefix}_{det}_summed_counts',
                    f'{prefix}_{det}_total_counts',
                    f'{prefix}_segment_1:NXdetector_data',
                    f'{prefix}_segment_8:NXdetector_data']:
        assert element in detector_list


def test_andorccd_fields(session, ccd_list):
    prefix = 'entry:NXentry_CAMEA:NXinstrument'
    det = 'detector:NXdetector'

    assert f'{prefix}_{det}_data' in ccd_list


def test_detector_links(session, detector_dict):
    for key, value in detector_dict.items():
        if key.startswith('entry:NXentry_data'):
            where = value.target.split('/')[1:]
            assert dict_recursive_search(detector_dict, where)


def test_andorccd_links(session, ccd_dict):
    for key, value in ccd_dict.items():
        if key.startswith('entry:NXentry_data'):
            where = value.target.split('/')[1:]
            assert dict_recursive_search(ccd_dict, where)
