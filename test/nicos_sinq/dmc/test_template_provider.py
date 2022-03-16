#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

from nicos_sinq.dmc.nexus.nexus_templates import DMCTemplateProvider

session_setup = "sinq_dmc_nexus"


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class TestTemplateProvider:
    prefix = 'entry:NXentry_DMC:NXinstrument'

    @pytest.fixture(autouse=True)
    def initialize_device(self, session):
        self.session = session

    def test_camera(self):
        self.session.experiment.detlist = ['andorccd']
        det = 'andorccd:NXdetector'
        template = flatten(DMCTemplateProvider().getTemplate())
        assert f'{self.prefix}_{det}_data' in template
        assert f'{self.prefix}_{det}_time_stamp' in template

    def test_mesydaq(self):
        self.session.experiment.detlist = ['detector']
        det = 'detector:NXdetector'
        template = flatten(DMCTemplateProvider().getTemplate())
        assert f'{self.prefix}_{det}_counts' in template
        assert f'{self.prefix}_{det}_detector_position' in template

    def test_adaptive_optics(self):
        self.session.experiment.detlist = ['andorccd']
        loaded_setups = self.session.loaded_setups
        loaded_setups |= {'adaptive_optics'}
        self.session.loaded_setups = loaded_setups
        template = flatten(DMCTemplateProvider().getTemplate())
        assert f'{self.prefix}_adaptive_optics:NXGroup_taz' in template
