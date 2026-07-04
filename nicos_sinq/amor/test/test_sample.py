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
#   Stefan Mathis <stefan.mathis@psi.ch>
#
# *****************************************************************************

import pytest

pytest.importorskip('yaml')

from nicos_sinq.amor.devices.sample import to_yaml

session_setup = 'system'


class TestAmorSample:

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.sample = session.experiment.sample

    def test_info(self):
        info = self.sample.info()

        # Assert that orsomodel_yaml is only contained once
        occurrences = 0
        for item in info:
            if item.key == 'orsomodel_yaml':
                occurrences += 1
        assert occurrences == 1

        # Assert that geometry_yaml is only contained once
        occurrences = 0
        for item in info:
            if item.key == 'geometry_yaml':
                occurrences += 1
        assert occurrences == 1

    def test_write_orsomodel(self):
        assert self.sample.orsomodel == {'stack': None}
        assert self.sample.orsomodel_yaml == to_yaml(self.sample.orsomodel)

        self.sample.orsomodel = {'stack': {'thickness': 1.0, 'roughness': 0.5}}
        assert self.sample.orsomodel_yaml == to_yaml(self.sample.orsomodel)

    def test_write_geometry(self):
        assert self.sample.geometry == {}
        assert self.sample.geometry_yaml == to_yaml(self.sample.geometry)

        self.sample.geometry = {'shape': 'disc'}
        assert self.sample.geometry_yaml == to_yaml(self.sample.geometry)
