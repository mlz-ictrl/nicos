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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
import re
from collections.abc import MutableMapping

import pytest

pytest.importorskip('lxml')

from nicos_sinq.dmc.nexus.nexus_templates import DMCTemplateProvider

session_setup = 'nexus'


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def strip_nx_class(key):
    return re.sub(':NX([a-zA-Z]*)_', '_', key)


class TestTemplateProvider:
    prefix = 'entry:NXentry_DMC:NXinstrument'

    @pytest.fixture(autouse=True)
    def initialize_device(self, session):
        self.session = session

    def test_camera(self):
        self.session.experiment.detlist = ['andorccd']
        template = flatten(DMCTemplateProvider().getTemplate())

        # Make sure that the detector group is a NXdetector
        assert any('detector:NXdetector' in key for key in template)

        # Make sure that the expected fields are there
        keys = {strip_nx_class(key) for key in template}
        assert ['entry_DMC_detector_data' in keys]
        assert ['entry_DMC_detector_summed_counts' in keys]
        assert ['entry_DMC_detector_timestamp' in keys]

    def test_mesydaq(self):
        self.session.experiment.detlist = ['det']
        template = flatten(DMCTemplateProvider().getTemplate())

        # Make sure that the detector group is a NXdetector
        assert any('detector:NXdetector' in key for key in template)

        # Make sure that the expected fields are there
        keys = {strip_nx_class(key) for key in template}
        assert ['entry_DMC_detector_data' in keys]
        assert ['entry_DMC_detector_summed_counts' in keys]
        assert ['entry_DMC_detector_timestamp' in keys]

    def test_adaptive_optics(self):
        self.session.experiment.detlist = ['andorccd']
        loaded_setups = self.session.loaded_setups
        loaded_setups |= {'adaptive_optics'}
        self.session.loaded_setups = loaded_setups
        template = flatten(DMCTemplateProvider().getTemplate())

        # Make sure that the adaptive_optics group is a NXguide
        assert any('adaptive_optics:NXguide' in key for key in template)

        # Make sure that the elements of the adaptive optics are there
        keys = {
            strip_nx_class(':'.join(key.split(':')[:-1]))
            for key in template
        }
        assert any('adaptive_optics_transformation_linear_stage' in key
                   for key in keys)
        assert any('adaptive_optics_transformation_rotational_stage' in key
                   for key in keys)
        assert any('adaptive_optics_transformation_z_stage' in key
                   for key in keys)
